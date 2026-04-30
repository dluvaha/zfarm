import requests
import base64
import calendar
from datetime import datetime, timedelta
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.conf import settings
from django.db.models import Sum, Count, Q
from django.utils import timezone
from .models import MpesaTransaction
from .forms import MpesaPaymentForm, TransactionSearchForm


def get_mpesa_access_token():
    """Get M-Pesa Daraja API access token"""
    api_url = f"https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
    try:
        response = requests.get(
            api_url,
            auth=(settings.MPESA_CONSUMER_KEY, settings.MPESA_CONSUMER_SECRET),
            timeout=30
        )
        response.raise_for_status()
        return response.json().get('access_token')
    except Exception:
        return None


def initiate_stk_push(phone_number, amount, description, reference):
    """Initiate M-Pesa STK Push (Sandbox)"""
    access_token = get_mpesa_access_token()
    if not access_token:
        return None, "Could not get M-Pesa access token"

    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    password = base64.b64encode(
        f"{settings.MPESA_BUSINESS_SHORTCODE}{settings.MPESA_PASSKEY}{timestamp}".encode()
    ).decode()

    payload = {
        "BusinessShortCode": settings.MPESA_BUSINESS_SHORTCODE,
        "Password": password,
        "Timestamp": timestamp,
        "TransactionType": "CustomerPayBillOnline",
        "Amount": int(amount),
        "PartyA": phone_number,
        "PartyB": settings.MPESA_BUSINESS_SHORTCODE,
        "PhoneNumber": phone_number,
        "CallBackURL": settings.MPESA_CALLBACK_URL,
        "AccountReference": reference[:12],
        "TransactionDesc": description[:13],
    }

    headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}

    try:
        response = requests.post(
            "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest",
            json=payload,
            headers=headers,
            timeout=30
        )
        result = response.json()
        if result.get('ResponseCode') == '0':
            return result, None
        return None, result.get('errorMessage', 'STK Push failed')
    except Exception as e:
        return None, str(e)


@login_required
def transaction_list(request):
    transactions = MpesaTransaction.objects.filter(farmer=request.user)
    search_form = TransactionSearchForm(request.GET or None)

    if search_form.is_valid():
        start_date = search_form.cleaned_data.get('start_date')
        end_date = search_form.cleaned_data.get('end_date')
        transaction_type = search_form.cleaned_data.get('transaction_type')
        status = search_form.cleaned_data.get('status')
        purpose = search_form.cleaned_data.get('purpose')

        if start_date:
            transactions = transactions.filter(created_at__date__gte=start_date)
        if end_date:
            transactions = transactions.filter(created_at__date__lte=end_date)
        if transaction_type:
            transactions = transactions.filter(transaction_type=transaction_type)
        if status:
            transactions = transactions.filter(status=status)
        if purpose:
            transactions = transactions.filter(purpose=purpose)

    transactions = transactions[:50]

    context = {
        'transactions': transactions,
        'search_form': search_form,
    }
    return render(request, 'payments/transaction_list.html', context)


@login_required
def initiate_payment(request):
    if request.method == 'POST':
        form = MpesaPaymentForm(request.POST)
        if form.is_valid():
            phone = form.cleaned_data['phone_number']
            amount = form.cleaned_data['amount']
            purpose = form.cleaned_data['purpose']
            description = form.cleaned_data['description'] or f"Payment for {purpose}"
            is_expense = form.cleaned_data['is_expense']
            reference_id = form.cleaned_data['reference_id']

            # Create pending transaction
            transaction = MpesaTransaction.objects.create(
                farmer=request.user,
                phone_number=phone,
                amount=amount,
                purpose=purpose,
                description=description,
                is_expense=is_expense,
                reference_id=reference_id,
                transaction_type='stk_push',
                status='pending',
            )

            # Attempt STK Push
            result, error = initiate_stk_push(phone, amount, description, str(transaction.pk))

            if result:
                transaction.checkout_request_id = result.get('CheckoutRequestID', '')
                transaction.merchant_request_id = result.get('MerchantRequestID', '')
                transaction.raw_response = result
                transaction.save()
                messages.info(request, 'M-Pesa STK Push sent! Please check your phone and enter PIN to confirm.')
            else:
                transaction.status = 'failed'
                transaction.result_desc = error
                transaction.save()
                messages.warning(request, f'M-Pesa STK Push failed: {error}. Transaction saved as pending.')

            return redirect('payments:transaction_detail', pk=transaction.pk)
    else:
        form = MpesaPaymentForm()
        form.fields['reference_id'].initial = request.GET.get('ref', '')

    return render(request, 'payments/initiate_payment.html', {'form': form})


@login_required
def transaction_detail(request, pk):
    transaction = get_object_or_404(MpesaTransaction, pk=pk, farmer=request.user)
    return render(request, 'payments/transaction_detail.html', {'transaction': transaction})


def mpesa_callback(request):
    """M-Pesa Daraja API callback endpoint"""
    if request.method == 'POST':
        try:
            data = request.json() if hasattr(request, 'json') else {}
            body = data.get('Body', {}).get('stkCallback', {})
            checkout_id = body.get('CheckoutRequestID', '')
            merchant_id = body.get('MerchantRequestID', '')
            result_code = str(body.get('ResultCode', ''))
            result_desc = body.get('ResultDesc', '')

            metadata = {}
            for item in body.get('CallbackMetadata', {}).get('Item', []):
                metadata[item.get('Name')] = item.get('Value')

            transaction = MpesaTransaction.objects.filter(checkout_request_id=checkout_id).first()
            if transaction:
                transaction.result_code = result_code
                transaction.result_desc = result_desc
                transaction.mpesa_receipt = metadata.get('MpesaReceiptNumber', '')
                transaction.raw_response = data
                transaction.status = 'success' if result_code == '0' else 'failed'
                transaction.save()

            return JsonResponse({"ResultCode": 0, "ResultDesc": "Accepted"})
        except Exception:
            return JsonResponse({"ResultCode": 1, "ResultDesc": "Error processing callback"}, status=400)
    return JsonResponse({"ResultCode": 1, "ResultDesc": "POST required"}, status=405)


@login_required
def finance_summary(request):
    """Finance summary with income vs expenses breakdown"""
    transactions = MpesaTransaction.objects.filter(farmer=request.user, status='success')

    total_income = transactions.filter(is_expense=False).aggregate(total=Sum('amount'))['total'] or 0
    total_expenses = transactions.filter(is_expense=True).aggregate(total=Sum('amount'))['total'] or 0
    net_profit = total_income - total_expenses

    # Expense breakdown by purpose
    expense_breakdown = transactions.filter(is_expense=True).values('purpose').annotate(
        total=Sum('amount'),
        count=Count('id')
    ).order_by('-total')

    # Income breakdown
    income_breakdown = transactions.filter(is_expense=False).values('purpose').annotate(
        total=Sum('amount'),
        count=Count('id')
    ).order_by('-total')

    # Monthly summary (last 6 months)
    monthly_data = []
    for i in range(5, -1, -1):
        today = timezone.now().date()
        month = today.month - i
        year = today.year
        while month <= 0:
            month += 12
            year -= 1
        month_date = datetime(year, month, 1)
        month_txns = transactions.filter(
            created_at__year=month_date.year,
            created_at__month=month_date.month
        )
        month_income = month_txns.filter(is_expense=False).aggregate(t=Sum('amount'))['t'] or 0
        month_expense = month_txns.filter(is_expense=True).aggregate(t=Sum('amount'))['t'] or 0
        monthly_data.append({
            'month': month_date.strftime('%b %Y'),
            'income': month_income,
            'expense': month_expense,
            'net': month_income - month_expense,
        })

    context = {
        'total_income': total_income,
        'total_expenses': total_expenses,
        'net_profit': net_profit,
        'expense_breakdown': expense_breakdown,
        'income_breakdown': income_breakdown,
        'monthly_data': monthly_data,
        'total_transactions': transactions.count(),
    }
    return render(request, 'payments/finance_summary.html', context)

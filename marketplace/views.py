from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, F
from .models import MarketplaceListing, BuyerInquiry
from .forms import ListingForm, BuyerInquiryForm
from accounts.models import Farm
from animals.models import Animal


def listing_list(request):
    """Public marketplace - shows all active listings"""
    listings = MarketplaceListing.objects.filter(status='active').select_related('seller', 'farm', 'animal', 'animal__category', 'animal__breed')

    category_filter = request.GET.get('category', '')
    county_filter = request.GET.get('county', '')
    search = request.GET.get('search', '')
    min_price = request.GET.get('min_price', '')
    max_price = request.GET.get('max_price', '')

    if category_filter:
        listings = listings.filter(category=category_filter)
    if county_filter:
        listings = listings.filter(county__icontains=county_filter)
    if search:
        listings = listings.filter(title__icontains=search) | listings.filter(description__icontains=search)
    if min_price:
        try:
            listings = listings.filter(price__gte=float(min_price))
        except ValueError:
            pass
    if max_price:
        try:
            listings = listings.filter(price__lte=float(max_price))
        except ValueError:
            pass

    listings = listings[:60]

    context = {
        'listings': listings,
        'category_filter': category_filter,
        'county_filter': county_filter,
        'search': search,
    }
    return render(request, 'marketplace/listing_list.html', context)


@login_required
def listing_detail(request, pk):
    listing = get_object_or_404(MarketplaceListing, pk=pk)
    # Increment view count
    MarketplaceListing.objects.filter(pk=pk).update(views_count=F('views_count') + 1)
    listing.refresh_from_db()

    inquiries = listing.inquiries.filter(buyer=request.user) if request.user == listing.seller else None
    can_inquire = request.user != listing.seller

    context = {
        'listing': listing,
        'inquiries': inquiries,
        'can_inquire': can_inquire,
        'inquiry_form': BuyerInquiryForm(),
    }
    return render(request, 'marketplace/listing_detail.html', context)


@login_required
def listing_create(request):
    farms = Farm.objects.filter(owner=request.user)
    if not farms.exists():
        messages.warning(request, 'Please create a farm first.')
        return redirect('accounts:farm_create')

    if request.method == 'POST':
        form = ListingForm(request.POST, request.FILES, farm=farms.first(), seller=request.user)
        if form.is_valid():
            listing = form.save()
            messages.success(request, f'Listing "{listing.title}" created!')
            return redirect('marketplace:listing_detail', pk=listing.pk)
    else:
        form = ListingForm()

    # Get animals available for listing (active, belong to this farmer)
    animals = Animal.objects.filter(farm__owner=request.user, status='active')

    context = {
        'form': form,
        'farms': farms,
        'animals': animals,
    }
    return render(request, 'marketplace/listing_form.html', context)


@login_required
def listing_edit(request, pk):
    listing = get_object_or_404(MarketplaceListing, pk=pk, seller=request.user)
    if listing.status not in ['active', 'cancelled']:
        messages.error(request, 'Cannot edit this listing.')
        return redirect('marketplace:listing_detail', pk=pk)

    if request.method == 'POST':
        form = ListingForm(request.POST, request.FILES, instance=listing)
        if form.is_valid():
            form.save()
            messages.success(request, 'Listing updated!')
            return redirect('marketplace:listing_detail', pk=pk)
    else:
        form = ListingForm(instance=listing)

    return render(request, 'marketplace/listing_form.html', {'form': form, 'listing': listing, 'edit': True})


@login_required
def create_inquiry(request, pk):
    listing = get_object_or_404(MarketplaceListing, pk=pk, status='active')
    if request.user == listing.seller:
        messages.error(request, 'Cannot inquire on your own listing.')
        return redirect('marketplace:listing_detail', pk=pk)

    if request.method == 'POST':
        form = BuyerInquiryForm(request.POST)
        if form.is_valid():
            inquiry = form.save(commit=False)
            inquiry.listing = listing
            inquiry.buyer = request.user
            inquiry.save()

            # Create notification for seller
            from notifications_app.models import Notification
            Notification.create_notification(
                farmer=listing.seller,
                title=f'New inquiry on "{listing.title}"',
                message=f'{request.user.get_full_name() or request.user.username} is interested in your listing: {inquiry.message[:100]}',
                notification_type='marketplace',
                related_id=str(listing.pk),
                related_model='MarketplaceListing',
                action_url=f'/marketplace/{listing.pk}/',
            )

            messages.success(request, 'Inquiry sent successfully!')
            return redirect('marketplace:listing_detail', pk=pk)
    return redirect('marketplace:listing_detail', pk=pk)


@login_required
def respond_inquiry(request, pk, ik):
    listing = get_object_or_404(MarketplaceListing, pk=pk, seller=request.user)
    inquiry = get_object_or_404(BuyerInquiry, pk=ik, listing=listing)

    if request.method == 'POST':
        response = request.POST.get('response', '')
        action = request.POST.get('action', 'respond')

        inquiry.seller_response = response
        if action == 'accept':
            inquiry.status = 'accepted'
        elif action == 'reject':
            inquiry.status = 'rejected'
        else:
            inquiry.status = 'responded'
        inquiry.save()

        # Notify buyer
        from notifications_app.models import Notification
        Notification.create_notification(
            farmer=inquiry.buyer,
            title=f'Response to your inquiry on "{listing.title}"',
            message=response[:200],
            notification_type='marketplace',
            related_id=str(listing.pk),
            related_model='MarketplaceListing',
            action_url=f'/marketplace/{listing.pk}/',
        )

        messages.success(request, 'Response sent!')
    return redirect('marketplace:my_listings')


@login_required
def my_listings(request):
    listings = MarketplaceListing.objects.filter(seller=request.user).annotate(
        inquiry_count=Count('inquiries')
    ).order_by('-created_at')

    context = {'listings': listings}
    return render(request, 'marketplace/my_listings.html', context)


@login_required
def my_inquiries(request):
    inquiries = BuyerInquiry.objects.filter(buyer=request.user).select_related('listing', 'listing__seller').order_by('-created_at')

    context = {'inquiries': inquiries}
    return render(request, 'marketplace/my_inquiries.html', context)

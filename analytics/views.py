from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count, Avg, Q, DecimalField
from django.db.models.functions import Coalesce
from django.utils import timezone
from datetime import timedelta
from accounts.models import Farm
from animals.models import Animal, HealthRecord, ProductionRecord, AnimalMovement
from payments.models import MpesaTransaction
from marketplace.models import MarketplaceListing
from notifications_app.models import Notification, FeedingSchedule


@login_required
def dashboard(request):
    """Main farm dashboard with analytics overview"""
    farmer = request.user
    farms = Farm.objects.filter(owner=farmer)

    # Farm summary
    total_animals = Animal.objects.filter(farm__owner=farmer).count()
    active_animals = Animal.objects.filter(farm__owner=farmer, status='active').count()
    sick_animals = Animal.objects.filter(farm__owner=farmer, status='sick').count()

    # Animal categories breakdown
    category_breakdown = Animal.objects.filter(farm__owner=farmer, status='active').values(
        'category__name', 'category__icon'
    ).annotate(count=Count('id')).order_by('-count')

    # Recent transactions
    recent_transactions = MpesaTransaction.objects.filter(farmer=farmer).order_by('-created_at')[:5]

    # Financial summary
    this_month = timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    month_income = MpesaTransaction.objects.filter(
        farmer=farmer, status='success', is_expense=False, created_at__gte=this_month
    ).aggregate(total=Coalesce(Sum('amount'), 0))['total']
    month_expenses = MpesaTransaction.objects.filter(
        farmer=farmer, status='success', is_expense=True, created_at__gte=this_month
    ).aggregate(total=Coalesce(Sum('amount'), 0))['total']

    # Health alerts - overdue vaccinations
    overdue_records = HealthRecord.objects.filter(
        animal__farm__owner=farmer,
        next_due_date__lte=timezone.now().date(),
        next_due_date__isnull=False
    ).select_related('animal').order_by('next_due_date')[:10]

    # Recent health records
    recent_health = HealthRecord.objects.filter(
        animal__farm__owner=farmer
    ).select_related('animal').order_by('-date')[:5]

    # Marketplace stats
    active_listings = MarketplaceListing.objects.filter(seller=farmer, status='active').count()
    pending_inquiries = MarketplaceListing.objects.filter(
        seller=farmer, inquiries__status='pending'
    ).distinct().count()

    # Production today
    today = timezone.now().date()
    today_milk = ProductionRecord.objects.filter(
        animal__farm__owner=farmer, record_type='milk', date=today
    ).aggregate(total=Coalesce(Sum('quantity'), 0))['total']
    today_eggs = ProductionRecord.objects.filter(
        animal__farm__owner=farmer, record_type='eggs', date=today
    ).aggregate(total=Coalesce(Sum('quantity'), 0))['total']

    # Mortality tracking
    thirty_days_ago = today - timedelta(days=30)
    deaths_30d = AnimalMovement.objects.filter(
        animal__farm__owner=farmer, movement_type='died', date__gte=thirty_days_ago
    ).count()

    # Upcoming feeding schedules
    feeding_schedules = FeedingSchedule.objects.filter(
        farm__owner=farmer, is_active=True
    ).select_related('animal')[:5]

    # Unread notifications
    unread_notifications = Notification.objects.filter(farmer=farmer, is_read=False).count()

    context = {
        'farms': farms,
        'total_animals': total_animals,
        'active_animals': active_animals,
        'sick_animals': sick_animals,
        'category_breakdown': category_breakdown,
        'recent_transactions': recent_transactions,
        'month_income': month_income,
        'month_expenses': month_expenses,
        'month_net': month_income - month_expenses,
        'overdue_records': overdue_records,
        'recent_health': recent_health,
        'active_listings': active_listings,
        'pending_inquiries': pending_inquiries,
        'today_milk': today_milk,
        'today_eggs': today_eggs,
        'deaths_30d': deaths_30d,
        'feeding_schedules': feeding_schedules,
        'unread_notifications': unread_notifications,
    }
    return render(request, 'analytics/dashboard.html', context)


@login_required
def animal_report(request, pk):
    """Detailed report for a single animal"""
    animal = get_object_or_404(Animal, pk=pk, farm__owner=request.user)

    # Health history
    health_records = animal.health_records.all().order_by('-date')

    # Production history
    production_records = animal.production_records.all().order_by('-date')

    # Calculate production totals
    milk_total = production_records.filter(record_type='milk').aggregate(t=Coalesce(Sum('quantity'), 0))['t']
    eggs_total = production_records.filter(record_type='eggs').aggregate(t=Coalesce(Sum('quantity'), 0))['t']
    latest_weight = production_records.filter(record_type='weight').first()

    # Cost tracking
    health_costs = health_records.aggregate(t=Coalesce(Sum('cost'), 0))['t']

    # Movements
    movements = animal.movements.all().order_by('-date')

    context = {
        'animal': animal,
        'health_records': health_records,
        'production_records': production_records,
        'milk_total': milk_total,
        'eggs_total': eggs_total,
        'latest_weight': latest_weight,
        'health_costs': health_costs,
        'movements': movements,
    }
    return render(request, 'analytics/animal_report.html', context)


@login_required
def farm_report(request, pk):
    """Comprehensive farm report"""
    farm = get_object_or_404(Farm, pk=pk, owner=request.user)

    # Animal statistics
    animals = Animal.objects.filter(farm=farm)
    total = animals.count()
    by_status = animals.values('status').annotate(count=Count('id'))
    by_category = animals.values('category__name').annotate(count=Count('id')).order_by('-count')
    by_gender = animals.values('gender').annotate(count=Count('id'))

    # Health overview
    health_records = HealthRecord.objects.filter(animal__farm=farm)
    total_health_records = health_records.count()
    total_health_cost = health_records.aggregate(t=Coalesce(Sum('cost'), 0))['t']
    overdue = health_records.filter(
        next_due_date__lte=timezone.now().date(), next_due_date__isnull=False
    ).select_related('animal')

    # Production totals
    production = ProductionRecord.objects.filter(animal__farm=farm)
    milk_total = production.filter(record_type='milk').aggregate(t=Coalesce(Sum('quantity'), 0))['t']
    eggs_total = production.filter(record_type='eggs').aggregate(t=Coalesce(Sum('quantity'), 0))['t']

    # Financial - related to this farm
    transactions = MpesaTransaction.objects.filter(farmer=request.user, status='success')
    total_income = transactions.filter(is_expense=False).aggregate(t=Coalesce(Sum('amount'), 0))['t']
    total_expenses = transactions.filter(is_expense=True).aggregate(t=Coalesce(Sum('amount'), 0))['t']

    # Mortality
    deaths = AnimalMovement.objects.filter(animal__farm=farm, movement_type='died').order_by('-date')[:10]
    death_count = deaths.count()

    context = {
        'farm': farm,
        'total': total,
        'by_status': by_status,
        'by_category': by_category,
        'by_gender': by_gender,
        'total_health_records': total_health_records,
        'total_health_cost': total_health_cost,
        'overdue': overdue,
        'milk_total': milk_total,
        'eggs_total': eggs_total,
        'total_income': total_income,
        'total_expenses': total_expenses,
        'deaths': deaths,
        'death_count': death_count,
    }
    return render(request, 'analytics/farm_report.html', context)

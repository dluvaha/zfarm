from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .models import Notification, FeedingSchedule
from .forms import FeedingScheduleForm
from accounts.models import Farm
from animals.models import Animal


@login_required
def notification_list(request):
    notifications = request.user.notifications.all()[:30]
    unread_count = request.user.notifications.filter(is_read=False).count()

    context = {
        'notifications': notifications,
        'unread_count': unread_count,
    }
    return render(request, 'notifications/notification_list.html', context)


@login_required
def mark_read(request, pk):
    notification = get_object_or_404(Notification, pk=pk, farmer=request.user)
    notification.is_read = True
    notification.save()
    if notification.action_url:
        return redirect(notification.action_url)
    return redirect('notifications:notification_list')


@login_required
def mark_all_read(request):
    if request.method == 'POST':
        request.user.notifications.filter(is_read=False).update(is_read=True)
        messages.success(request, 'All notifications marked as read.')
    return redirect('notifications:notification_list')


@login_required
def feeding_schedule_list(request):
    farms = Farm.objects.filter(owner=request.user)
    schedules = FeedingSchedule.objects.filter(farm__owner=request.user, is_active=True).select_related('farm', 'animal')
    context = {
        'schedules': schedules,
        'farms': farms,
    }
    return render(request, 'notifications/schedule_list.html', context)


@login_required
def feeding_schedule_create(request):
    farms = Farm.objects.filter(owner=request.user)
    if not farms.exists():
        messages.warning(request, 'Please create a farm first.')
        return redirect('accounts:farm_create')

    if request.method == 'POST':
        form = FeedingScheduleForm(request.POST)
        farm_id = request.POST.get('farm')
        farm = get_object_or_404(Farm, pk=farm_id, owner=request.user)
        if form.is_valid():
            schedule = form.save(commit=False)
            schedule.farm = farm
            schedule.save()
            messages.success(request, 'Feeding schedule created!')
            return redirect('notifications:schedule_list')
    else:
        form = FeedingScheduleForm()

    context = {
        'form': form,
        'farms': farms,
    }
    return render(request, 'notifications/schedule_form.html', context)


@login_required
def feeding_schedule_delete(request, pk):
    schedule = get_object_or_404(FeedingSchedule, pk=pk, farm__owner=request.user)
    if request.method == 'POST':
        schedule.delete()
        messages.success(request, 'Feeding schedule deleted.')
        return redirect('notifications:schedule_list')
    return render(request, 'notifications/schedule_confirm_delete.html', {'schedule': schedule})

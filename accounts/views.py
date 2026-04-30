from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import Farmer, Farm, OTPVerification
from .forms import FarmerRegistrationForm, FarmerLoginForm, FarmerProfileForm, FarmForm


def register(request):
    if request.user.is_authenticated:
        return redirect('analytics:dashboard')
    if request.method == 'POST':
        form = FarmerRegistrationForm(request.POST)
        if form.is_valid():
            farmer = form.save(commit=False)
            farmer.is_verified = False
            farmer.save()
            messages.success(request, 'Account created successfully! Please log in.')
            return redirect('accounts:login')
    else:
        form = FarmerRegistrationForm()
    return render(request, 'accounts/register.html', {'form': form})


def farmer_login(request):
    if request.user.is_authenticated:
        return redirect('analytics:dashboard')
    if request.method == 'POST':
        form = FarmerLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'Welcome back, {user.first_name or user.username}!')
            next_url = request.GET.get('next')
            if next_url:
                return redirect(next_url)
            return redirect('analytics:dashboard')
    else:
        form = FarmerLoginForm()
    return render(request, 'accounts/login.html', {'form': form})


def farmer_logout(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('accounts:login')


@login_required
def profile_view(request):
    farmer = request.user
    info_pairs = [
        ('Phone Number', farmer.phone_number or 'Not set'),
        ('M-Pesa Number', farmer.mpesa_number or 'Not set'),
        ('Location', farmer.location or 'Not set'),
        ('County', farmer.county or 'Not set'),
        ('Farm Name', farmer.farm_name or 'Not set'),
        ('Farm Type', farmer.farm_type or 'Not set'),
        ('ID Number', farmer.id_number or 'Not set'),
        ('Member Since', farmer.created_at.strftime('%b %d, %Y')),
    ]
    return render(request, 'accounts/profile.html', {'farmer': farmer, 'info_pairs': info_pairs})


@login_required
def profile_edit(request):
    if request.method == 'POST':
        form = FarmerProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('accounts:profile')
    else:
        form = FarmerProfileForm(instance=request.user)
    return render(request, 'accounts/profile_edit.html', {'form': form})


@login_required
def farm_list(request):
    farms = Farm.objects.filter(owner=request.user)
    return render(request, 'accounts/farm_list.html', {'farms': farms})


@login_required
def farm_create(request):
    if request.method == 'POST':
        form = FarmForm(request.POST)
        if form.is_valid():
            farm = form.save(commit=False)
            farm.owner = request.user
            farm.save()
            messages.success(request, f'Farm "{farm.name}" created successfully!')
            return redirect('accounts:farm_detail', pk=farm.pk)
    else:
        form = FarmForm()
    return render(request, 'accounts/farm_form.html', {'form': form, 'title': 'Create New Farm'})


@login_required
def farm_detail(request, pk):
    farm = get_object_or_404(Farm, pk=pk, owner=request.user)
    animals = farm.animals.all()[:10]
    return render(request, 'accounts/farm_detail.html', {'farm': farm, 'animals': animals})


@login_required
def farm_edit(request, pk):
    farm = get_object_or_404(Farm, pk=pk, owner=request.user)
    if request.method == 'POST':
        form = FarmForm(request.POST, instance=farm)
        if form.is_valid():
            form.save()
            messages.success(request, 'Farm updated successfully!')
            return redirect('accounts:farm_detail', pk=farm.pk)
    else:
        form = FarmForm(instance=farm)
    return render(request, 'accounts/farm_form.html', {'form': form, 'title': 'Edit Farm', 'farm': farm})


@login_required
def farm_delete(request, pk):
    farm = get_object_or_404(Farm, pk=pk, owner=request.user)
    if request.method == 'POST':
        farm_name = farm.name
        farm.delete()
        messages.success(request, f'Farm "{farm_name}" deleted successfully.')
        return redirect('accounts:farm_list')
    return render(request, 'accounts/farm_confirm_delete.html', {'farm': farm})

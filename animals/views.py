from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Count
from .models import Animal, AnimalCategory, Breed, HealthRecord, ProductionRecord, AnimalMovement
from .forms import AnimalForm, HealthRecordForm, ProductionRecordForm, AnimalMovementForm
from accounts.models import Farm


@login_required
def animal_list(request):
    farms = Farm.objects.filter(owner=request.user)
    animals = Animal.objects.filter(farm__owner=request.user).select_related('category', 'breed', 'farm')
    categories = AnimalCategory.objects.all()

    category_filter = request.GET.get('category', '')
    status_filter = request.GET.get('status', '')
    farm_filter = request.GET.get('farm', '')
    search = request.GET.get('search', '')

    if category_filter:
        animals = animals.filter(category_id=category_filter)
    if status_filter:
        animals = animals.filter(status=status_filter)
    if farm_filter:
        animals = animals.filter(farm_id=farm_filter)
    if search:
        animals = animals.filter(tag_id__icontains=search) | animals.filter(name__icontains=search)

    context = {
        'animals': animals,
        'categories': categories,
        'farms': farms,
        'category_filter': category_filter,
        'status_filter': status_filter,
        'farm_filter': farm_filter,
        'search': search,
    }
    return render(request, 'animals/animal_list.html', context)


@login_required
def animal_create(request):
    farms = Farm.objects.filter(owner=request.user)
    if not farms.exists():
        messages.warning(request, 'Please create a farm first before adding animals.')
        return redirect('accounts:farm_create')

    if request.method == 'POST':
        form = AnimalForm(request.POST, request.FILES)
        farm_id = request.POST.get('farm')
        farm = get_object_or_404(Farm, pk=farm_id, owner=request.user)
        if form.is_valid():
            animal = form.save(commit=False)
            animal.farm = farm
            animal.save()
            messages.success(request, f'Animal {animal.tag_id} added successfully!')
            return redirect('animals:animal_detail', pk=animal.pk)
    else:
        form = AnimalForm()

    context = {
        'form': form,
        'farms': farms,
        'categories': AnimalCategory.objects.all(),
    }
    return render(request, 'animals/animal_form.html', context)


@login_required
def animal_detail(request, pk):
    animal = get_object_or_404(Animal, pk=pk, farm__owner=request.user)
    health_records = animal.health_records.all()[:20]
    production_records = animal.production_records.all()[:20]
    movements = animal.movements.all()[:20]

    context = {
        'animal': animal,
        'health_records': health_records,
        'production_records': production_records,
        'movements': movements,
        'health_form': HealthRecordForm(),
        'production_form': ProductionRecordForm(),
        'movement_form': AnimalMovementForm(),
    }
    return render(request, 'animals/animal_detail.html', context)


@login_required
def animal_edit(request, pk):
    animal = get_object_or_404(Animal, pk=pk, farm__owner=request.user)
    if request.method == 'POST':
        form = AnimalForm(request.POST, request.FILES, instance=animal)
        if form.is_valid():
            form.save()
            messages.success(request, f'Animal {animal.tag_id} updated successfully!')
            return redirect('animals:animal_detail', pk=animal.pk)
    else:
        form = AnimalForm(instance=animal)
    return render(request, 'animals/animal_form.html', {'form': form, 'animal': animal, 'edit': True})


@login_required
def animal_delete(request, pk):
    animal = get_object_or_404(Animal, pk=pk, farm__owner=request.user)
    if request.method == 'POST':
        tag = animal.tag_id
        animal.delete()
        messages.success(request, f'Animal {tag} deleted.')
        return redirect('animals:animal_list')
    return render(request, 'animals/animal_confirm_delete.html', {'animal': animal})


@login_required
def health_record_create(request, pk):
    animal = get_object_or_404(Animal, pk=pk, farm__owner=request.user)
    if request.method == 'POST':
        form = HealthRecordForm(request.POST)
        if form.is_valid():
            record = form.save(commit=False)
            record.animal = animal
            record.save()
            messages.success(request, 'Health record added successfully!')
            return redirect('animals:animal_detail', pk=pk)
    return redirect('animals:animal_detail', pk=pk)


@login_required
def health_record_edit(request, pk, hk):
    animal = get_object_or_404(Animal, pk=pk, farm__owner=request.user)
    record = get_object_or_404(HealthRecord, pk=hk, animal=animal)
    if request.method == 'POST':
        form = HealthRecordForm(request.POST, instance=record)
        if form.is_valid():
            form.save()
            messages.success(request, 'Health record updated!')
            return redirect('animals:animal_detail', pk=pk)
    return redirect('animals:animal_detail', pk=pk)


@login_required
def health_record_delete(request, pk, hk):
    animal = get_object_or_404(Animal, pk=pk, farm__owner=request.user)
    record = get_object_or_404(HealthRecord, pk=hk, animal=animal)
    if request.method == 'POST':
        record.delete()
        messages.success(request, 'Health record deleted.')
    return redirect('animals:animal_detail', pk=pk)


@login_required
def production_create(request, pk):
    animal = get_object_or_404(Animal, pk=pk, farm__owner=request.user)
    if request.method == 'POST':
        form = ProductionRecordForm(request.POST)
        if form.is_valid():
            record = form.save(commit=False)
            record.animal = animal
            record.save()
            messages.success(request, 'Production record added!')
            return redirect('animals:animal_detail', pk=pk)
    return redirect('animals:animal_detail', pk=pk)


@login_required
def production_delete(request, pk, rk):
    animal = get_object_or_404(Animal, pk=pk, farm__owner=request.user)
    record = get_object_or_404(ProductionRecord, pk=rk, animal=animal)
    if request.method == 'POST':
        record.delete()
        messages.success(request, 'Production record deleted.')
    return redirect('animals:animal_detail', pk=pk)


@login_required
def movement_create(request, pk):
    animal = get_object_or_404(Animal, pk=pk, farm__owner=request.user)
    if request.method == 'POST':
        form = AnimalMovementForm(request.POST)
        if form.is_valid():
            movement = form.save(commit=False)
            movement.animal = animal
            movement.save()
            if movement.movement_type == 'sold':
                animal.status = 'sold'
                animal.save()
            elif movement.movement_type == 'died':
                animal.status = 'died'
                animal.save()
            elif movement.movement_type == 'transferred_out':
                animal.status = 'transferred'
                animal.save()
            messages.success(request, f'Animal movement recorded: {movement.movement_type}')
            return redirect('animals:animal_detail', pk=pk)
    return redirect('animals:animal_detail', pk=pk)


@login_required
def get_breeds(request, cat_id):
    breeds = Breed.objects.filter(category_id=cat_id).values('id', 'name')
    return JsonResponse(list(breeds), safe=False)

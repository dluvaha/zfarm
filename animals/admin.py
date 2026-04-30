from django.contrib import admin
from .models import AnimalCategory, Breed, Animal, HealthRecord, ProductionRecord, AnimalMovement


@admin.register(AnimalCategory)
class AnimalCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'icon']
    prepopulated_fields = {}


@admin.register(Breed)
class BreedAdmin(admin.ModelAdmin):
    list_display = ['name', 'category']
    list_filter = ['category']


@admin.register(Animal)
class AnimalAdmin(admin.ModelAdmin):
    list_display = ['tag_id', 'name', 'farm', 'category', 'breed', 'gender', 'status', 'weight', 'date_of_birth']
    list_filter = ['status', 'gender', 'category', 'farm']
    search_fields = ['tag_id', 'name']


@admin.register(HealthRecord)
class HealthRecordAdmin(admin.ModelAdmin):
    list_display = ['animal', 'record_type', 'date', 'vet_name', 'cost']
    list_filter = ['record_type', 'date']


@admin.register(ProductionRecord)
class ProductionRecordAdmin(admin.ModelAdmin):
    list_display = ['animal', 'record_type', 'date', 'quantity']


@admin.register(AnimalMovement)
class AnimalMovementAdmin(admin.ModelAdmin):
    list_display = ['animal', 'movement_type', 'date', 'price']
    list_filter = ['movement_type']

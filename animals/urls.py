from django.urls import path
from . import views

app_name = 'animals'

urlpatterns = [
    # Animal CRUD
    path('', views.animal_list, name='animal_list'),
    path('create/', views.animal_create, name='animal_create'),
    path('<uuid:pk>/', views.animal_detail, name='animal_detail'),
    path('<uuid:pk>/edit/', views.animal_edit, name='animal_edit'),
    path('<uuid:pk>/delete/', views.animal_delete, name='animal_delete'),

    # Health Records
    path('<uuid:pk>/health/', views.health_record_create, name='health_create'),
    path('<uuid:pk>/health/<uuid:hk>/', views.health_record_edit, name='health_edit'),
    path('<uuid:pk>/health/<uuid:hk>/delete/', views.health_record_delete, name='health_delete'),

    # Production Records
    path('<uuid:pk>/production/', views.production_create, name='production_create'),
    path('<uuid:pk>/production/<uuid:rk>/delete/', views.production_delete, name='production_delete'),

    # Animal Movements
    path('<uuid:pk>/movement/', views.movement_create, name='movement_create'),

    # AJAX breed filter
    path('breeds/<uuid:cat_id>/', views.get_breeds, name='get_breeds'),
]

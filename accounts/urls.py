from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.farmer_login, name='login'),
    path('logout/', views.farmer_logout, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.profile_edit, name='profile_edit'),
    path('farms/', views.farm_list, name='farm_list'),
    path('farms/create/', views.farm_create, name='farm_create'),
    path('farms/<uuid:pk>/', views.farm_detail, name='farm_detail'),
    path('farms/<uuid:pk>/edit/', views.farm_edit, name='farm_edit'),
    path('farms/<uuid:pk>/delete/', views.farm_delete, name='farm_delete'),
]

from django.urls import path
from . import views

app_name = 'analytics'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('animal-report/<uuid:pk>/', views.animal_report, name='animal_report'),
    path('farm-report/<uuid:pk>/', views.farm_report, name='farm_report'),
]

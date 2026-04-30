from django.urls import path
from . import views

app_name = 'notifications'

urlpatterns = [
    path('', views.notification_list, name='notification_list'),
    path('<uuid:pk>/read/', views.mark_read, name='mark_read'),
    path('read-all/', views.mark_all_read, name='mark_all_read'),
    path('schedules/', views.feeding_schedule_list, name='schedule_list'),
    path('schedules/create/', views.feeding_schedule_create, name='schedule_create'),
    path('schedules/<uuid:pk>/delete/', views.feeding_schedule_delete, name='schedule_delete'),
]

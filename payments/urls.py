from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    path('', views.transaction_list, name='transaction_list'),
    path('pay/', views.initiate_payment, name='initiate_payment'),
    path('callback/', views.mpesa_callback, name='mpesa_callback'),
    path('<uuid:pk>/', views.transaction_detail, name='transaction_detail'),
    path('summary/', views.finance_summary, name='finance_summary'),
]

from django.urls import path
from . import views

app_name = 'marketplace'

urlpatterns = [
    path('', views.listing_list, name='listing_list'),
    path('create/', views.listing_create, name='listing_create'),
    path('<uuid:pk>/', views.listing_detail, name='listing_detail'),
    path('<uuid:pk>/edit/', views.listing_edit, name='listing_edit'),
    path('<uuid:pk>/inquire/', views.create_inquiry, name='create_inquiry'),
    path('<uuid:pk>/inquiry/<uuid:ik>/respond/', views.respond_inquiry, name='respond_inquiry'),
    path('my-listings/', views.my_listings, name='my_listings'),
    path('my-inquiries/', views.my_inquiries, name='my_inquiries'),
]

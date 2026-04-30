from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from analytics.views import dashboard as landing_dashboard

urlpatterns = [
    path('admin/', admin.site.urls),
    path('admin/', admin.site.urls),
    path('', landing_dashboard, name='home'),
    path('dashboard/', landing_dashboard, name='dashboard'),

    # App URLs
    path('accounts/', include('accounts.urls')),
    path('animals/', include('animals.urls')),
    path('payments/', include('payments.urls')),
    path('marketplace/', include('marketplace.urls')),
    path('notifications/', include('notifications_app.urls')),
    path('analytics/', include('analytics.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('', include('hub_service.urls')),
    path('accounts/', include('django.contrib.auth.urls'))
]

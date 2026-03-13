
from django.contrib import admin
from django.urls import include, path
from licorera.views import home

urlpatterns = [
    path('', home, name='home'),
     path('', include('reportes.urls')),
]

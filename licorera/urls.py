
from django.contrib import admin
from django.urls import path
from reportes import views

urlpatterns = [
    path('', views.home, name='home'),
    path('reportes/', views.reportes, name='reportes'),
]
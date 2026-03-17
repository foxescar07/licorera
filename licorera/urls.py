
from django.urls import path
from reportes import views

urlpatterns = [
    path('', views.reporte, name='home'),
]
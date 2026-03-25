from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.login_proyecto, name='login_url'),
    path('principal/', views.principal_view, name='home_principal'),
]
from django.urls import path
from . import views

app_name = 'inventario'

urlpatterns = [
    path('', views.inventario_home, name='inventario_home'),
    path('agenda/<int:pk>/estado/', views.agenda_cambiar_estado, name='agenda_estado'),
    path('conteo/guardar/', views.guardar_conteo, name='guardar_conteo'),
    path('conteo/', views.conteo_inventario, name='conteo_inventario'),
    path('ajustar/<int:pk>/', views.ajustar_inventario, name='ajustar_inventario'),
]
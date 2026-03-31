from django.urls import path
from . import views

app_name = 'inventario'

urlpatterns = [
    path('', views.inventario_home, name='inventario_home'),
    path('conteo/', views.conteo_inventario, name='conteo_inventario'),
    path('comparar/', views.comparar_inventario, name='comparar_inventario'),
    path('agenda/<int:pk>/estado/', views.agenda_cambiar_estado, name='agenda_estado'),
    path('conteo/guardar/', views.guardar_conteo, name='guardar_conteo'),
]
from django.urls import path
from . import views

urlpatterns = [
    path('',                          views.lista_usuarios,         name='usuario'),
    path('login/',                    views.login_view,             name='login'),
    path('logout/',                   views.logout_view,            name='logout'),
    path('crear/',                    views.crear_usuario,          name='crear_usuario'),
    path('recuperar/',                views.solicitar_recuperacion, name='recuperar_clave'),
    path('restablecer/<str:token>/',  views.restablecer_clave,      name='restablecer_clave'),
    path('perfil/',                   views.perfil_datos,           name='perfil_datos'),
    path('perfil/editar/',            views.perfil_editar,          name='perfil_editar'),
]
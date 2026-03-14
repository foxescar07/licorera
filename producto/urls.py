from django.urls import path
from . import views

# Namespace de la app (usar en templates como {% url 'producto:...' %})
app_name = "producto"

urlpatterns = [
    # ── Lista principal + modal de registro (POST) ──────────────────
    path(
        "",
        views.producto_lista,
        name="producto_lista"
    ),

    # ── Detalle de un producto ───────────────────────────────────────
    path(
        "producto/<int:pk>/",
        views.producto_detalle,
        name="producto_detalle"
    ),

    # ── Editar un producto ───────────────────────────────────────────
    path(
        "producto/<int:pk>/editar/",
        views.producto_editar,
        name="producto_editar"
    ),
]


# ────────────────────────────────────────────────────────────────────
#  En tu archivo raíz urls.py (proyecto/urls.py) agrega esto:
# ────────────────────────────────────────────────────────────────────
#
#   from django.contrib import admin
#   from django.urls import path, include
#
#   urlpatterns = [
#       path("admin/", admin.site.urls),
#       path("producto/", include("producto.urls", namespace="producto")),
#   ]
#
# ────────────────────────────────────────────────────────────────────
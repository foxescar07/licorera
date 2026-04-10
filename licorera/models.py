from django.db import models

# Create your models here.
from django.db.models import Sum, Count
from django.shortcuts import render
from producto.models import Producto, Categoria, Inventario
from reportes.models import Venta  # si usas ventas

def home(request):

    # 🔹 RESUMEN POR CATEGORÍA
    categorias = Categoria.objects.all()

    resumen_categorias = []
    for cat in categorias:
        total = Producto.objects.filter(categoria=cat).aggregate(
            total_stock=Sum("cantidad_disponible")
        )["total_stock"] or 0

        resumen_categorias.append({
            "nombre": cat.nombre,
            "total": total
        })

    # 🔹 STOCK CRÍTICO
    stock_critico = Producto.objects.filter(cantidad_disponible__lte=5).count()

    # 🔹 TOTAL PRODUCTOS
    total_productos = Producto.objects.count()

    # 🔹 MOVIMIENTOS RECIENTES
    movimientos = Inventario.objects.select_related("producto").all()[:5]

    # 🔹 VENTAS (para gráfica)
    ventas = Venta.objects.all()  # luego mejoramos esto

    context = {
        "resumen_categorias": resumen_categorias,
        "total_productos": total_productos,
        "stock_critico": stock_critico,
        "movimientos": movimientos,
        "ventas": ventas
    }

    return render(request, "home.html", context)

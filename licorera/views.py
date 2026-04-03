from django.shortcuts import render
from django.http import JsonResponse
from django.db.models import Sum
from producto.models import Categoria, Inventario
from reportes.models import Venta
from datetime import datetime, timedelta


def home(request):
    nombre = 'cristian'

    # Categorías con total de productos
    categorias_qs = Categoria.objects.annotate(
        total=Sum('productos__cantidad_disponible')
    )

    categorias = [
        {"nombre": c.nombre, "total": c.total if c.total else 0}
        for c in categorias_qs
    ]

    # AGRUPAR EN BLOQUES DE 6
    grupos_categorias = [
        categorias[i:i+6] for i in range(0, len(categorias), 6)
    ]

    # Movimientos recientes
    movimientos = Inventario.objects.select_related('producto').all()[:10]

    # Ventas últimos 7 días
    hoy = datetime.today()
    labels = []
    data = []

    for i in range(6, -1, -1):
        dia = hoy - timedelta(days=i)
        inicio = datetime(dia.year, dia.month, dia.day)
        fin = inicio + timedelta(days=1)

        total = Venta.objects.aggregate(
            total=Sum('cantidad')
        )['total'] or 0

        labels.append(dia.strftime("%d/%m"))
        data.append(total)

    context = {
        'nombre': nombre,
        'titulo': 'Home',
        'grupos_categorias': grupos_categorias,
        'movimientos': movimientos,
        'labels': labels,
        'data': data,
    }

    return render(request, 'usuario.html', context)
    



    return render(request, 'home.html', context)


def categorias_json(request):
    categorias_qs = Categoria.objects.annotate(
        total=Sum('productos__cantidad_disponible')
    )
    categorias = [
        {"nombre": c.nombre, "total": c.total if c.total else 0}
        for c in categorias_qs
    ]
    return JsonResponse({"categorias": categorias})



def proveedores(request):
    return render(request, 'proveedor.html')


def reportes(request):
    return render(request, 'reportes.html')



def dashboard(request):
    return render(request, 'dashboard.html')
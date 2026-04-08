from django.shortcuts import render
from django.http import JsonResponse
from django.db.models import Sum
from producto.models import Categoria, Inventario


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

    # Agrupar en bloques de 6
    grupos_categorias = [
        categorias[i:i+6] for i in range(0, len(categorias), 6)
    ]

    # Movimientos recientes
    movimientos = Inventario.objects.select_related('producto').all()[:10]

    context = {
        'nombre': nombre,
        'titulo': 'Home',
        'grupos_categorias': grupos_categorias,
        'movimientos': movimientos,

        # 🔥 IMPORTANTE (para que no falle la gráfica)
        'labels': [],
        'data': [],
    }

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


def usuario(request):
    return render(request, 'usuario.html')


def dashboard(request):
    return render(request, 'dashboard.html')


def proveedores(request):
    return render(request, 'proveedor.html')


def reportes(request):
    return render(request, 'reportes.html')

def reportes(request):
    return render(request, 'ventas.html')
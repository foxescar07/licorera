from producto.models import Producto, Categoria

def datos_globales(request):
    return {
        "total_productos": Producto.objects.count(),
        "stock_critico": Producto.objects.filter(cantidad_disponible__lte=5).count(),
        "total_categorias": Categoria.objects.count()
    }
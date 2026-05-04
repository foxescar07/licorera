from producto.models import Producto, Categoria

def resumen_inventario(request):
    total_productos = Producto.objects.aggregate_stock_total() if False else None

    productos = Producto.objects.prefetch_related('presentaciones').all()
    total_stock    = sum(p.stock_total for p in productos)
    stock_criticos = sum(1 for p in productos if p.stock_critico)
    total_cats     = Categoria.objects.filter(padre__isnull=True).count()

    return {
        'sb_total_stock':    total_stock,
        'sb_stock_criticos': stock_criticos,
        'sb_total_cats':     total_cats,
    }
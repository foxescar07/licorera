from django.shortcuts import render
from django.utils import timezone
from ventas.models import Venta, DetalleVenta
from producto.models import Producto, Inventario, Categoria
from proveedores.models import Proveedor

def reportes(request):

    # ── Filtros de ventas ──────────────────────────────────────────
    fecha_inicio = request.GET.get('fecha_inicio')
    fecha_fin    = request.GET.get('fecha_fin')
    categoria_id = request.GET.get('categoria')
    cliente_q    = request.GET.get('cliente')

    ventas = Venta.objects.prefetch_related('detalles__producto').all()

    if fecha_inicio:
        ventas = ventas.filter(fecha__date__gte=fecha_inicio)
    if fecha_fin:
        ventas = ventas.filter(fecha__date__lte=fecha_fin)
    if categoria_id:
        ventas = ventas.filter(detalles__producto__categoria__id=categoria_id)
    if cliente_q:
        ventas = ventas.filter(cliente__icontains=cliente_q)

    # ── Datos generales ────────────────────────────────────────────
    productos   = Producto.objects.all().order_by('nombre')

    proveedores = Proveedor.objects.prefetch_related('productos').all().order_by('nombre')
    categorias  = Categoria.objects.all().order_by('nombre')

    proveedores = Proveedor.objects.all().order_by('nombre_empresa')  # ← corregido


    total_ventas    = sum(v.total() for v in ventas)
    total_productos = sum(det.cantidad for v in ventas for det in v.detalles.all())
    total_clientes  = ventas.values('cliente').distinct().count()

    total_registrados = productos.count()
    total_en_stock    = productos.filter(cantidad_disponible__gt=10).count()
    total_stock_bajo  = productos.filter(cantidad_disponible__gt=0, cantidad_disponible__lte=10).count()
    total_agotados    = productos.filter(cantidad_disponible=0).count()


    entradas = Inventario.objects.filter(tipo='entrada').select_related('producto').order_by('-fecha_actualizada')
    salidas  = Inventario.objects.filter(tipo='salida').select_related('producto').order_by('-fecha_actualizada')

    # ── Resumen diario ─────────────────────────────────────────────
    hoy         = timezone.now().date()
    ventas_hoy  = Venta.objects.prefetch_related('detalles__producto').filter(fecha__date=hoy)
    ingresos_hoy = sum(v.total() for v in ventas_hoy)

    movimientos_hoy    = Inventario.objects.filter(fecha_actualizada__date=hoy).select_related('producto')
    entradas_hoy       = movimientos_hoy.filter(tipo='entrada')
    salidas_hoy        = movimientos_hoy.filter(tipo='salida')
    total_entradas_hoy = sum(e.cantidad for e in entradas_hoy)
    total_salidas_hoy  = sum(s.cantidad for s in salidas_hoy)

    return render(request, 'reportes.html', {

        'ventas':            ventas,
        'total_ventas':      total_ventas,
        'total_productos':   total_productos,
        'total_clientes':    total_clientes,

        # Inventario
        'productos':         productos,

        'productos':         productos,
        'proveedores':       proveedores,

        'total_registrados': total_registrados,
        'total_en_stock':    total_en_stock,
        'total_stock_bajo':  total_stock_bajo,
        'total_agotados':    total_agotados,
        'entradas':          entradas,
        'salidas':           salidas,

        # Proveedores
        'proveedores':       proveedores,
        # Categorías
        'categorias':        categorias,
        # Filtros activos
        'fecha_inicio':      fecha_inicio or '',
        'fecha_fin':         fecha_fin or '',
        'categoria_id':      categoria_id or '',
        'cliente_q':         cliente_q or '',
        # Resumen diario
        'hoy':               hoy,
        'ventas_hoy':        ventas_hoy,
        'ingresos_hoy':      ingresos_hoy,
        'entradas_hoy':      entradas_hoy,
        'salidas_hoy':       salidas_hoy,
        'total_entradas_hoy': total_entradas_hoy,
        'total_salidas_hoy':  total_salidas_hoy,

    })
from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from ventas.models import Venta, DetalleVenta
from producto.models import Producto, Inventario, Categoria
from proveedores.models import Proveedor
import json
from django.core.serializers.json import DjangoJSONEncoder


def reportes(request):
    # ── SCRUM-239: Filtros para revisar información ────────────────────────
    fecha_inicio = request.GET.get('fecha_inicio')
    fecha_fin    = request.GET.get('fecha_fin')       # ← nuevo filtro
    categoria_id = request.GET.get('categoria')
    cliente_q    = request.GET.get('cliente')
    producto_q   = request.GET.get('producto')

    # ── SCRUM-235: Mostrar reportes generados — queryset base ──────────────
    ventas = Venta.objects.prefetch_related(
        'detalles__producto__categoria',
        'detalles__presentacion'
    ).all().order_by('-fecha')

    # ── SCRUM-239: Aplicar filtros ─────────────────────────────────────────
    if fecha_inicio:
        ventas = ventas.filter(fecha__date__gte=fecha_inicio)
    if fecha_fin:
        ventas = ventas.filter(fecha__date__lte=fecha_fin)
    if categoria_id:
        ventas = ventas.filter(
            detalles__producto__categoria_id=categoria_id
        ).distinct()
    if cliente_q:
        ventas = ventas.filter(
            cliente__icontains=cliente_q
        ).distinct()
    if producto_q:
        ventas = ventas.filter(
            detalles__producto__nombre__icontains=producto_q
        ).distinct()

    # ── Datos generales ────────────────────────────────────────────────────
    productos   = Producto.objects.all().order_by('nombre')
    proveedores = Proveedor.objects.all().order_by('nombre_empresa')
    categorias  = Categoria.objects.all().order_by('nombre')

    # ── Tarjetas resumen ───────────────────────────────────────────────────
    total_ventas    = sum(v.total_venta for v in ventas)
    total_productos = sum(det.cantidad for v in ventas for det in v.detalles.all())
    total_clientes  = ventas.values('cliente').distinct().count()

    # ── Inventario ─────────────────────────────────────────────────────────
    total_registrados = productos.count()
    total_en_stock    = productos.filter(cantidad_disponible__gt=10).count()
    total_stock_bajo  = productos.filter(cantidad_disponible__gt=0, cantidad_disponible__lte=10).count()
    total_agotados    = productos.filter(cantidad_disponible=0).count()

    entradas = (
        Inventario.objects
        .filter(tipo='entrada')
        .select_related('producto')
        .order_by('-fecha_actualizada')
    )
    salidas = (
        Inventario.objects
        .filter(tipo='salida')
        .select_related('producto')
        .order_by('-fecha_actualizada')
    )

    # ── SCRUM-237: Resumen diario — detalles completos ─────────────────────
    hoy        = timezone.now().date()
    ventas_hoy = Venta.objects.prefetch_related(
        'detalles__producto__categoria',
        'detalles__presentacion'
    ).filter(fecha__date=hoy).order_by('-fecha')

    ingresos_hoy = sum(v.total_venta for v in ventas_hoy)

    movimientos_hoy    = Inventario.objects.filter(fecha_actualizada__date=hoy).select_related('producto')
    entradas_hoy       = movimientos_hoy.filter(tipo='entrada')
    salidas_hoy        = movimientos_hoy.filter(tipo='salida')
    total_entradas_hoy = sum(e.cantidad for e in entradas_hoy)
    total_salidas_hoy  = sum(s.cantidad for s in salidas_hoy)

    # ── SCRUM-237: Detalle extendido del resumen diario ────────────────────
    productos_vendidos_hoy = (
        DetalleVenta.objects
        .filter(venta__fecha__date=hoy)
        .select_related('producto__categoria', 'presentacion', 'venta')
        .order_by('producto__nombre')
    )
    top_productos_hoy = {}
    for det in productos_vendidos_hoy:
        nombre = det.producto.nombre
        if nombre not in top_productos_hoy:
            top_productos_hoy[nombre] = {'cantidad': 0, 'subtotal': 0}
        top_productos_hoy[nombre]['cantidad'] += det.cantidad
        top_productos_hoy[nombre]['subtotal'] += float(det.subtotal())
    top_productos_hoy = sorted(
        top_productos_hoy.items(),
        key=lambda x: x[1]['subtotal'],
        reverse=True
    )[:5]

    # ── SCRUM-235: ventas_json para gráficas Chart.js ──────────────────────
    ventas_data = []
    for v in ventas:
        for det in v.detalles.all():
            ventas_data.append({
                "fecha":          v.fecha.strftime("%Y-%m-%d"),
                "hora":           v.fecha.strftime("%H:%M"),
                "cliente":        str(v.cliente),
                "producto":       det.producto.nombre,
                "presentacion":   det.presentacion.nombre if det.presentacion else "Unidad",
                "categoria":      (
                    det.producto.categoria.nombre
                    if det.producto.categoria
                    else "Sin categoría"
                ),
                "cantidad":       det.cantidad,
                "precio_unitario": float(det.precio_unitario),
                "subtotal":       float(det.subtotal()),
                "descuento":      float(v.descuento_porcentaje),
                "total_venta":    float(v.total_venta),
            })
    ventas_json = json.dumps(ventas_data, cls=DjangoJSONEncoder)

    return render(request, 'reportes.html', {
        # Historial filtrado (SCRUM-235 y SCRUM-239)
        'ventas':             ventas,
        'total_ventas':       total_ventas,
        'total_productos':    total_productos,
        'total_clientes':     total_clientes,

        # Catálogos
        'productos':          productos,
        'proveedores':        proveedores,
        'categorias':         categorias,

        # Inventario
        'total_registrados':  total_registrados,
        'total_en_stock':     total_en_stock,
        'total_stock_bajo':   total_stock_bajo,
        'total_agotados':     total_agotados,
        'entradas':           entradas,
        'salidas':            salidas,

        # Filtros activos (SCRUM-239)
        'fecha_inicio':       fecha_inicio or '',
        'fecha_fin':          fecha_fin or '',
        'categoria_id':       categoria_id or '',
        'cliente_q':          cliente_q or '',
        'producto_q':         producto_q or '',

        # Resumen diario con detalles (SCRUM-237)
        'hoy':                hoy,
        'ventas_hoy':         ventas_hoy,
        'ingresos_hoy':       ingresos_hoy,
        'entradas_hoy':       entradas_hoy,
        'salidas_hoy':        salidas_hoy,
        'total_entradas_hoy': total_entradas_hoy,
        'total_salidas_hoy':  total_salidas_hoy,
        'top_productos_hoy':  top_productos_hoy,  # ← nuevo: top 5 del día

        # JSON para gráficas
        'ventas_json':        ventas_json,
    })
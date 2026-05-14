from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.db import transaction
from decimal import Decimal, InvalidOperation
from functools import wraps
import hashlib
import json
from django.utils import timezone
from django.views.decorators.http import require_POST
 
from .models import Venta, DetalleVenta, AperturaCaja, CierreCaja, Devolucion, DetalleDevolucion
from .forms import VentaForm, DetalleVentaForm
from producto.models import Producto, Inventario, Categoria, PresentacionProducto
from usuario.models import Usuario
 
 
# ── DECORADOR PERSONALIZADO ───────────────────────────────────────────────────
def session_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.session.get('usuario_id'):
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return wrapper
 
 
# ── VISTAS ────────────────────────────────────────────────────────────────────
@session_required
def ventas_lista(request):
    ventas = Venta.objects.prefetch_related(
        'detalles__producto',
        'detalles__presentacion'
    ).all().order_by('-fecha')
    form       = VentaForm()
    detalle    = DetalleVentaForm()
    categorias = Categoria.objects.prefetch_related('productos__presentaciones').all()
 
    return render(request, 'ventas/ventas.html', {
        'ventas':     ventas,
        'form':       form,
        'detalle':    detalle,
        'categorias': categorias,
    })
 
 
@session_required
def nueva_venta(request):
    if request.method != 'POST':
        return redirect('ventas:ventas_lista')
 
    form             = VentaForm(request.POST)
    producto_ids     = request.POST.getlist('producto_id[]')
    presentacion_ids = request.POST.getlist('presentacion_id[]')
    cantidades       = request.POST.getlist('cantidad[]')
    precios          = request.POST.getlist('precio[]')
 
    def to_decimal(key, default='0'):
        try:
            return Decimal(request.POST.get(key, default) or default)
        except (InvalidOperation, TypeError):
            return Decimal('0')
 
    descuento_pct      = to_decimal('descuento_porcentaje')
    pago_efectivo      = to_decimal('pago_efectivo')
    pago_tarjeta       = to_decimal('pago_tarjeta')
    pago_transferencia = to_decimal('pago_transferencia')
    pago_nequi        = to_decimal('pago_nequi')
    pago_daviplata     = to_decimal('pago_daviplata')
 
    if not producto_ids:
        messages.error(request, "El carrito esta vacio.")
        return redirect('ventas:ventas_lista')
 
    if not form.is_valid():
        messages.error(request, "Revisa los campos del formulario.")
        return redirect('ventas:ventas_lista')
 
    items_validados = []
    subtotal_venta  = Decimal('0')
 
    for i, prod_id in enumerate(producto_ids):
        try:
            cantidad = int(cantidades[i])
            precio   = Decimal(precios[i])
            if cantidad <= 0 or precio < 0:
                raise ValueError
        except (ValueError, TypeError, InvalidOperation, IndexError):
            messages.error(request, f"Datos invalidos en el item {i+1}.")
            return redirect('ventas:ventas_lista')
 
        try:
            producto = Producto.objects.prefetch_related('presentaciones').get(pk=prod_id)
        except Producto.DoesNotExist:
            messages.error(request, f"Producto {i+1} no encontrado.")
            return redirect('ventas:ventas_lista')
 
        pres_id      = presentacion_ids[i] if i < len(presentacion_ids) else ''
        presentacion = None
 
        if pres_id:
            try:
                presentacion = PresentacionProducto.objects.get(pk=pres_id, producto=producto)
            except PresentacionProducto.DoesNotExist:
                messages.error(request, f"Presentacion invalida para {producto.nombre}.")
                return redirect('ventas:ventas_lista')
 
            if cantidad > presentacion.cantidad:
                messages.error(request, f"Stock insuficiente: solo hay {presentacion.cantidad} de {producto.nombre}.")
                return redirect('ventas:ventas_lista')
        else:
            if cantidad > producto.cantidad_disponible:
                messages.error(request, f"Stock insuficiente: solo hay {producto.cantidad_disponible} unidades de {producto.nombre}.")
                return redirect('ventas:ventas_lista')
 
        items_validados.append({
            'producto':     producto,
            'presentacion': presentacion,
            'cantidad':     cantidad,
            'precio':       precio,
        })
        subtotal_venta += precio * cantidad
 
    monto_descuento = (subtotal_venta * descuento_pct) / Decimal('100')
    total_final     = subtotal_venta - monto_descuento
 
    total_pagado = pago_efectivo + pago_tarjeta + pago_transferencia + pago_nequi + pago_daviplata
    if total_pagado < total_final:
        messages.error(request, f"El total pagado (${total_pagado:,.0f}) no cubre el total de la venta (${total_final:,.0f}).".replace(',', '.'))
        return redirect('ventas:ventas_lista')
 
    venta = form.save(commit=False)
    venta.descuento_porcentaje = descuento_pct
    venta.total_con_descuento  = total_final
    venta.pago_efectivo        = pago_efectivo
    venta.pago_tarjeta         = pago_tarjeta
    venta.pago_transferencia   = pago_transferencia
    venta.pago_nequi           = pago_nequi
    venta.pago_daviplata       = pago_daviplata
    venta.save()
 
    for item in items_validados:
        producto     = item['producto']
        presentacion = item['presentacion']
        cantidad     = item['cantidad']
        precio       = item['precio']
 
        DetalleVenta.objects.create(
            venta=venta,
            producto=producto,
            presentacion=presentacion,
            cantidad=cantidad,
            precio_unitario=precio,
        )
 
        if presentacion:
            presentacion.cantidad -= cantidad
            presentacion.save()
            unidades = cantidad * presentacion.unidades
        else:
            producto.cantidad_disponible -= cantidad
            producto.save()
            unidades = cantidad
 
        Inventario.objects.create(
            producto=producto,
            tipo='salida',
            cantidad=unidades,
            motivo='Venta registrada',
            ubicacion='Venta',
        )
 
    messages.success(request, f"Venta registrada - Total: ${total_final:,.0f}".replace(',', '.'))
    return redirect('ventas:ventas_lista')
 
 
@session_required
def eliminar_venta(request, pk):
    venta = get_object_or_404(Venta, pk=pk)
    if request.method == 'POST':
        for det in venta.detalles.all():
            if det.presentacion:
                det.presentacion.cantidad += det.cantidad
                det.presentacion.save()
                unidades = det.cantidad * det.presentacion.unidades
            else:
                det.producto.cantidad_disponible += det.cantidad
                det.producto.save()
                unidades = det.cantidad
 
            Inventario.objects.create(
                producto=det.producto,
                tipo='entrada',
                cantidad=unidades,
                motivo='Anulacion de venta',
                ubicacion='Devolucion',
            )
 
        venta.delete()
        messages.success(request, "Venta eliminada y stock restaurado.")
    return redirect('ventas:ventas_lista')
 
 
def producto_stock_json(request, pk):
    producto = get_object_or_404(Producto.objects.prefetch_related('presentaciones'), pk=pk)
    presentaciones = [
        {
            'id':       p.id,
            'nombre':   p.nombre,
            'unidades': p.unidades,
            'cantidad': p.cantidad,
            'precio':   float(p.precio),
        }
        for p in producto.presentaciones.all()
    ]
    return JsonResponse({
        'stock':          producto.cantidad_disponible,
        'precio':         float(producto.precio_unitario),
        'unidad':         producto.unidad,
        'presentaciones': presentaciones,
    })
 
 
@session_required
def lista_devoluciones(request):
    devoluciones = Devolucion.objects.select_related('venta').prefetch_related(
        'detalles__producto', 'detalles__presentacion'
    )
    return render(request, 'ventas/devoluciones.html', {
        'devoluciones': devoluciones,
    })
 
 
@session_required
def buscar_venta_devolucion(request):
    q = request.GET.get('q', '').strip()
    if not q:
        return JsonResponse({'ventas': []})
 
    ventas = Venta.objects.filter(cliente__icontains=q).order_by('-fecha')[:10]
    if q.isdigit():
        ventas = (Venta.objects.filter(pk=int(q)) | ventas).distinct()
 
    data = []
    for v in ventas:
        data.append({
            'id':      v.pk,
            'cliente': v.cliente,
            'fecha':   v.fecha.strftime('%d/%m/%Y %H:%M'),
            'total':   float(v.total_venta),
        })
    return JsonResponse({'ventas': data})
 
 
@session_required
def detalle_venta_devolucion(request, venta_id):
    venta = get_object_or_404(Venta, pk=venta_id)
    detalles = []
    for d in venta.detalles.select_related('producto', 'presentacion').all():
        detalles.append({
            'detalle_id':      d.pk,
            'producto_id':     d.producto.pk,
            'producto':        d.producto.nombre,
            'presentacion_id': d.presentacion.pk if d.presentacion else None,
            'presentacion':    d.presentacion.nombre if d.presentacion else '',
            'cantidad':        d.cantidad,
            'precio':          float(d.precio_unitario),
            'subtotal':        float(d.subtotal()),
        })
    return JsonResponse({
        'venta_id':  venta.pk,
        'cliente':   venta.cliente,
        'fecha':     venta.fecha.strftime('%d/%m/%Y %H:%M'),
        'total':     float(venta.total_venta),
        'descuento': float(venta.descuento_porcentaje),
        'detalles':  detalles,
    })
 
 
@session_required
@transaction.atomic
def registrar_devolucion(request):
    if request.method != 'POST':
        return redirect('ventas:lista_devoluciones')
 
    venta_id          = request.POST.get('venta_id')
    tiene_comprobante = request.POST.get('tiene_comprobante') == '1'
    restaurar_stock   = request.POST.get('restaurar_stock') == '1'
    motivo            = request.POST.get('motivo', 'otro')
    observaciones     = request.POST.get('observaciones', '')
 
    producto_ids     = request.POST.getlist('producto_id[]')
    presentacion_ids = request.POST.getlist('presentacion_id[]')
    cantidades       = request.POST.getlist('cantidad[]')
    precios          = request.POST.getlist('precio[]')
 
    if not tiene_comprobante:
        messages.warning(request, 'No se puede registrar la devolucion sin comprobante de compra.')
        return redirect('ventas:lista_devoluciones')
 
    venta = get_object_or_404(Venta, pk=venta_id)
 
    total_devuelto = sum(
        int(cantidades[i]) * float(precios[i])
        for i in range(len(producto_ids))
    )
 
    devolucion = Devolucion.objects.create(
        venta=venta,
        motivo=motivo,
        observaciones=observaciones,
        restaurar_stock=restaurar_stock,
        tiene_comprobante=tiene_comprobante,
        total_devuelto=total_devuelto,
    )
 
    for i in range(len(producto_ids)):
        producto     = get_object_or_404(Producto, pk=producto_ids[i])
        presentacion = None
        if presentacion_ids[i] and presentacion_ids[i] != 'null':
            presentacion = PresentacionProducto.objects.filter(pk=presentacion_ids[i]).first()
 
        cantidad = int(cantidades[i])
        precio   = float(precios[i])
 
        DetalleDevolucion.objects.create(
            devolucion=devolucion,
            producto=producto,
            presentacion=presentacion,
            cantidad=cantidad,
            precio_unitario=precio,
        )
 
        if restaurar_stock and presentacion:
            presentacion.cantidad += cantidad
            presentacion.save()
 
    messages.success(request, f'Devolucion {devolucion.numero} registrada correctamente.')
    return redirect('ventas:comprobante_devolucion', pk=devolucion.pk)
 
 
@session_required
def comprobante_devolucion(request, pk):
    devolucion = get_object_or_404(
        Devolucion.objects.select_related('venta').prefetch_related(
            'detalles__producto', 'detalles__presentacion'
        ),
        pk=pk,
    )
    return render(request, 'ventas/comprobante_devolucion.html', {
        'devolucion': devolucion,
    })
 
 
@session_required
def ventas_dia(request):
    hoy = timezone.localdate()
 
    ventas = Venta.objects.prefetch_related(
        'detalles__producto',
        'detalles__presentacion',
    ).filter(fecha__date=hoy).order_by('-fecha')
 
    total_dia = sum(v.total_venta for v in ventas)
    total_productos = sum(
        det.cantidad
        for v in ventas
        for det in v.detalles.all()
    )
 
    caja_abierta  = AperturaCaja.objects.filter(fecha=hoy).first()
    ultimo_cierre = CierreCaja.objects.filter(fecha=hoy).first()


    # ── Leer autorización de caja desde sesión ──
    caja_autorizado   = request.session.get('caja_autorizado', False)
    caja_autor_nombre = request.session.get('caja_autorizado_usuario', '')

    return render(request, 'ventas/ventas_dia.html', {
        'ventas':            ventas,
        'total_dia':         total_dia,
        'total_productos':   total_productos,
        'hoy':               hoy,
        'caja_abierta':      caja_abierta,
        'ultimo_cierre':     ultimo_cierre,
        'caja_autorizado':   caja_autorizado,
        'caja_autor_nombre': caja_autor_nombre,
    })
 
 
@require_POST
@session_required
def apertura_caja(request):
    try:
        data = json.loads(request.body)
    except (json.JSONDecodeError, ValueError):
        return JsonResponse({'ok': False, 'error': 'JSON invalido.'}, status=400)
 
    hoy = timezone.localdate()
 
    if AperturaCaja.objects.filter(fecha=hoy).exists():
        return JsonResponse({'ok': False, 'error': 'Ya existe una apertura para hoy.'}, status=400)
 
    monto_base = data.get('monto_base', 0)
    try:
        monto_base = float(monto_base)
        if monto_base <= 0:
            raise ValueError
    except (TypeError, ValueError):
        return JsonResponse({'ok': False, 'error': 'Monto base invalido.'}, status=400)
 
    AperturaCaja.objects.create(
        fecha=hoy,
        monto_base=monto_base,
        usuario=data.get('observacion', ''),
        denominaciones=data.get('denominaciones', {}),
    )


    # ── Limpiar autorización tras usarla ──
    request.session.pop('caja_autorizado', None)
    request.session.pop('caja_autorizado_usuario', None)
    request.session.pop('caja_autorizado_ts', None)


    return JsonResponse({'ok': True})
 
 
@require_POST
@session_required
def cierre_caja(request):
    try:
        data = json.loads(request.body)
    except (json.JSONDecodeError, ValueError):
        return JsonResponse({'ok': False, 'error': 'JSON invalido.'}, status=400)
 
    hoy = timezone.localdate()
 
    apertura = AperturaCaja.objects.filter(fecha=hoy).first()
    if not apertura:
        return JsonResponse({'ok': False, 'error': 'No hay apertura de caja para hoy.'}, status=400)
 
    try:
        total_contado  = float(data.get('total_contado', 0))
        monto_base_sig = float(data.get('monto_base_siguiente', 0))
        total_retirado = float(data.get('total_retirado', 0))
    except (TypeError, ValueError):
        return JsonResponse({'ok': False, 'error': 'Valores numericos invalidos.'}, status=400)
 
    CierreCaja.objects.update_or_create(
        fecha=hoy,
        defaults={
            'apertura':             apertura,
            'total_contado':        total_contado,
            'monto_base_siguiente': monto_base_sig,
            'total_retirado':       total_retirado,
            'denominaciones':       data.get('denominaciones', {}),
        }
    )


    # ── Limpiar autorización tras usarla ──
    request.session.pop('caja_autorizado', None)
    request.session.pop('caja_autorizado_usuario', None)
    request.session.pop('caja_autorizado_ts', None)

    return JsonResponse({'ok': True})
 
 
@require_POST
@session_required
def verificar_acceso_caja(request):
    try:
        data = json.loads(request.body)
    except (json.JSONDecodeError, ValueError):
        return JsonResponse({'ok': False, 'error': 'JSON invalido.'})
 
    password = data.get('password', '').strip()
    if not password:
        return JsonResponse({'ok': False, 'error': 'Ingresa tu contrasena.'})
 
    try:
        usuario = Usuario.objects.get(
            pk=request.session['usuario_id'],
            activo=True
        )
    except Usuario.DoesNotExist:
        return JsonResponse({'ok': False, 'error': 'Sesion invalida.'})
 
    clave_hash = hashlib.sha256(password.encode()).hexdigest()
    if usuario.clave != clave_hash:
        return JsonResponse({'ok': False, 'error': 'Contrasena incorrecta.'})
 
    es_admin  = usuario.rol == 'admin'
    es_cajero = usuario.rol == 'cajero'
 
    if not (es_admin or es_cajero):
        return JsonResponse({'ok': False, 'error': 'No tienes permiso. Tu usuario no es administrador ni cajero.'})


    # ── Guardar autorización en sesión ──
    request.session['caja_autorizado']         = True
    request.session['caja_autorizado_usuario'] = usuario.nombre_completo
    request.session['caja_autorizado_ts']      = timezone.now().isoformat()
    request.session.modified = True


    return JsonResponse({'ok': True, 'nombre': usuario.nombre_completo})
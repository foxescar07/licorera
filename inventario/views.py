from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from django.db import models as db_models
from django.db.models import Prefetch

from producto.models import Producto, AgendaInventario, Categoria, Inventario, PresentacionProducto

from .models import ConteoProducto, SesionConteo, ResultadoInventario, Lote


# ===============================
# INVENTARIO HOME
# ===============================
def inventario_home(request):
    agendas = AgendaInventario.objects.filter(estado__in=['pendiente', 'en_proceso']).order_by('fecha_programada')
    sesion  = SesionConteo.objects.order_by('-fecha_inicio').first()

    categoria_id = request.GET.get('categoria')
    if categoria_id:
        productos = Producto.objects.select_related('categoria').filter(categoria__pk=categoria_id)
    else:
        productos = Producto.objects.select_related('categoria').all()

    conteos = ConteoProducto.objects.filter(sesion=sesion).select_related('producto') if sesion else []

    discrepancias = []
    if sesion:
        for c in ConteoProducto.objects.filter(sesion=sesion).select_related('producto__categoria'):
            diff = c.cantidad_contada - c.producto.cantidad_disponible
            discrepancias.append({
                'producto':   c.producto,
                'en_sistema': c.producto.cantidad_disponible,
                'fisico':     c.cantidad_contada,
                'diferencia': diff,
                'estado':     'ok' if diff == 0 else ('sobrante' if diff > 0 else 'faltante'),
            })

    productos_con_codigo = productos.exclude(codigo='').exclude(codigo__isnull=True).count()
    productos_sin_codigo = productos.filter(codigo='').count() + productos.filter(codigo__isnull=True).count()

    historial_sesiones = SesionConteo.objects.filter(activa=False).order_by('-fecha_fin')

    if request.method == 'POST':
        AgendaInventario.objects.create(
            titulo=request.POST.get('titulo'),
            descripcion=request.POST.get('descripcion', ''),
            fecha_programada=request.POST.get('fecha_programada'),
        )
        messages.success(request, '✅ Inventario agendado correctamente.')
        return redirect('inventario:inventario_home')

    return render(request, 'inventario/inventario_home.html', {
        'agendas':            agendas,
        'sesion':             sesion,
        'productos':          productos,
        'conteos':            conteos,
        'discrepancias':      discrepancias,
        'categoria_activa':   categoria_id,
        'con_codigo':         productos_con_codigo,
        'sin_codigo':         productos_sin_codigo,
        'historial_sesiones': historial_sesiones,
    })


# ===============================
# AGENDA
# ===============================
def agenda_cambiar_estado(request, pk):
    agenda = get_object_or_404(AgendaInventario, pk=pk)
    nuevo_estado = request.POST.get('estado')
    if nuevo_estado in dict(AgendaInventario.ESTADO_CHOICES):
        agenda.estado = nuevo_estado
        agenda.save()
    return redirect('inventario:inventario_home')


# ===============================
# CONTEO
# ===============================
def guardar_conteo(request):
    if request.method == 'POST':
        sesion   = get_object_or_404(SesionConteo, pk=request.POST.get('sesion_id'))
        producto = get_object_or_404(Producto, pk=request.POST.get('producto_id'))
        ConteoProducto.objects.update_or_create(
            sesion=sesion, producto=producto,
            defaults={'cantidad_contada': request.POST.get('cantidad_contada')}
        )
        messages.success(request, f'✅ Conteo de {producto.nombre} guardado.')
    return redirect('inventario:inventario_home')


def conteo_inventario(request):
    if request.method == 'POST' and 'iniciar_sesion' in request.POST:
        SesionConteo.objects.filter(activa=True).update(activa=False)
        SesionConteo.objects.create(
            activa=True,
            responsable=request.user
        )
        messages.success(request, '✅ Nueva sesión de conteo iniciada.')
    return redirect('inventario:inventario_home')


# ===============================
# AJUSTE Y CIERRE
# ===============================
def ajustar_inventario(request, pk):
    if request.method == 'POST':
        producto       = get_object_or_404(Producto, pk=pk)
        nueva_cantidad = request.POST.get('nueva_cantidad')
        if nueva_cantidad is not None:
            producto.cantidad_disponible = int(nueva_cantidad)
            producto.save()
            messages.success(request, f'✅ Stock de {producto.nombre} actualizado a {nueva_cantidad}.')
        else:
            messages.error(request, '❌ Cantidad inválida.')
    return redirect('inventario:inventario_home')


def finalizar_inventario(request):
    if request.method == 'POST':
        sesion = SesionConteo.objects.filter(activa=True).first()
        if sesion:
            for conteo in sesion.conteos.select_related('producto'):
                ResultadoInventario.objects.update_or_create(
                    sesion=sesion,
                    producto=conteo.producto,
                    defaults={
                        'cantidad_sistema': conteo.producto.cantidad_disponible,
                        'cantidad_fisica':  conteo.cantidad_contada,
                        'diferencia':       conteo.cantidad_contada - conteo.producto.cantidad_disponible,
                    }
                )
            sesion.activa    = False
            sesion.estado    = 'finalizada'
            sesion.fecha_fin = timezone.now()
            sesion.save()
            messages.success(request, '✅ Inventario finalizado y resultados guardados.')
        else:
            messages.error(request, '❌ No hay sesión activa para finalizar.')
    return redirect('inventario:inventario_home')


def guardar_codigo_barras(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    if request.method == 'POST':
        nuevo_codigo = request.POST.get('codigo', '').strip()
        if nuevo_codigo:
            producto.codigo = nuevo_codigo
            producto.save()
            return JsonResponse({'ok': True, 'nombre': producto.nombre, 'codigo': nuevo_codigo})
        return JsonResponse({'ok': False, 'error': 'Código vacío'})
    return JsonResponse({'ok': False, 'error': 'Método no permitido'})


# ══════════════════════════════════════════════════════
# GESTIÓN DE PRODUCTOS
# La creación de productos se delega a producto:crear_producto.
# Esta vista solo renderiza la página y provee el contexto.
# ══════════════════════════════════════════════════════
def gestion_productos(request):
    productos_qs = Producto.objects.select_related('categoria').prefetch_related('presentaciones', 'lotes').all()

    categorias = Categoria.objects.filter(padre__isnull=True).prefetch_related(
        Prefetch(
            'productos',
            queryset=Producto.objects.prefetch_related('presentaciones').select_related('categoria')
        ),
        Prefetch(
            'subcategorias',
            queryset=Categoria.objects.prefetch_related(
                Prefetch(
                    'productos',
                    queryset=Producto.objects.prefetch_related('presentaciones').select_related('categoria')
                )
            )
        ),
    )

    todas_cats     = Categoria.objects.all()
    total_criticos = sum(1 for p in productos_qs if p.stock_critico)

    from producto.forms import ProductoRegistroForm
    form = ProductoRegistroForm()

    return render(request, 'inventario/gestion_productos.html', {
        'productos':      productos_qs,
        'categorias':     categorias,
        'todas_cats':     todas_cats,
        'form':           form,
        'total_criticos': total_criticos,
    })


# ══════════════════════════════════════════════════════
# SALIDA
# ══════════════════════════════════════════════════════
def gestion_salida(request):
    if request.method == 'POST':
        producto_id     = request.POST.get('producto')
        presentacion_id = request.POST.get('presentacion')
        cantidad_raw    = request.POST.get('cantidad', '')
        motivo          = request.POST.get('motivo', '').strip()
        lote_id         = request.POST.get('lote_id') or None
        

        try:
            cantidad = int(cantidad_raw)
            if cantidad <= 0:
                raise ValueError
        except (ValueError, TypeError):
            messages.error(request, '⚠️ La cantidad debe ser un número mayor a cero.')
            return redirect('inventario:gestion_productos')

        if not motivo:
            messages.error(request, '⚠️ Debes indicar el motivo de la salida.')
            return redirect('inventario:gestion_productos')
        
          # ── SCRUM-259: bloquear salida si el lote está vencido ──
        if lote_id:
            from django.utils import timezone
            lote = get_object_or_404(Lote, pk=lote_id)
            if lote.fecha_vencimiento and lote.fecha_vencimiento < timezone.now().date():
                messages.error(request, f'🚫 El lote "{lote.numero_lote}" está vencido desde el {lote.fecha_vencimiento.strftime("%d/%m/%Y")}. No se puede registrar la salida.')
                return redirect('inventario:gestion_productos')
        # ── fin validación ──

        producto = get_object_or_404(Producto, pk=producto_id)

        if presentacion_id:
            presentacion = get_object_or_404(PresentacionProducto, pk=presentacion_id, producto=producto)
            if cantidad > presentacion.cantidad:
                messages.error(request, f'⚠️ Stock insuficiente: solo hay {presentacion.cantidad} unidades de "{presentacion.nombre}".')
                return redirect('inventario:gestion_productos')
            presentacion.cantidad -= cantidad
            presentacion.save()
            Inventario.objects.create(
                producto=producto, tipo='salida',
                cantidad=cantidad * presentacion.unidades,
                motivo=motivo, ubicacion='Salida manual'
            )
            messages.success(request, f'✅ Salida de {cantidad} × "{presentacion.nombre}" registrada.')
        else:
            if cantidad > producto.cantidad_disponible:
                messages.error(request, f'⚠️ Stock insuficiente: solo hay {producto.cantidad_disponible} unidades de "{producto.nombre}".')
                return redirect('inventario:gestion_productos')
            producto.cantidad_disponible -= cantidad
            producto.save()
            Inventario.objects.create(
                producto=producto, tipo='salida',
                cantidad=cantidad, motivo=motivo, ubicacion='Salida manual'
            )
            messages.success(request, f'✅ Salida de {cantidad} uds de "{producto.nombre}" registrada.')

    return redirect('inventario:gestion_productos')


# ══════════════════════════════════════════════════════
# EDITAR / ELIMINAR PRODUCTO
# ══════════════════════════════════════════════════════
def gestion_producto_editar(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    if request.method == "POST":
        nombre       = request.POST.get('nombre', '').strip()
        codigo       = request.POST.get('codigo', '').strip()
        descripcion  = request.POST.get('descripcion', '').strip()
        categoria_pk = request.POST.get('categoria')
        precio_raw   = request.POST.get('precio_unitario', '').strip()

        if nombre:
            producto.nombre = nombre
        if codigo:
            producto.codigo = codigo
        producto.descripcion = descripcion

        if categoria_pk:
            try:
                producto.categoria_id = int(categoria_pk)
            except (ValueError, TypeError):
                pass

        if precio_raw:
            try:
                producto.precio_unitario = max(0, float(precio_raw))
            except (ValueError, TypeError):
                pass

        producto.save()

        # ✅ Actualizar presentaciones existentes (nombre, precio, cantidad)
        for key, valor in request.POST.items():
            if key.startswith('pres_nombre_'):
                pres_id = key.replace('pres_nombre_', '')
                try:
                    pres = PresentacionProducto.objects.get(pk=int(pres_id), producto=producto)

                    nuevo_nombre   = valor.strip()
                    nuevo_precio   = request.POST.get(f'pres_precio_{pres_id}', '').strip()
                    nueva_cantidad = request.POST.get(f'pres_cantidad_{pres_id}', '').strip()

                    if nuevo_nombre:
                        pres.nombre = nuevo_nombre
                    if nuevo_precio:
                        try:
                            pres.precio = max(0, float(nuevo_precio))
                        except (ValueError, TypeError):
                            pass
                    if nueva_cantidad:
                        try:
                            pres.cantidad = max(0, int(nueva_cantidad))
                        except (ValueError, TypeError):
                            pass
                    pres.save()
                except PresentacionProducto.DoesNotExist:
                    pass

        # ✅ Crear nuevas presentaciones agregadas desde el modal
        nuevos_nombres    = request.POST.getlist('nueva_pres_nombre[]')
        nuevos_precios    = request.POST.getlist('nueva_pres_precio[]')
        nuevas_cantidades = request.POST.getlist('nueva_pres_cantidad[]')

        for i, nombre_pres in enumerate(nuevos_nombres):
            nombre_pres = nombre_pres.strip()
            if not nombre_pres:
                continue
            try:
                precio_pres   = max(0, float(nuevos_precios[i]))   if i < len(nuevos_precios)    else 0
                cantidad_pres = max(0, int(nuevas_cantidades[i]))   if i < len(nuevas_cantidades) else 0
            except (ValueError, TypeError):
                precio_pres   = 0
                cantidad_pres = 0

            PresentacionProducto.objects.create(
                producto=producto,
                nombre=nombre_pres,
                precio=precio_pres,
                cantidad=cantidad_pres,
                unidades=1,  # valor por defecto para nuevas presentaciones
            )

        messages.success(request, f'✅ Producto "{producto.nombre}" actualizado correctamente.')

    return redirect('inventario:gestion_productos')

def gestion_producto_eliminar(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    if request.method == 'POST':
        nombre = producto.nombre
        producto.delete()
        messages.success(request, f'✅ Producto "{nombre}" eliminado.')
    return redirect('inventario:gestion_productos')


# ══════════════════════════════════════════════════════
# CATEGORÍAS
# ══════════════════════════════════════════════════════
def gestion_categoria_crear(request):
    if request.method == 'POST':
        nombre      = request.POST.get('nombre', '').strip()
        codigo      = request.POST.get('codigo', '').strip()
        descripcion = request.POST.get('descripcion', '').strip()
        padre_id    = request.POST.get('padre') or None

        if not nombre or not codigo:
            messages.error(request, '⚠️ Nombre y código son obligatorios.')
            return redirect('inventario:gestion_productos')

        if Categoria.objects.filter(codigo=codigo).exists():
            messages.error(request, f'⚠️ Ya existe una categoría con el código "{codigo}".')
            return redirect('inventario:gestion_productos')

        padre = get_object_or_404(Categoria, pk=padre_id) if padre_id else None
        Categoria.objects.create(nombre=nombre, codigo=codigo, descripcion=descripcion, padre=padre)
        tipo = 'Subcategoría' if padre else 'Categoría'
        messages.success(request, f'✅ {tipo} "{nombre}" creada.')

    return redirect('inventario:gestion_productos')


def gestion_categoria_editar(request, pk):
    categoria = get_object_or_404(Categoria, pk=pk)
    if request.method == 'POST':
        nombre      = request.POST.get('nombre', '').strip()
        codigo      = request.POST.get('codigo', '').strip()
        descripcion = request.POST.get('descripcion', '').strip()
        padre_id    = request.POST.get('padre') or None

        if not nombre or not codigo:
            messages.error(request, '⚠️ Nombre y código son obligatorios.')
            return redirect('inventario:gestion_productos')

        if Categoria.objects.filter(codigo=codigo).exclude(pk=pk).exists():
            messages.error(request, f'⚠️ Ya existe otra categoría con el código "{codigo}".')
            return redirect('inventario:gestion_productos')

        categoria.nombre      = nombre
        categoria.codigo      = codigo
        categoria.descripcion = descripcion
        categoria.padre       = get_object_or_404(Categoria, pk=padre_id) if padre_id else None
        categoria.save()
        messages.success(request, f'✅ Categoría "{nombre}" actualizada.')
    return redirect('inventario:gestion_productos')


def gestion_categoria_eliminar(request, pk):
    categoria = get_object_or_404(Categoria, pk=pk)
    if request.method == 'POST':
        if categoria.productos.exists() or categoria.subcategorias.exists():
            messages.error(request, f'⚠️ No se puede eliminar "{categoria.nombre}": tiene productos o subcategorías asociadas.')
        else:
            nombre = categoria.nombre
            categoria.delete()
            messages.success(request, f'✅ Categoría "{nombre}" eliminada.')
    return redirect('inventario:gestion_productos')


# ══════════════════════════════════════════════════════
# LOTES
# ══════════════════════════════════════════════════════
def registrar_lote(request):
    if request.method == 'POST':
        numero_lote = request.POST.get('numero_lote', '').strip()
        producto_id = request.POST.get('producto')
        fecha_vencimiento = request.POST.get('fecha_vencimiento') or None 

        if not numero_lote:
            messages.error(request, '⚠️ El número de lote es obligatorio.')
            return redirect('inventario:gestion_productos')

        if not producto_id:
            messages.error(request, '⚠️ Debes seleccionar un producto.')
            return redirect('inventario:gestion_productos')

        if Lote.objects.filter(numero_lote=numero_lote).exists():
            messages.error(request, f'⚠️ El lote "{numero_lote}" ya está registrado.')
            return redirect('inventario:gestion_productos')

        producto = get_object_or_404(Producto, pk=producto_id)

        Lote.objects.create(
            numero_lote=numero_lote,
            producto=producto,
            fecha_vencimiento=fecha_vencimiento,
            registrado_por=request.user if request.user.is_authenticated else None
        )

        # Mensaje con fecha de vencimiento si fue ingresada (SCRUM-260)
        if fecha_vencimiento:
            messages.success(request, f'✅ Lote "{numero_lote}" registrado para "{producto.nombre}" — vence el {Lote.fecha_vencimiento.strftime("%d/%m/%Y")}.')
        else:
            messages.success(request, f'✅ Lote "{numero_lote}" registrado para "{producto.nombre}" (sin fecha de vencimiento).')
        
        messages.success(request, f'✅ Lote "{numero_lote}" registrado para "{producto.nombre}".')
        return redirect('inventario:gestion_productos')

    return redirect('inventario:gestion_productos')
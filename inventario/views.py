from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from django.db import models as db_models
from django.http import JsonResponse


from producto.models import Producto, AgendaInventario, Categoria, Inventario, PresentacionProducto
from .models import ConteoProducto, SesionConteo, ResultadoInventario


# ===============================
# INVENTARIO HOME
# ===============================
def inventario_home(request):
    agendas = AgendaInventario.objects.filter(estado__in=['pendiente', 'en_proceso']).order_by('fecha_programada')
    sesion = SesionConteo.objects.order_by('-fecha_inicio').first()

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
        'agendas':          agendas,
        'sesion':           sesion,
        'productos':        productos,
        'conteos':          conteos,
        'discrepancias':    discrepancias,
        'categoria_activa': categoria_id,
        'con_codigo': productos_con_codigo,  
        'sin_codigo': productos_sin_codigo,   
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
            sesion.activa   = False
            sesion.estado   = 'finalizada'
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

    return redirect('inventario:inventario_home')


# ══════════════════════════════════════════════════════
# GESTIÓN DE PRODUCTOS (movido desde proveedores)
# ══════════════════════════════════════════════════════
def gestion_productos(request):
    productos  = Producto.objects.select_related('categoria').prefetch_related('presentaciones').all()
    categorias = Categoria.objects.filter(padre__isnull=True).prefetch_related('subcategorias')
    todas_cats = Categoria.objects.all()

    from producto.forms import ProductoRegistroForm
    form = ProductoRegistroForm()

    if request.method == 'POST' and request.POST.get('accion') == 'crear_producto':
        form = ProductoRegistroForm(request.POST)
        if form.is_valid():
            p = form.save(commit=False)
            p.cantidad_disponible = 0
            p.save()
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'ok': True, 'pk': p.pk, 'nombre': p.nombre})
            messages.success(request, f'✅ Producto "{p.nombre}" registrado.')
            return redirect('inventario:gestion_productos')
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'ok': False, 'error': 'Revisa los campos del formulario.'})
            messages.error(request, '⚠️ Revisa los campos del formulario.')

    return render(request, 'inventario/gestion_productos.html', {
        'productos':  productos,
        'categorias': categorias,
        'todas_cats': todas_cats,
        'form':       form,
    })


def gestion_salida(request):
    if request.method == 'POST':
        producto_id     = request.POST.get('producto')
        presentacion_id = request.POST.get('presentacion')
        cantidad_raw    = request.POST.get('cantidad', '')
        motivo          = request.POST.get('motivo', '').strip()

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


def gestion_producto_editar(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    if request.method == 'POST':
        nombre       = request.POST.get('nombre', '').strip()
        codigo       = request.POST.get('codigo', '').strip()
        descripcion  = request.POST.get('descripcion', '').strip()
        precio       = request.POST.get('precio_unitario', '').strip()
        categoria_id = request.POST.get('categoria') or None

        if not nombre or not codigo:
            messages.error(request, '⚠️ Nombre y código son obligatorios.')
            return redirect('inventario:gestion_productos')

        producto.nombre      = nombre
        producto.codigo      = codigo
        producto.descripcion = descripcion
        if precio:
            producto.precio_unitario = precio
        if categoria_id:
            producto.categoria = get_object_or_404(Categoria, pk=categoria_id)
        producto.save()
        messages.success(request, f'✅ Producto "{nombre}" actualizado.')
    return redirect('inventario:gestion_productos')


def gestion_producto_eliminar(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    if request.method == 'POST':
        nombre = producto.nombre
        producto.delete()
        messages.success(request, f'✅ Producto "{nombre}" eliminado.')
    return redirect('inventario:gestion_productos')


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


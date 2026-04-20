from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta

from producto.models import Producto, Inventario, Categoria, PresentacionProducto
from .models import Proveedor, Compra
from .forms import ProveedorForm


# ===============================
# DASHBOARD PROVEEDORES
# ===============================
def inicio_proveedores(request):
    proveedores = Proveedor.objects.all().order_by('-ultima_modificacion')

    total        = proveedores.count()
    hace_30_dias = timezone.now() - timedelta(days=30)
    nuevos       = proveedores.filter(fecha_registro__gte=hace_30_dias).count()
    ultimo       = proveedores.first()
    fecha_u      = ultimo.ultima_modificacion if ultimo else None

    if request.method == 'POST':
        form = ProveedorForm(request.POST)
        if form.is_valid():
            p = form.save(commit=False)
            if request.user.is_authenticated:
                p.registrado_por = request.user
                p.modificado_por = request.user
            p.save()
            messages.success(request, f'¡Proveedor "{p.nombre_empresa}" registrado!')
            return redirect('proveedores')
    else:
        form = ProveedorForm()

    context = {
        'proveedores':          proveedores,
        'form':                 form,
        'total_proveedores':    total,
        'nuevos_mes':           nuevos,
        'proveedores_activos':  total,
        'ordenes_pendientes':   0,
        'porcentaje_activos':   100 if total > 0 else 0,
        'ultima_actualizacion': fecha_u,
    }
    return render(request, 'proveedores/proveedor.html', context)


# ===============================
# EDITAR PROVEEDOR
# ===============================
def editar_proveedor(request, id):
    proveedor = get_object_or_404(Proveedor, id=id)

    if request.method == 'POST':
        form = ProveedorForm(request.POST, instance=proveedor)
        if form.is_valid():
            p = form.save(commit=False)
            if request.user.is_authenticated:
                p.modificado_por = request.user
            p.ultima_modificacion = timezone.now()
            p.save()
            messages.success(request, f'¡Proveedor "{p.nombre_empresa}" actualizado correctamente!')
            return redirect('proveedores')
    else:
        form = ProveedorForm(instance=proveedor)

    return render(request, 'proveedores/editar_proveedor.html', {
        'form':      form,
        'proveedor': proveedor
    })


# ===============================
# ELIMINAR PROVEEDOR
# ===============================
def eliminar_proveedor(request, id):
    proveedor = get_object_or_404(Proveedor, id=id)
    if request.method == 'POST':
        nombre = proveedor.nombre_empresa
        proveedor.delete()
        messages.success(request, f'¡Proveedor "{nombre}" eliminado!')
    return redirect('proveedores')


# ===============================
# MARCAR COMPRA COMO RECIBIDA
# ===============================
def marcar_recibida(request, compra_id):
    if request.method == 'POST':
        compra = get_object_or_404(Compra, id=compra_id)
        compra.recibida = True
        compra.save()
        messages.success(request, f'Compra de "{compra.producto.nombre}" marcada como recibida.')
    return redirect(request.META.get('HTTP_REFERER', 'proveedores'))


# ===============================
# REGISTRAR COMPRA
# ===============================
def registrar_compra(request, proveedor_id):
    proveedor_obj     = get_object_or_404(Proveedor, id=proveedor_id)
    productos         = Producto.objects.prefetch_related('presentaciones').all()
    todos_proveedores = Proveedor.objects.all().order_by('nombre_empresa')
    compras           = Compra.objects.filter(proveedor=proveedor_obj).order_by('-fecha_registro')
    subtotal          = sum(c.total for c in compras if c.total)
    pendientes        = Compra.objects.filter(recibida=False).order_by('-fecha_registro')[:5]
    total_pendientes  = Compra.objects.filter(recibida=False).count()

    if request.method == 'POST':
        id_prod = request.POST.get('producto')
        cant    = request.POST.get('cantidad')
        precio  = request.POST.get('precio_unitario')

        if not id_prod or not cant or not precio:
            messages.warning(request, "Completa todos los campos.")
        else:
            try:
                producto_instancia = Producto.objects.get(id=int(id_prod))
                cantidad_int       = int(cant)

                if cantidad_int <= 0:
                    messages.error(request, "La cantidad debe ser mayor a cero.")
                    return redirect('registrar_compra', proveedor_id=proveedor_id)

                Compra.objects.create(
                    proveedor       = proveedor_obj,
                    producto        = producto_instancia,
                    cantidad        = cantidad_int,
                    precio_unitario = precio if precio else None,
                )

                producto_instancia.cantidad_disponible += cantidad_int
                producto_instancia.save()

                Inventario.objects.create(
                    producto  = producto_instancia,
                    tipo      = 'entrada',
                    cantidad  = cantidad_int,
                    motivo    = f'Compra a proveedor: {proveedor_obj.nombre_empresa}',
                    ubicacion = 'Ingreso por compra'
                )

                messages.success(
                    request,
                    f'✅ {cantidad_int} unidades de "{producto_instancia.nombre}" ingresadas.'
                )
                return redirect('registrar_compra', proveedor_id=proveedor_id)

            except Producto.DoesNotExist:
                messages.error(request, "El producto seleccionado no existe.")
            except Exception as e:
                messages.error(request, f"Error: {e}")

    return render(request, 'proveedores/compra.html', {
        'proveedor':         proveedor_obj,
        'todos_proveedores': todos_proveedores,
        'productos':         productos,
        'compras':           compras,
        'subtotal_compras':  subtotal,
        'pendientes':        pendientes,
        'total_pendientes':  total_pendientes,
    })


# ===============================
# GESTIÓN DE PRODUCTOS
# ===============================
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
            messages.success(request, f'✅ Producto "{p.nombre}" registrado.')
            return redirect('gestion_productos')
        else:
            messages.error(request, '⚠️ Revisa los campos del formulario.')

    return render(request, 'proveedores/gestion_productos.html', {
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
            return redirect('gestion_productos')

        if not motivo:
            messages.error(request, '⚠️ Debes indicar el motivo de la salida.')
            return redirect('gestion_productos')

        producto = get_object_or_404(Producto, pk=producto_id)

        if presentacion_id:
            presentacion = get_object_or_404(PresentacionProducto, pk=presentacion_id, producto=producto)
            if cantidad > presentacion.cantidad:
                messages.error(request, f'⚠️ Stock insuficiente: solo hay {presentacion.cantidad} unidades de "{presentacion.nombre}".')
                return redirect('gestion_productos')
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
                return redirect('gestion_productos')
            producto.cantidad_disponible -= cantidad
            producto.save()
            Inventario.objects.create(
                producto=producto, tipo='salida',
                cantidad=cantidad, motivo=motivo, ubicacion='Salida manual'
            )
            messages.success(request, f'✅ Salida de {cantidad} uds de "{producto.nombre}" registrada.')

    return redirect('gestion_productos')


def gestion_categoria_crear(request):
    if request.method == 'POST':
        nombre      = request.POST.get('nombre', '').strip()
        codigo      = request.POST.get('codigo', '').strip()
        descripcion = request.POST.get('descripcion', '').strip()
        padre_id    = request.POST.get('padre') or None

        if not nombre or not codigo:
            messages.error(request, '⚠️ Nombre y código son obligatorios.')
            return redirect('gestion_productos')

        if Categoria.objects.filter(codigo=codigo).exists():
            messages.error(request, f'⚠️ Ya existe una categoría con el código "{codigo}".')
            return redirect('gestion_productos')

        padre = get_object_or_404(Categoria, pk=padre_id) if padre_id else None
        Categoria.objects.create(nombre=nombre, codigo=codigo, descripcion=descripcion, padre=padre)
        tipo = 'Subcategoría' if padre else 'Categoría'
        messages.success(request, f'✅ {tipo} "{nombre}" creada.')

    return redirect('gestion_productos')


def gestion_categoria_eliminar(request, pk):
    categoria = get_object_or_404(Categoria, pk=pk)
    if request.method == 'POST':
        if categoria.productos.exists() or categoria.subcategorias.exists():
            messages.error(request, f'⚠️ No se puede eliminar "{categoria.nombre}": tiene productos o subcategorías asociadas.')
        else:
            nombre = categoria.nombre
            categoria.delete()
            messages.success(request, f'✅ Categoría "{nombre}" eliminada.')
    return redirect('gestion_productos')


def gestion_producto_eliminar(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    if request.method == 'POST':
        nombre = producto.nombre
        producto.delete()
        messages.success(request, f'✅ Producto "{nombre}" eliminado.')
    return redirect('gestion_productos')
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Sum
from django.db import transaction
from .models import Producto, Categoria, Inventario, AgendaInventario, PresentacionProducto, Lote
from .forms import ProductoForm, AgendaInventarioForm, PresentacionForm, ProductoRegistroForm


def producto_lista(request):
    todas_categorias   = Categoria.objects.all()
    categorias_raiz    = Categoria.objects.filter(padre__isnull=True)
    resumen_categorias = []
    for cat in todas_categorias:
        resumen_categorias.append({
            "nombre": cat.nombre,
            "total":  cat.productos.count(),
            "pk":     cat.pk,
        })
    productos = Producto.objects.select_related("categoria").prefetch_related(
        "presentaciones", "lotes", "movimientos"
    ).all()
    context = {
        "productos":          productos,
        "resumen_categorias": resumen_categorias,
        "categorias":         categorias_raiz,
        "form":               ProductoRegistroForm(),
    }
    return render(request, "producto.html", context)


def producto_detalle(request, pk):
    producto    = get_object_or_404(Producto, pk=pk)
    movimientos = producto.movimientos.all()
    return render(request, "producto_detalle.html", {"producto": producto, "movimientos": movimientos})


def producto_crear(request):
    if request.method == 'POST':
        form = ProductoRegistroForm(request.POST)
        if form.is_valid():
            p = form.save(commit=False)
            p.cantidad_disponible = 0
            p.save()
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'ok': True, 'pk': p.pk, 'nombre': p.nombre})
            messages.success(request, f'✅ Producto "{p.nombre}" registrado.')
            return redirect('producto:producto_lista')
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'ok': False, 'error': 'Revisa los campos del formulario.'})
            messages.error(request, '⚠️ Revisa los campos del formulario.')
    return redirect('producto:producto_lista')


def producto_editar(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    if request.method == 'POST':
        nombre       = request.POST.get('nombre', '').strip()
        codigo       = request.POST.get('codigo', '').strip()
        descripcion  = request.POST.get('descripcion', '').strip()
        precio_raw   = request.POST.get('precio_unitario', '').strip()
        categoria_id = request.POST.get('categoria') or None
        if not nombre or not codigo:
            messages.error(request, '⚠️ Nombre y código son obligatorios.')
            next_url = request.POST.get('next') or request.GET.get('next')
            return redirect(next_url if next_url else 'producto:producto_lista')
        producto.nombre      = nombre
        producto.codigo      = codigo
        producto.descripcion = descripcion
        if precio_raw:
            try:
                producto.precio_unitario = float(precio_raw)
            except ValueError:
                messages.error(request, '⚠️ El precio ingresado no es válido.')
                next_url = request.POST.get('next') or request.GET.get('next')
                return redirect(next_url if next_url else 'producto:producto_lista')
        if categoria_id:
            producto.categoria = get_object_or_404(Categoria, pk=categoria_id)
        producto.save()
        messages.success(request, f'✅ Producto "{nombre}" actualizado.')
    next_url = request.POST.get('next') or request.GET.get('next')
    return redirect(next_url if next_url else 'producto:producto_lista')


def producto_eliminar(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    if request.method == 'POST':
        nombre = producto.nombre
        producto.delete()
        messages.success(request, f'✅ Producto "{nombre}" eliminado.')
    next_url = request.POST.get('next') or request.GET.get('next')
    return redirect(next_url if next_url else 'producto:producto_lista')


def presentaciones_guardar(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    if request.method == 'POST':
        nombres    = request.POST.getlist('nombre[]')
        unidades   = request.POST.getlist('unidades_base[]')
        precios    = request.POST.getlist('precio[]')
        cantidades = request.POST.getlist('cantidad[]')
        try:
            with transaction.atomic():
                precios_existentes = {p.nombre: p.precio for p in producto.presentaciones.all()}
                producto.presentaciones.all().delete()
                for n, u, precio_nuevo, c in zip(nombres, unidades, precios, cantidades):
                    n = n.strip()
                    if not n or not u:
                        continue
                    precio_raw   = precio_nuevo.strip() if precio_nuevo else ''
                    precio_final = precio_raw if precio_raw else precios_existentes.get(n, '0')
                    PresentacionProducto.objects.create(
                        producto=producto,
                        nombre=n,
                        unidades=int(u),
                        precio=precio_final,
                        cantidad=int(c) if c else 0,
                    )
            messages.success(request, f'✅ Presentaciones de {producto.nombre} guardadas.')
        except Exception as e:
            messages.error(request, f'❌ Error al guardar presentaciones: {e}')
    next_url = request.POST.get('next') or request.GET.get('next')
    return redirect(next_url if next_url else 'producto:producto_lista')


def presentaciones_json(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    data     = list(producto.presentaciones.values("id", "nombre", "unidades", "precio", "cantidad"))
    return JsonResponse({"presentaciones": data, "producto": producto.nombre})


def registrar_lote(request):
    if request.method == 'POST':
        numero_lote = request.POST.get('numero_lote', '').strip()
        producto_id = request.POST.get('producto')
        if not numero_lote or not producto_id:
            messages.error(request, '⚠️ Número de lote y producto son obligatorios.')
            return redirect('inventario:gestion_productos')
        producto = get_object_or_404(Producto, pk=producto_id)
        Lote.objects.create(producto=producto, numero_lote=numero_lote)
        messages.success(request, f'✅ Lote "{numero_lote}" registrado para {producto.nombre}.')
    return redirect('inventario:gestion_productos')


def stock_status(request):
    productos = Producto.objects.prefetch_related('presentaciones').all()
    criticos  = []
    bajos     = []
    for p in productos:
        stock_pres  = p.presentaciones.aggregate(total=Sum('cantidad'))['total'] or 0
        stock_total = p.cantidad_disponible + stock_pres
        if stock_total == 0:
            criticos.append({"nombre": p.nombre, "cantidad": stock_total})
        elif stock_total <= 10:
            bajos.append({"nombre": p.nombre, "cantidad": stock_total})
    estado   = "rojo" if criticos else "amarillo" if bajos else "verde"
    response = JsonResponse({
        "estado":        estado,
        "criticos":      criticos,
        "bajos":         bajos,
        "total_alertas": len(criticos) + len(bajos),
    })
    response['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response['Pragma']        = 'no-cache'
    return response


def producto_salida(request):
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
            messages.error(request, '⚠️ La cantidad debe ser un número entero mayor a cero.')
            return redirect('producto:producto_lista')
        if not motivo:
            messages.error(request, '⚠️ Debes indicar el motivo de la salida.')
            return redirect('producto:producto_lista')
        producto = get_object_or_404(Producto, pk=producto_id)
        if presentacion_id:
            presentacion = get_object_or_404(PresentacionProducto, pk=presentacion_id, producto=producto)
            if cantidad > presentacion.cantidad:
                messages.error(request,
                    f'⚠️ Stock insuficiente: solo hay {presentacion.cantidad} '
                    f'unidades de "{presentacion.nombre}".')
                return redirect('producto:producto_lista')
            presentacion.cantidad -= cantidad
            presentacion.save()
            Inventario.objects.create(
                producto=producto, tipo='salida',
                cantidad=cantidad * presentacion.unidades,
                motivo=motivo, ubicacion='Salida manual',
            )
            messages.success(request,
                f'✅ Salida: {cantidad} × "{presentacion.nombre}" de {producto.nombre}. Motivo: {motivo}.')
        else:
            if cantidad > producto.cantidad_disponible:
                messages.error(request,
                    f'⚠️ Stock insuficiente: solo hay {producto.cantidad_disponible} uds sueltas.')
                return redirect('producto:producto_lista')
            producto.cantidad_disponible -= cantidad
            producto.save()
            Inventario.objects.create(
                producto=producto, tipo='salida',
                cantidad=cantidad, motivo=motivo, ubicacion='Salida manual',
            )
            messages.success(request,
                f'✅ Salida: {cantidad} uds sueltas de {producto.nombre}. Motivo: {motivo}.')
    return redirect('producto:producto_lista')


def agenda_lista(request):
    form = AgendaInventarioForm()
    if request.method == 'POST':
        form = AgendaInventarioForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, '✅ Agenda registrada correctamente.')
            return redirect('producto:agenda_lista')
        else:
            messages.error(request, '⚠️ Revisa los campos del formulario.')
    agendas = AgendaInventario.objects.all()
    return render(request, 'agenda.html', {'form': form, 'agendas': agendas})


def agenda_eliminar(request, pk):
    agenda = get_object_or_404(AgendaInventario, pk=pk)
    if request.method == 'POST':
        agenda.delete()
        messages.success(request, '✅ Agenda eliminada.')
    return redirect('producto:agenda_lista')


def categoria_crear(request):
    if request.method == 'POST':
        nombre      = request.POST.get('nombre', '').strip()
        codigo      = request.POST.get('codigo', '').strip()
        descripcion = request.POST.get('descripcion', '').strip()
        if Categoria.objects.filter(codigo=codigo).exists():
            messages.error(request, f'⚠️ Ya existe una categoría con el código "{codigo}".')
        else:
            Categoria.objects.create(nombre=nombre, codigo=codigo, descripcion=descripcion)
            messages.success(request, '✅ Categoría creada correctamente.')
    return redirect('producto:producto_lista')


def gestion_productos(request):
    if request.method == 'POST':
        accion = request.POST.get('accion')
        if accion == 'crear_producto':
            form = ProductoForm(request.POST)
            if form.is_valid():
                p = form.save(commit=False)
                p.cantidad_disponible = 0
                p.save()
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({'ok': True, 'pk': p.pk, 'nombre': p.nombre})
                messages.success(request, f'✅ Producto "{p.nombre}" creado.')
            else:
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({'ok': False, 'error': 'Revisa los campos.'})
                messages.error(request, '⚠️ Revisa los campos del formulario.')
            return redirect('inventario:gestion_productos')

    categorias     = Categoria.objects.filter(padre__isnull=True).prefetch_related('subcategorias', 'productos')
    todas_cats     = Categoria.objects.all()
    productos      = Producto.objects.select_related('categoria').prefetch_related(
        'presentaciones', 'lotes', 'movimientos'
    ).all()
    total_criticos = sum(1 for p in productos if p.stock_critico)
    context = {
        'categorias':     categorias,
        'todas_cats':     todas_cats,
        'productos':      productos,
        'total_criticos': total_criticos,
        'form':           ProductoForm(),
    }
    return render(request, 'gestion_productos.html', context)


def gestion_producto_editar(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    if request.method == 'POST':
        nombre       = request.POST.get('nombre', '').strip()
        codigo       = request.POST.get('codigo', '').strip()
        descripcion  = request.POST.get('descripcion', '').strip()
        precio_raw   = request.POST.get('precio_unitario', '').strip()
        categoria_id = request.POST.get('categoria') or None
        if not nombre or not codigo:
            messages.error(request, '⚠️ Nombre y código son obligatorios.')
            return redirect('inventario:gestion_productos')
        producto.nombre      = nombre
        producto.codigo      = codigo
        producto.descripcion = descripcion
        if precio_raw:
            try:
                producto.precio_unitario = float(precio_raw)
            except ValueError:
                messages.error(request, '⚠️ Precio no válido.')
                return redirect('inventario:gestion_productos')
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
            messages.error(request, '⚠️ Cantidad inválida.')
            return redirect('inventario:gestion_productos')
        producto = get_object_or_404(Producto, pk=producto_id)
        if presentacion_id:
            presentacion = get_object_or_404(PresentacionProducto, pk=presentacion_id, producto=producto)
            if cantidad > presentacion.cantidad:
                messages.error(request, f'⚠️ Stock insuficiente en "{presentacion.nombre}".')
                return redirect('inventario:gestion_productos')
            presentacion.cantidad -= cantidad
            presentacion.save()
            Inventario.objects.create(
                producto=producto, tipo='salida',
                cantidad=cantidad * presentacion.unidades,
                motivo=motivo, ubicacion='Salida manual',
            )
            messages.success(request, f'✅ Salida: {cantidad} × "{presentacion.nombre}".')
        else:
            if cantidad > producto.cantidad_disponible:
                messages.error(request, f'⚠️ Stock insuficiente.')
                return redirect('inventario:gestion_productos')
            producto.cantidad_disponible -= cantidad
            producto.save()
            Inventario.objects.create(
                producto=producto, tipo='salida',
                cantidad=cantidad, motivo=motivo, ubicacion='Salida manual',
            )
            messages.success(request, f'✅ Salida: {cantidad} uds de {producto.nombre}.')
    return redirect('inventario:gestion_productos')


def gestion_categoria_crear(request):
    if request.method == 'POST':
        nombre      = request.POST.get('nombre', '').strip()
        codigo      = request.POST.get('codigo', '').strip()
        descripcion = request.POST.get('descripcion', '').strip()
        padre_id    = request.POST.get('padre') or None
        if Categoria.objects.filter(codigo=codigo).exists():
            messages.error(request, f'⚠️ Ya existe una categoría con el código "{codigo}".')
        else:
            padre = get_object_or_404(Categoria, pk=padre_id) if padre_id else None
            Categoria.objects.create(nombre=nombre, codigo=codigo, descripcion=descripcion, padre=padre)
            messages.success(request, '✅ Categoría creada.')
    return redirect('inventario:gestion_productos')


def gestion_categoria_editar(request, pk):
    categoria = get_object_or_404(Categoria, pk=pk)
    if request.method == 'POST':
        nombre      = request.POST.get('nombre', '').strip()
        codigo      = request.POST.get('codigo', '').strip()
        descripcion = request.POST.get('descripcion', '').strip()
        padre_id    = request.POST.get('padre') or None
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
        nombre = categoria.nombre
        categoria.delete()
        messages.success(request, f'✅ Categoría "{nombre}" eliminada.')
    return redirect('inventario:gestion_productos')
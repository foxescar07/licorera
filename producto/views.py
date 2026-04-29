from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Sum
from .models import Producto, Categoria, Inventario, AgendaInventario, PresentacionProducto
from .forms import ProductoForm, AgendaInventarioForm, PresentacionForm, ProductoRegistroForm
from django.db import transaction


# ===============================
# LISTA DE PRODUCTOS
# ===============================
def producto_lista(request):
    form = ProductoForm()

    if request.method == "POST":
        form = ProductoForm(request.POST)
        if form.is_valid():
            producto = form.save()
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'ok': True, 'pk': producto.pk, 'nombre': producto.nombre})
            messages.success(request, "✅ Producto registrado correctamente.")
            return redirect("producto:producto_lista")
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                errores = {f: e.get_json_data() for f, e in form.errors.items()}
                return JsonResponse({'ok': False, 'error': 'Revisa los campos del formulario.', 'errores': errores})
            messages.error(request, "⚠️ Revisa los campos del formulario.")

    categorias = Categoria.objects.all()
    resumen_categorias = []
    for cat in categorias:
        resumen_categorias.append({"nombre": cat.nombre, "total": cat.productos.count(), "pk": cat.pk})

    productos = Producto.objects.select_related("categoria").prefetch_related("presentaciones").all()

    context = {
        "form":               form,
        "productos":          productos,
        "resumen_categorias": resumen_categorias,
    }
    return render(request, "producto.html", context)


def crear_producto(request):
    if request.method != 'POST':
        return redirect('inventario:gestion_productos')

    form = ProductoRegistroForm(request.POST)
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    next_url = request.POST.get('next') or request.GET.get('next') or 'inventario:gestion_productos'

    if form.is_valid():
        p = form.save(commit=False)

        # ── Cantidad inicial ──────────────────────────────────────────────
        try:
            cantidad = int(request.POST.get('cantidad_disponible', 0) or 0)
            p.cantidad_disponible = max(0, cantidad)
        except (ValueError, TypeError):
            p.cantidad_disponible = 0

        # ── Precio unitario ───────────────────────────────────────────────
        precio_raw = request.POST.get('precio_unitario', '').strip()
        if precio_raw:
            try:
                p.precio_unitario = max(0, float(precio_raw))
            except (ValueError, TypeError):
                pass

        p.save()

        if is_ajax:
            return JsonResponse({'ok': True, 'pk': p.pk, 'nombre': p.nombre})
        messages.success(request, f'✅ Producto "{p.nombre}" registrado.')
        return redirect(next_url)
    else:
        if is_ajax:
            errors = {f: e.get_json_data() for f, e in form.errors.items()}
            return JsonResponse({'ok': False, 'error': 'Revisa los campos del formulario.', 'errores': errors})
        messages.error(request, '⚠️ Revisa los campos del formulario.')
        return redirect(next_url)


# ===============================
# DETALLE
# ===============================
def producto_detalle(request, pk):
    producto    = get_object_or_404(Producto, pk=pk)
    movimientos = producto.movimientos.all()
    return render(request, "producto_detalle.html", {"producto": producto, "movimientos": movimientos})


# ===============================
# EDITAR
# ===============================
def producto_editar(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    if request.method == "POST":
        form = ProductoForm(request.POST, instance=producto)
        if form.is_valid():
            form.save()
            messages.success(request, "✅ Producto actualizado correctamente.")
        else:
            messages.error(request, "⚠️ Revisa los campos del formulario.")
    return redirect("producto:producto_lista")


# ===============================
# PRESENTACIONES
# ===============================
def presentaciones_guardar(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    if request.method == "POST":
        nombres    = request.POST.getlist("nombre[]")
        unidades   = request.POST.getlist("unidades_base[]")
        precios    = request.POST.getlist("precio[]")
        cantidades = request.POST.getlist("cantidad[]")

        try:
            with transaction.atomic():
                nuevas = []
                for nombre_v, unidad_v, precio_v, cantidad_v in zip(nombres, unidades, precios, cantidades):
                    nombre_v = nombre_v.strip()
                    if not nombre_v:
                        continue          # fila sin nombre → ignorar
                    if not unidad_v:
                        continue
                    # precio vacío → 0, no saltamos la fila
                    try:
                        precio_f = float(precio_v) if precio_v.strip() else 0
                    except (ValueError, TypeError):
                        precio_f = 0
                    try:
                        cantidad_i = int(cantidad_v) if cantidad_v else 0
                    except (ValueError, TypeError):
                        cantidad_i = 0

                    nuevas.append(dict(
                        nombre=nombre_v,
                        unidades=int(unidad_v),
                        precio=precio_f,
                        cantidad=max(0, cantidad_i),
                    ))

                producto.presentaciones.all().delete()
                for datos in nuevas:
                    PresentacionProducto.objects.create(producto=producto, **datos)

            messages.success(request, f"✅ Presentaciones de {producto.nombre} guardadas.")

        except Exception as e:
            messages.error(request, f"❌ Error al guardar presentaciones: {e}")

    next_url = request.POST.get('next') or request.GET.get('next')
    if next_url:
        return redirect(next_url)
    return redirect("producto:producto_lista")


def presentaciones_json(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    data     = list(producto.presentaciones.values("id", "nombre", "unidades", "precio", "cantidad"))
    return JsonResponse({"presentaciones": data, "producto": producto.nombre})


# ===============================
# AGENDA
# ===============================
def agenda_lista(request):
    form = AgendaInventarioForm()
    if request.method == "POST":
        form = AgendaInventarioForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "✅ Agenda registrada correctamente.")
            return redirect("producto:agenda_lista")
        else:
            messages.error(request, "⚠️ Revisa los campos del formulario.")
    agendas = AgendaInventario.objects.all()
    return render(request, "agenda.html", {"form": form, "agendas": agendas})


def agenda_eliminar(request, pk):
    agenda = get_object_or_404(AgendaInventario, pk=pk)
    if request.method == "POST":
        agenda.delete()
        messages.success(request, "✅ Agenda eliminada.")
    return redirect("producto:agenda_lista")


# ===============================
# CATEGORÍA
# ===============================
def categoria_crear(request):
    if request.method == "POST":
        nombre      = request.POST.get("nombre")
        codigo      = request.POST.get("codigo")
        descripcion = request.POST.get("descripcion")
        if Categoria.objects.filter(codigo=codigo).exists():
            messages.error(request, f"⚠️ Ya existe una categoría con el código '{codigo}'.")
        else:
            Categoria.objects.create(nombre=nombre, codigo=codigo, descripcion=descripcion)
            messages.success(request, "✅ Categoría creada correctamente.")
    return redirect("producto:producto_lista")


# ===============================
# REGISTRO (vista standalone, opcional)
# ===============================
def producto_registro(request):
    form = ProductoRegistroForm()
    if request.method == "POST":
        form = ProductoRegistroForm(request.POST)
        if form.is_valid():
            producto = form.save(commit=False)
            producto.cantidad_disponible = 0
            producto.save()
            messages.success(request, "✅ Producto registrado correctamente.")
            return redirect("producto:producto_registro")
        else:
            messages.error(request, "⚠️ Revisa los campos del formulario.")
    return render(request, "producto_registro.html", {"form": form})


# ===============================
# STOCK STATUS (API)
# ===============================
def stock_status(request):
    productos = Producto.objects.prefetch_related('presentaciones').all()

    criticos = []
    bajos    = []

    for p in productos:
        stock_presentaciones = p.presentaciones.aggregate(total=Sum('cantidad'))['total'] or 0
        stock_total          = p.cantidad_disponible + stock_presentaciones

        if stock_total == 0:
            criticos.append({"nombre": p.nombre, "cantidad": stock_total})
        elif stock_total <= 10:
            bajos.append({"nombre": p.nombre, "cantidad": stock_total})

    if criticos:
        estado = "rojo"
    elif bajos:
        estado = "amarillo"
    else:
        estado = "verde"

    response = JsonResponse({
        "estado":        estado,
        "criticos":      criticos,
        "bajos":         bajos,
        "total_alertas": len(criticos) + len(bajos),
    })
    response['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response['Pragma']        = 'no-cache'
    return response


# ===============================
# SALIDA DE PRODUCTOS
# ===============================
def producto_salida(request):
    if request.method == "POST":
        producto_id     = request.POST.get("producto")
        presentacion_id = request.POST.get("presentacion")
        cantidad_raw    = request.POST.get("cantidad", "")
        motivo          = request.POST.get("motivo", "").strip()

        try:
            cantidad = int(cantidad_raw)
            if cantidad <= 0:
                raise ValueError
        except (ValueError, TypeError):
            messages.error(request, "⚠️ La cantidad debe ser un número entero mayor a cero.")
            return redirect("producto:producto_lista")

        if not motivo:
            messages.error(request, "⚠️ Debes indicar el motivo de la salida.")
            return redirect("producto:producto_lista")

        producto = get_object_or_404(Producto, pk=producto_id)

        if presentacion_id:
            presentacion = get_object_or_404(PresentacionProducto, pk=presentacion_id, producto=producto)
            if cantidad > presentacion.cantidad:
                messages.error(
                    request,
                    f"⚠️ Stock insuficiente: solo hay {presentacion.cantidad} "
                    f"unidades de '{presentacion.nombre}' de {producto.nombre}."
                )
                return redirect("producto:producto_lista")
            presentacion.cantidad -= cantidad
            presentacion.save()
            Inventario.objects.create(
                producto=producto, tipo='salida',
                cantidad=cantidad * presentacion.unidades,
                motivo=motivo, ubicacion='Salida manual',
            )
            messages.success(
                request,
                f"✅ Salida registrada: {cantidad} × '{presentacion.nombre}' de {producto.nombre}. Motivo: {motivo}."
            )
        else:
            if cantidad > producto.cantidad_disponible:
                messages.error(
                    request,
                    f"⚠️ Stock insuficiente: solo hay {producto.cantidad_disponible} "
                    f"unidades sueltas de {producto.nombre}."
                )
                return redirect("producto:producto_lista")
            producto.cantidad_disponible -= cantidad
            producto.save()
            Inventario.objects.create(
                producto=producto, tipo='salida',
                cantidad=cantidad, motivo=motivo, ubicacion='Salida manual',
            )
            messages.success(
                request,
                f"✅ Salida registrada: {cantidad} unidades sueltas de {producto.nombre}. Motivo: {motivo}."
            )

    return redirect("producto:producto_lista")
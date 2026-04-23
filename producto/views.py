from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Sum
from .models import Producto, Categoria, Inventario, AgendaInventario, PresentacionProducto
from .forms import ProductoForm, AgendaInventarioForm, PresentacionForm, ProductoRegistroForm
from django.db import transaction


def producto_lista(request):
    categorias         = Categoria.objects.all()
    resumen_categorias = []
    for cat in categorias:
        resumen_categorias.append({
            "nombre": cat.nombre,
            "total":  cat.productos.count(),
            "pk":     cat.pk,
        })

    productos = Producto.objects.select_related("categoria").prefetch_related("presentaciones").all()

    context = {
        "productos":          productos,
        "resumen_categorias": resumen_categorias,
    }
    return render(request, "producto.html", context)


def producto_detalle(request, pk):
    producto    = get_object_or_404(Producto, pk=pk)
    movimientos = producto.movimientos.all()
    return render(request, "producto_detalle.html", {
        "producto":    producto,
        "movimientos": movimientos,
    })


# ══════════════════════════════════════════════════════
# CREAR PRODUCTO — movido desde inventario/gestion
# Vive aquí porque crear un producto es definir el catálogo,
# no una acción de stock.
# ══════════════════════════════════════════════════════
def producto_crear(request):
    """
    Crea un producto nuevo desde la página de Productos.
    Soporta petición normal y AJAX (X-Requested-With: XMLHttpRequest).
    """
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


# ══════════════════════════════════════════════════════
# EDITAR PRODUCTO — precio NO se borra si viene vacío
# ══════════════════════════════════════════════════════
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

        # ✅ Solo actualiza precio si el usuario escribió algo
        # Si viene vacío → conserva el precio que ya tenía en BD
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


# ══════════════════════════════════════════════════════
# PRESENTACIONES — precio NO se borra si viene vacío
# ══════════════════════════════════════════════════════
def presentaciones_guardar(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    if request.method == 'POST':
        nombres    = request.POST.getlist('nombre[]')
        unidades   = request.POST.getlist('unidades_base[]')
        precios    = request.POST.getlist('precio[]')
        cantidades = request.POST.getlist('cantidad[]')

        try:
            with transaction.atomic():
                # ✅ Guardar precios existentes ANTES de borrar
                # Clave: nombre de presentación → precio guardado
                precios_existentes = {
                    p.nombre: p.precio
                    for p in producto.presentaciones.all()
                }

                producto.presentaciones.all().delete()

                for n, u, precio_nuevo, c in zip(nombres, unidades, precios, cantidades):
                    n = n.strip()
                    if not n or not u:
                        continue

                    precio_raw = precio_nuevo.strip() if precio_nuevo else ''

                    if precio_raw:
                        # Usuario escribió un precio → usar ese
                        precio_final = precio_raw
                    else:
                        # Usuario dejó vacío → conservar precio anterior si existe
                        precio_final = precios_existentes.get(n, '0')

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
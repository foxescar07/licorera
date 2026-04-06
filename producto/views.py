from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Sum
from .models import Producto, Categoria, Inventario, AgendaInventario, PresentacionProducto
from .forms import ProductoForm, AgendaInventarioForm, PresentacionForm, ProductoRegistroForm


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


def producto_detalle(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    movimientos = producto.movimientos.all()
    return render(request, "producto_detalle.html", {"producto": producto, "movimientos": movimientos})


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


def presentaciones_guardar(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    if request.method == "POST":
        nombres    = request.POST.getlist("nombre[]")
        unidades   = request.POST.getlist("unidades_base[]")
        precios    = request.POST.getlist("precio[]")
        cantidades = request.POST.getlist("cantidad[]")

        producto.presentaciones.all().delete()

        for n, u, p, c in zip(nombres, unidades, precios, cantidades):
            if n and u and p:
                try:
                    PresentacionProducto.objects.create(
                        producto=producto,
                        nombre=n,
                        unidades=int(u),
                        precio=p,
                        cantidad=int(c) if c else 0
                    )
                except Exception as e:
                    print("Error creando presentación:", e)

        messages.success(request, f"✅ Presentaciones de {producto.nombre} guardadas.")
    return redirect("producto:producto_lista")


def presentaciones_json(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    data = list(producto.presentaciones.values("id", "nombre", "unidades", "precio", "cantidad"))
    return JsonResponse({"presentaciones": data, "producto": producto.nombre})


def producto_ingreso(request):
    if request.method == "POST":
        producto_id     = request.POST.get("producto")
        presentacion_id = request.POST.get("presentacion")
        cantidad_raw    = request.POST.get("cantidad", "")
        notas           = request.POST.get("notas", "")

        try:
            cantidad = int(cantidad_raw)
            if cantidad <= 0:
                raise ValueError
        except (ValueError, TypeError):
            messages.error(request, "⚠️ La cantidad debe ser un número válido.")
            return redirect("producto:producto_lista")

        producto = get_object_or_404(Producto, pk=producto_id)

        if presentacion_id:
            presentacion = get_object_or_404(PresentacionProducto, pk=presentacion_id)
            presentacion.cantidad += cantidad
            presentacion.save()
            messages.success(request, f"✅ Se agregaron {cantidad} a {presentacion.nombre} de {producto.nombre}.")
        else:
            producto.cantidad_disponible += cantidad
            producto.save()
            messages.success(request, f"✅ Se agregaron {cantidad} unidades sueltas de {producto.nombre}.")

        Inventario.objects.create(producto=producto, cantidad=cantidad, ubicacion=notas)
        return redirect("producto:producto_lista")

    return redirect("producto:producto_lista")


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
    """
    Endpoint JSON para el widget de stock en tiempo real.
    Considera tanto unidades sueltas (cantidad_disponible)
    como el stock de cada presentación.
    """
    productos = Producto.objects.prefetch_related('presentaciones').all()

    criticos = []
    bajos    = []

    for p in productos:
        # ✅ Stock total = unidades sueltas + suma de todas las presentaciones
        stock_presentaciones = p.presentaciones.aggregate(
            total=Sum('cantidad')
        )['total'] or 0

        stock_total = p.cantidad_disponible + stock_presentaciones

        if stock_total <= 2:
            criticos.append({"nombre": p.nombre, "cantidad": stock_total})
        elif stock_total <= 6:
            bajos.append({"nombre": p.nombre, "cantidad": stock_total})

    if criticos:
        estado = "rojo"
    elif bajos:
        estado = "amarillo"
    else:
        estado = "verde"

    return JsonResponse({
        "estado":        estado,
        "criticos":      criticos,
        "bajos":         bajos,
        "total_alertas": len(criticos) + len(bajos),
    })
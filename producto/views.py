from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models  import Producto, Categoria, Inventario
from .forms   import ProductoForm


# ─────────────────────────────────────────────
#  Vista principal: lista de productos
# ─────────────────────────────────────────────
def producto_lista(request):
    """
    GET  → Muestra el inventario con tarjetas por categoría y tabla.
    POST → Recibe el formulario del modal y registra un nuevo producto.
    """
    form = ProductoForm()

    if request.method == "POST":
        form = ProductoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "✅ Producto registrado correctamente.")
            return redirect("producto_lista")
        else:
            # Si hay errores, reabre el modal (se maneja en el template con JS)
            messages.error(request, "⚠️ Revisa los campos del formulario.")

    # Datos para las tarjetas de resumen por categoría
    categorias = Categoria.objects.all()
    resumen_categorias = []
    for cat in categorias:
        resumen_categorias.append({
            "nombre": cat.nombre,
            "total":  cat.productos.count(),
        })

    # Productos con stock crítico (≤ 5) para el banner de alerta
    stock_critico = Producto.objects.filter(cantidad_disponible__lte=5)

    # Todos los productos para la tabla
    productos = Producto.objects.select_related("categoria").all()

    context = {
        "form":               form,
        "productos":          productos,
        "resumen_categorias": resumen_categorias,
        "stock_critico":      stock_critico,
    }
    return render(request, "producto.html", context)


# ─────────────────────────────────────────────
#  Vista de detalle de un producto
# ─────────────────────────────────────────────
def producto_detalle(request, pk):
    """
    Muestra la información completa de un producto
    y su historial de movimientos en el inventario.
    """
    producto    = get_object_or_404(Producto, pk=pk)
    movimientos = producto.movimientos.all()

    context = {
        "producto":    producto,
        "movimientos": movimientos,
    }
    return render(request, "producto_detalle.html", context)


# ─────────────────────────────────────────────
#  Vista de edición de un producto
# ─────────────────────────────────────────────
def producto_editar(request, pk):
    """
    GET  → Muestra el formulario pre-cargado con los datos del producto.
    POST → Guarda los cambios.
    """
    producto = get_object_or_404(Producto, pk=pk)

    if request.method == "POST":
        form = ProductoForm(request.POST, instance=producto)
        if form.is_valid():
            form.save()
            messages.success(request, "✅ Producto actualizado correctamente.")
            return redirect("producto_lista")
    else:
        form = ProductoForm(instance=producto)

    return render(request, "producto_editar.html", {
        "form":     form,
        "producto": producto,
    })
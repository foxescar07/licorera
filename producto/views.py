from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models  import Producto, Categoria, Inventario
from .forms   import ProductoForm




def producto_lista(request):
    form = ProductoForm()

    if request.method == "POST":
        form = ProductoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "✅ Producto registrado correctamente.")
            # 2. CAMBIO: Agregamos "producto:" al redirect para que use el namespace
            return redirect("producto:producto_lista") 
        else:
            messages.error(request, "⚠️ Revisa los campos del formulario.")

    categorias = Categoria.objects.all()
    resumen_categorias = []
    for cat in categorias:
        resumen_categorias.append({
            "nombre": cat.nombre,
            "total":  cat.productos.count(),
        })

    stock_critico = Producto.objects.filter(cantidad_disponible__lte=5)
    productos = Producto.objects.select_related("categoria").all()

    context = {
        "form":               form,
        "productos":          productos,
        "resumen_categorias": resumen_categorias,
        "stock_critico":      stock_critico,
    }
    return render(request, "producto.html", context)

def producto_detalle(request, pk):
    producto    = get_object_or_404(Producto, pk=pk)
    movimientos = producto.movimientos.all()

    context = {
        "producto":    producto,
        "movimientos": movimientos,
    }
    return render(request, "producto_detalle.html", context)

def producto_editar(request, pk):
    producto = get_object_or_404(Producto, pk=pk)

    if request.method == "POST":
        form = ProductoForm(request.POST, instance=producto)
        if form.is_valid():
            form.save()
            messages.success(request, "✅ Producto actualizado correctamente.")
            # 3. CAMBIO: Agregamos "producto:" aquí también
            return redirect("producto:producto_lista") 
    else:
        form = ProductoForm(instance=producto)

    return render(request, "producto_editar.html", {
        "form":     form,
        "producto": producto,
    })
    
from .models  import Producto, Categoria, Inventario, AgendaInventario
from .forms   import ProductoForm, AgendaInventarioForm

def agenda_lista(request):
    """Lista todas las agendas y permite crear una nueva."""
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
    return render(request, "agenda.html", {
        "form":    form,
        "agendas": agendas,
    })


def agenda_eliminar(request, pk):
    """Elimina una agenda."""
    agenda = get_object_or_404(AgendaInventario, pk=pk)
    if request.method == "POST":
        agenda.delete()
        messages.success(request, "✅ Agenda eliminada.")
    return redirect("producto:agenda_lista")
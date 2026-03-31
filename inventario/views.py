from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from producto.models import Producto, AgendaInventario
from .models import ConteoProducto, SesionConteo


def inventario_home(request):
    agendas = AgendaInventario.objects.all()
    if request.method == 'POST':
        AgendaInventario.objects.create(
            titulo=request.POST.get('titulo'),
            descripcion=request.POST.get('descripcion', ''),
            fecha_programada=request.POST.get('fecha_programada'),
        )
        messages.success(request, '✅ Inventario agendado correctamente.')
        return redirect('inventario:inventario_home')
    return render(request, 'inventario/inventario_home.html', {'agendas': agendas})


def agenda_cambiar_estado(request, pk):
    agenda = get_object_or_404(AgendaInventario, pk=pk)
    nuevo_estado = request.POST.get('estado')
    if nuevo_estado in dict(AgendaInventario.ESTADO_CHOICES):
        agenda.estado = nuevo_estado
        agenda.save()
    return redirect('inventario:inventario_home')


def conteo_inventario(request):
    productos = Producto.objects.select_related('categoria').all()
    sesion = SesionConteo.objects.filter(activa=True).first()
    if request.method == 'POST' and 'iniciar_sesion' in request.POST:
        SesionConteo.objects.filter(activa=True).update(activa=False)
        sesion = SesionConteo.objects.create(activa=True)
        messages.success(request, '✅ Nueva sesión de conteo iniciada.')
        return redirect('inventario:conteo_inventario')
    conteos = ConteoProducto.objects.filter(sesion=sesion) if sesion else []
    return render(request, 'inventario/conteo_inventario.html', {
        'productos': productos,
        'sesion': sesion,
        'conteos': conteos,
    })


def guardar_conteo(request):
    if request.method == 'POST':
        sesion   = get_object_or_404(SesionConteo, pk=request.POST.get('sesion_id'))
        producto = get_object_or_404(Producto, pk=request.POST.get('producto_id'))
        ConteoProducto.objects.update_or_create(
            sesion=sesion, producto=producto,
            defaults={'cantidad_contada': request.POST.get('cantidad_contada')}
        )
        messages.success(request, f'✅ Conteo de {producto.nombre} guardado.')
    return redirect('inventario:conteo_inventario')


def comparar_inventario(request):
    sesion = SesionConteo.objects.filter(activa=True).first()
    discrepancias = []
    if sesion:
        for c in ConteoProducto.objects.filter(sesion=sesion).select_related('producto'):
            diff = c.cantidad_contada - c.producto.cantidad_disponible
            discrepancias.append({
                'producto':   c.producto,
                'en_sistema': c.producto.cantidad_disponible,
                'fisico':     c.cantidad_contada,
                'diferencia': diff,
                'estado':     'ok' if diff == 0 else ('sobrante' if diff > 0 else 'faltante'),
            })
    return render(request, 'inventario/comparar_inventario.html', {
        'discrepancias': discrepancias,
        'sesion': sesion,
    })
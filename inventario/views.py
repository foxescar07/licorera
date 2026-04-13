from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from producto.models import Producto, AgendaInventario
from .models import ConteoProducto, SesionConteo


def inventario_home(request):
    agendas = AgendaInventario.objects.all()
    sesion = SesionConteo.objects.filter(activa=True).first()

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

    if request.method == 'POST':
        AgendaInventario.objects.create(
            titulo=request.POST.get('titulo'),
            descripcion=request.POST.get('descripcion', ''),
            fecha_programada=request.POST.get('fecha_programada'),
        )
        messages.success(request, '✅ Inventario agendado correctamente.')
        return redirect('inventario:inventario_home')

    return render(request, 'inventario/inventario_home.html', {
        'agendas': agendas,
        'sesion': sesion,
        'productos': productos,
        'conteos': conteos,
        'discrepancias': discrepancias,
        'categoria_activa': categoria_id,
    })


def agenda_cambiar_estado(request, pk):
    agenda = get_object_or_404(AgendaInventario, pk=pk)
    nuevo_estado = request.POST.get('estado')
    if nuevo_estado in dict(AgendaInventario.ESTADO_CHOICES):
        agenda.estado = nuevo_estado
        agenda.save()
    return redirect('inventario:inventario_home')


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
        SesionConteo.objects.create(activa=True)
        messages.success(request, '✅ Nueva sesión de conteo iniciada.')
    return redirect('inventario:inventario_home')
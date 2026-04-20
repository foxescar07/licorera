from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from producto.models import Producto, AgendaInventario
from .models import ConteoProducto, SesionConteo, ConteoProducto
from django.utils import timezone
from django.db import models as db_models
from django.http import JsonResponse


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

    productos_con_codigo = productos.exclude(codigo='').exclude(codigo__isnull=True).count()
    productos_sin_codigo = productos.filter(codigo='').count() + productos.filter(codigo__isnull=True).count()

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
        'con_codigo': productos_con_codigo,  
        'sin_codigo': productos_sin_codigo,   
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

def ajustar_inventario(request, pk):
    """SCRUM-95, 97, 100 — Modifica, guarda y actualiza el stock real del producto."""
    if request.method == 'POST':
        producto = get_object_or_404(Producto, pk=pk)
        nueva_cantidad = request.POST.get('nueva_cantidad')

        if nueva_cantidad is not None:
            producto.cantidad_disponible = int(nueva_cantidad)
            producto.save()
            messages.success(request, f'✅ Stock de {producto.nombre} actualizado a {nueva_cantidad}.')
        else:
            messages.error(request, '❌ Cantidad inválida.')

    return redirect('inventario:inventario_home')

from .models import ConteoProducto, SesionConteo, ResultadoInventario 

def finalizar_inventario(request):
    if request.method == 'POST':
        # ✅ Usa activa=True, no estado='activa'
        sesion = SesionConteo.objects.filter(activa=True).first()
        if sesion:
            conteos = sesion.conteos.select_related('producto')
            for conteo in conteos:
                ResultadoInventario.objects.update_or_create(
                    sesion=sesion,
                    producto=conteo.producto,
                    defaults={
                        'cantidad_sistema': conteo.producto.cantidad_disponible,
                        'cantidad_fisica':  conteo.cantidad_contada,
                        'diferencia':       conteo.cantidad_contada - conteo.producto.cantidad_disponible,
                    }
                )
            # ✅ Marca como inactiva Y como finalizada
            sesion.activa = False
            sesion.estado = 'finalizada'
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

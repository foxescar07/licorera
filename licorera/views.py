from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.db.models import Count, Sum
from django.utils import timezone
from datetime import timedelta

from producto.models import Categoria, Inventario
from ventas.models import Venta


# ── helpers de acceso por rol ─────────────────────────────
def _verificar_sesion(request):
    return bool(request.session.get('usuario_id'))

def _solo_admin(request):
    return request.session.get('usuario_rol') == 'admin'

def _admin_o_cajero(request):
    return request.session.get('usuario_rol') in ('admin', 'cajero')

def _sin_acceso(request, mensaje='No tienes permiso para acceder a esta sección.'):
    request.session['acceso_denegado'] = mensaje
    return redirect('home')


# ── vistas ────────────────────────────────────────────────
def home(request):
    if not _verificar_sesion(request):
        return redirect('login')

    # ── Categorías ──
    categorias_qs = Categoria.objects.annotate(total=Count('productos'))
    categorias = [
        {"nombre": c.nombre, "total": c.total if c.total else 0}
        for c in categorias_qs
    ]
    grupos_categorias = [categorias[i:i+6] for i in range(0, len(categorias), 6)]

    # ── Movimientos recientes ──
    movimientos = Inventario.objects.select_related('producto').all()[:10]

    # ── Últimos 7 días rodantes ──
    DIAS_ES = ['Dom', 'Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb']
    hoy = timezone.localtime(timezone.now()).date()

    labels, data, data_count = [], [], []
    for i in range(6, -1, -1):
        dia = hoy - timedelta(days=i)
        nombre_dia = DIAS_ES[dia.isoweekday() % 7]
        labels.append(f"{nombre_dia} {dia.day}/{dia.month}")

        ventas_dia = Venta.objects.filter(fecha__date=dia).aggregate(
            total=Sum('total_con_descuento'),
            cantidad=Count('id')
        )
        data.append(float(ventas_dia['total'] or 0))
        data_count.append(ventas_dia['cantidad'] or 0)

    # ── Métricas de resumen ──
    total_hoy      = data[-1]
    ventas_hoy_num = data_count[-1]
    prom_diario    = round(sum(data[:6]) / 6) if any(data[:6]) else 0
    mejor_idx      = data[:6].index(max(data[:6])) if any(d > 0 for d in data[:6]) else 0
    mejor_dia      = labels[mejor_idx]
    mejor_dia_val  = data[mejor_idx]

    acceso_denegado = request.session.pop('acceso_denegado', None)

    return render(request, 'home.html', {
        'titulo':            'Home',
        'grupos_categorias': grupos_categorias,
        'movimientos':       movimientos,
        'labels':            labels,
        'data':              data,
        'data_count':        data_count,
        'total_hoy':         total_hoy,
        'ventas_hoy_num':    ventas_hoy_num,
        'prom_diario':       prom_diario,
        'mejor_dia':         mejor_dia,
        'mejor_dia_val':     mejor_dia_val,
        'acceso_denegado':   acceso_denegado,
    })


def categorias_json(request):
    if not _verificar_sesion(request):
        return JsonResponse({'error': 'Sin sesión.'}, status=401)

    categorias_qs = Categoria.objects.annotate(total=Count('productos'))
    categorias = [
        {"nombre": c.nombre, "total": c.total if c.total else 0}
        for c in categorias_qs
    ]
    return JsonResponse({"categorias": categorias})


def usuario(request):
    if not _verificar_sesion(request):
        return redirect('login')
    if not _admin_o_cajero(request):
        return _sin_acceso(request)
    return render(request, 'usuario.html')


def dashboard(request):
    if not _verificar_sesion(request):
        return redirect('login')
    return render(request, 'dashboard.html')


def proveedores(request):
    if not _verificar_sesion(request):
        return redirect('login')
    return render(request, 'proveedor.html')


def reportes(request):
    if not _verificar_sesion(request):
        return redirect('login')
    return render(request, 'reportes.html')
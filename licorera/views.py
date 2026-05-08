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
DIAS_ES   = ['Dom', 'Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb']
MESES_ES  = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun',
             'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic']


def _semana_lun_dom(offset=0):
    hoy   = timezone.localtime(timezone.now()).date()
    lunes = hoy - timedelta(days=hoy.weekday()) - timedelta(weeks=offset)
    return lunes, lunes + timedelta(days=6)


def _datos_semana(lunes):
    labels, data, data_count = [], [], []
    for i in range(7):
        dia = lunes + timedelta(days=i)
        labels.append(f"{DIAS_ES[dia.isoweekday() % 7]} {dia.day}/{dia.month}")
        agg = Venta.objects.filter(fecha__date=dia).aggregate(
            total=Sum('total_con_descuento'), cantidad=Count('id')
        )
        data.append(float(agg['total'] or 0))
        data_count.append(int(agg['cantidad'] or 0))
    return labels, data, data_count


def home(request):
    if not _verificar_sesion(request):
        return redirect('login')

    categorias_qs     = Categoria.objects.annotate(total=Count('productos'))
    categorias        = [{"nombre": c.nombre, "total": c.total or 0} for c in categorias_qs]
    grupos_categorias = [categorias[i:i+6] for i in range(0, len(categorias), 6)]
    movimientos       = Inventario.objects.select_related('producto').all()[:10]

    lunes, domingo        = _semana_lun_dom(offset=0)
    labels, data, data_count = _datos_semana(lunes)

    hoy            = timezone.localtime(timezone.now()).date()
    total_hoy      = float(Venta.objects.filter(fecha__date=hoy)
                           .aggregate(t=Sum('total_con_descuento'))['t'] or 0)
    ventas_hoy_num = Venta.objects.filter(fecha__date=hoy).count()

    vals_pasados   = [v for v, d in zip(data, [lunes + timedelta(days=i) for i in range(7)]) if d <= hoy]
    prom_diario    = round(sum(vals_pasados) / len(vals_pasados)) if vals_pasados else 0

    max_val        = max(data) if any(data) else 0
    mejor_idx      = data.index(max_val) if max_val else 0
    semana_label   = f"{lunes.day}/{lunes.month} – {domingo.day}/{domingo.month}/{domingo.year}"
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
        'mejor_dia':         labels[mejor_idx],
        'mejor_dia_val':     max_val,
        'semana_label':      semana_label,
        'acceso_denegado':   acceso_denegado,
    })

def semana_json(request):
    if not _verificar_sesion(request):
        return JsonResponse({'error': 'Sin sesión.'}, status=401)
    try:
        offset = max(0, int(request.GET.get('offset', 0)))
    except (ValueError, TypeError):
        offset = 0

    lunes, domingo       = _semana_lun_dom(offset)
    labels, data, counts = _datos_semana(lunes)
    hoy                  = timezone.localtime(timezone.now()).date()

    # ── total_hoy y ventas_hoy_num (solo tienen sentido en la semana actual) ──
    if offset == 0:
        total_hoy      = float(Venta.objects.filter(fecha__date=hoy)
                               .aggregate(t=Sum('total_con_descuento'))['t'] or 0)
        ventas_hoy_num = Venta.objects.filter(fecha__date=hoy).count()
    else:
        total_hoy      = None
        ventas_hoy_num = None

    # ── promedio diario: igual que en home(), solo días con fecha <= hoy ──
    dias_semana  = [lunes + timedelta(days=i) for i in range(7)]
    vals_pasados = [v for v, d in zip(data, dias_semana) if d <= hoy]
    prom_diario  = round(sum(vals_pasados) / len(vals_pasados)) if vals_pasados else 0

    # ── mejor día ──
    max_val    = max(data) if any(data) else 0
    mejor_idx  = data.index(max_val) if max_val else 0

    return JsonResponse({
        'offset':          offset,
        'semana_label':    f"{lunes.day}/{lunes.month} – {domingo.day}/{domingo.month}/{domingo.year}",
        'labels':          labels,
        'data':            data,
        'data_count':      counts,
        'es_actual':       offset == 0,
        'total_hoy':       total_hoy,       # ← agregado
        'ventas_hoy_num':  ventas_hoy_num,  # ← agregado
        'prom_diario':     prom_diario,     # ← agregado
        'mejor_dia':       labels[mejor_idx],  # ← agregado
        'mejor_dia_val':   max_val,            # ← agregado
    })

def meses_json(request):
    if not _verificar_sesion(request):
        return JsonResponse({'error': 'Sin sesión.'}, status=401)
    from datetime import date
    hoy = timezone.localtime(timezone.now()).date()
    labels, data, counts = [], [], []

    # Solo desde enero del año actual hasta el mes actual, en orden
    for mes in range(1, hoy.month + 1):
        anio     = hoy.year
        primer   = date(anio, mes, 1)
        if mes == 12:
            ultimo = date(anio + 1, 1, 1) - timedelta(days=1)
        else:
            ultimo = date(anio, mes + 1, 1) - timedelta(days=1)

        agg = Venta.objects.filter(
            fecha__date__gte=primer,
            fecha__date__lte=ultimo,
        ).aggregate(total=Sum('total_con_descuento'), cantidad=Count('id'))

        labels.append(MESES_ES[mes - 1])
        data.append(float(agg['total'] or 0))
        counts.append(int(agg['cantidad'] or 0))

    return JsonResponse({'labels': labels, 'data': data, 'data_count': counts})
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
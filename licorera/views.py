from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.db.models import Sum
from producto.models import Categoria, Inventario


# ── helper de acceso por rol ──────────────────────────────
def _verificar_sesion(request):
    """Devuelve True si hay sesión activa."""
    return bool(request.session.get('usuario_id'))

def _solo_admin(request):
    return request.session.get('usuario_rol') == 'admin'

def _admin_o_cajero(request):
    return request.session.get('usuario_rol') in ('admin', 'cajero')

def _sin_acceso(request, mensaje='No tienes permiso para acceder a esta sección.'):
    """Redirige al home con mensaje de error embebido en sesión."""
    request.session['acceso_denegado'] = mensaje
    return redirect('home')


# ── vistas ────────────────────────────────────────────────
def home(request):
    if not _verificar_sesion(request):
        return redirect('login')

    categorias_qs = Categoria.objects.annotate(
        total=Sum('productos__cantidad_disponible')
    )
    categorias = [
        {"nombre": c.nombre, "total": c.total if c.total else 0}
        for c in categorias_qs
    ]
    grupos_categorias = [categorias[i:i+6] for i in range(0, len(categorias), 6)]
    movimientos = Inventario.objects.select_related('producto').all()[:10]

    # Tomar y limpiar el mensaje de acceso denegado si existe
    acceso_denegado = request.session.pop('acceso_denegado', None)

    context = {
        'titulo': 'Home',
        'grupos_categorias': grupos_categorias,
        'movimientos': movimientos,
        'labels': [],
        'data': [],
        'acceso_denegado': acceso_denegado,
    }
    return render(request, 'home.html', context)


def categorias_json(request):
    if not _verificar_sesion(request):
        return JsonResponse({'error': 'Sin sesión.'}, status=401)

    categorias_qs = Categoria.objects.annotate(
        total=Sum('productos__cantidad_disponible')
    )
    categorias = [
        {"nombre": c.nombre, "total": c.total if c.total else 0}
        for c in categorias_qs
    ]
    return JsonResponse({"categorias": categorias})


def usuario(request):
    # Solo admin y cajero pueden ver la lista
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
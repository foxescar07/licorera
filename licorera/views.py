from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Sum
from producto.models import Categoria, Inventario
from reportes.models import Venta
from datetime import datetime, timedelta

def home(request):
    # 1. LÓGICA DE LOGIN
    if request.method == 'POST':
        accion = request.POST.get('accion')
        if accion == 'login':
            usuario = request.POST.get('usuario_input')
            clave = request.POST.get('clave_input')

            if usuario == 'luna' and clave == '555':
                # Si los datos son correctos, permitimos que pase a la lógica del tablero
                pass 
            else:
                messages.error(request, "Usuario o contraseña incorrectos")
                return render(request, 'usuario.html')
        else:
            return render(request, 'usuario.html')
    else:
        # Si no han enviado el formulario, mostrar el diseño beige
        return render(request, 'usuario.html')

    # 2. LÓGICA DEL TABLERO (Solo corre si el login fue exitoso)
    
    # Categorías con total de productos
    categorias_qs = Categoria.objects.annotate(
        total=Sum('productos__cantidad_disponible')
    )

    categorias = [
        {"nombre": c.nombre, "total": c.total if c.total else 0}
        for c in categorias_qs
    ]

    grupos_categorias = [
        categorias[i:i+6] for i in range(0, len(categorias), 6)
    ]

    # Movimientos recientes
    movimientos = Inventario.objects.select_related('producto').all()[:10]

    # --- ARREGLO PARA LA GRÁFICA (Sin usar el campo 'fecha') ---
    hoy = datetime.today()
    labels = []
    data = []

    # Obtenemos el total general de ventas ya que no podemos filtrar por fecha aún
    total_ventas_general = Venta.objects.aggregate(total=Sum('cantidad'))['total'] or 0

    for i in range(6, -1, -1):
        dia = hoy - timedelta(days=i)
        labels.append(dia.strftime("%d/%m"))
        # Llenamos con 0 los días anteriores y el total en el último día para que la gráfica cargue
        if i == 0:
            data.append(total_ventas_general)
        else:
            data.append(0)

    context = {
        'nombre': 'Luna',
        'titulo': 'Panel de Control',
        'grupos_categorias': grupos_categorias,
        'movimientos': movimientos,
        'labels': labels,
        'data': data,
    }

    # Cargamos el tablero azul (home.html)
    return render(request, 'home.html', context)

# --- Funciones adicionales ---

def categorias_json(request):
    categorias_qs = Categoria.objects.annotate(
        total=Sum('productos__cantidad_disponible')
    )
    categorias = [
        {"nombre": c.nombre, "total": c.total if c.total else 0}
        for c in categorias_qs
    ]
    return JsonResponse({"categorias": categorias})

def proveedores(request):
    return render(request, 'proveedor.html')

def reportes(request):
    return render(request, 'reportes.html')

def prueba(request):
    return render(request, 'prueba.html')

def dashboard(request):
    return render(request, 'dashboard.html')
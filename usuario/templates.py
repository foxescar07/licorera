{% load static %}
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CYS - Gestión Licorera</title>
    
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css2?family=Rajdhani:wght@500;700&family=Inter:wght@400;500&display=swap" rel="stylesheet">

    <style>
        /* ============================================================
           CSS INTEGRADO - DISEÑO CYS FUTURISTA
           ============================================================ */
        :root {
            --fondo-beige: #E8C898;
            --fondo-card: #f1e9dc;
            --rojo-cys: #B7372A;
            --rojo-glow: rgba(183, 55, 42, 0.3);
            --trans: all .22s ease;
        }

        body {
            background-color: var(--fondo-beige);
            font-family: 'Inter', sans-serif;
            min-height: 100vh;
        }

        /* Botones Superiores e Inferiores */
        .btn-cys {
            background-color: var(--rojo-cys) !important;
            color: white !important;
            border-radius: 15px !important;
            font-family: 'Rajdhani', sans-serif !important;
            font-weight: 700 !important;
            letter-spacing: 1px;
            border: none !important;
            transition: var(--trans) !important;
            box-shadow: 0 4px 12px var(--rojo-glow) !important;
            text-transform: uppercase;
        }

        .btn-cys:hover {
            transform: translateY(-2px) scale(1.02);
            box-shadow: 0 6px 18px rgba(183, 55, 42, 0.5) !important;
            filter: brightness(1.1);
        }

        /* Tarjeta Principal */
        .card-cys {
            background-color: var(--fondo-card);
            width: 100%;
            max-width: 420px;
            border-radius: 25px;
            border: none;
            box-shadow: 0 15px 35px rgba(0,0,0,0.1);
            transition: var(--trans);
        }

        /* Logo con Brillo */
        .logo-cys {
            width: 110px;
            height: 110px;
            object-fit: cover;
            border-radius: 50%;
            border: 3px solid var(--rojo-cys);
            box-shadow: 0 0 20px var(--rojo-glow);
        }

        /* Títulos */
        .titulo-cys {
            font-family: 'Rajdhani', sans-serif;
            font-weight: 700;
            color: var(--rojo-cys);
            letter-spacing: 2px;
        }

        /* Inputs */
        .form-control, .form-select {
            border-radius: 12px !important;
            border: 1px solid rgba(0,0,0,0.05) !important;
            padding: 10px !important;
            font-size: 0.9rem;
        }

        .form-control:focus {
            border-color: var(--rojo-cys) !important;
            box-shadow: 0 0 0 3px var(--rojo-glow) !important;
        }

        .btn-link-cys {
            color: var(--rojo-cys) !important;
            font-family: 'Rajdhani', sans-serif;
            font-weight: 700;
            text-decoration: none;
            text-transform: uppercase;
            font-size: 0.8rem;
        }
    </style>
</head>
<body class="d-flex flex-column min-vh-100">

    <div class="container-fluid d-flex justify-content-between p-4">
        <button class="btn btn-cys px-4" data-bs-toggle="collapse" data-bs-target="#seccionRecuperar">
            Olvidé mi contraseña
        </button>
        
        <button class="btn btn-cys px-4" data-bs-toggle="collapse" data-bs-target="#seccionRegistro">
            Crear cuenta
        </button>
    </div>

    <div class="flex-grow-1 d-flex flex-column align-items-center justify-content-center" style="margin-top: -40px;">
        
        <div class="card card-cys p-5 text-center" id="contenedorPrincipal">
            
            <div class="mb-4">
                <img src="{% static 'img/logo.jpeg' %}" alt="Logo CYS" class="logo-cys">
            </div>

            {% if messages %}
                {% for message in messages %}
                <div class="alert alert-danger py-2 small mb-3" style="border-radius: 12px;">
                    {{ message }}
                </div>
                {% endfor %}
            {% endif %}

            <div class="collapse show" id="seccionLogin" data-bs-parent="#contenedorPrincipal">
                <h2 class="titulo-cys mb-4 display-6">CYS</h2>
                
                <form method="POST">
                    {% csrf_token %}
                    <input type="hidden" name="accion" value="login">
                    <div class="mb-3">
                        <input type="text" name="usuario_input" class="form-control text-center" placeholder="Usuario" required>
                    </div>
                    <div class="mb-4">
                        <input type="password" name="clave_input" class="form-control text-center" placeholder="Contraseña" required>
                    </div>
                    <button type="submit" class="btn btn-cys w-100 py-2">ENTRAR</button>
                </form>
            </div>

            <div class="collapse" id="seccionRegistro" data-bs-parent="#contenedorPrincipal">
                <h3 class="titulo-cys mb-3 h4">NUEVO USUARIO</h3>
                <form method="POST">
                    {% csrf_token %}
                    <input type="hidden" name="accion" value="registrar">
                    <input type="text" name="nombre_input" class="form-control mb-2 text-center" placeholder="Nombre completo" required>
                    <input type="text" name="user_nuevo" class="form-control mb-2 text-center" placeholder="Usuario" required>
                    <input type="password" name="pass_nueva" class="form-control mb-3 text-center" placeholder="Contraseña" required>
                    
                    <select name="rol_nuevo" class="form-select mb-3 text-center">
                        <option value="empleado">Empleado</option>
                        <option value="admin">Administrador</option>
                    </select>
                    
                    <button type="submit" class="btn btn-cys w-100 py-2">GUARDAR</button>
                </form>
                <button class="btn btn-link-cys mt-3" data-bs-toggle="collapse" data-bs-target="#seccionLogin">Volver</button>
            </div>

            <div class="collapse" id="seccionRecuperar" data-bs-parent="#contenedorPrincipal">
                <h3 class="titulo-cys mb-3 h4">RECUPERAR</h3>
                <form method="POST">
{% csrf_token %}
                    <input type="hidden" name="accion" value="recuperar">
                    <input type="text" name="user_recuperar" class="form-control mb-4 text-center" placeholder="Ingresa tu Usuario" required>
                    <button type="submit" class="btn btn-cys w-100 py-2">ENVIAR SOLICITUD</button>
                </form>
                <button class="btn btn-link-cys mt-3" data-bs-toggle="collapse" data-bs-target="#seccionLogin">Volver</button>
            </div>

        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
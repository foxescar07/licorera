from django.db import models

class Usuario(models.Model):
    ROLES = [
        ('admin', 'Administrador'),
        ('empleado', 'Empleado'),
    ]
    
    identificacion = models.CharField(max_length=20, unique=True)
    nombre_completo = models.CharField(max_length=100)
    usuario = models.CharField(max_length=50, unique=True)
    clave = models.CharField(max_length=50)
    rol = models.CharField(max_length=10, choices=ROLES, default='empleado')
    fecha_registro = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nombre_completo} ({self.rol})"
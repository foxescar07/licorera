from django.db import models
from django.utils import timezone
 
 
class Usuario(models.Model):
    ROL_CHOICES = [
        ('admin',    'Administrador'),
        ('cajero',   'Cajero'),
        ('empleado', 'Empleado'),
    ]
 
    TIPO_ID_CHOICES = [
        ('CC',  'Cédula de Ciudadanía'),
        ('CE',  'Cédula de Extranjería'),
        ('TI',  'Tarjeta de Identidad'),
        ('PA',  'Pasaporte'),
        ('PT',  'Permiso de Permanencia Temporal'),
    ]
 
    tipo_id          = models.CharField(max_length=5, choices=TIPO_ID_CHOICES, default='CC')
    identificacion   = models.CharField(max_length=20, unique=True)
    nombre           = models.CharField(max_length=100)
    apellidos        = models.CharField(max_length=100)
    email            = models.EmailField(unique=True, blank=True, null=True)
    telefono         = models.CharField(max_length=15, blank=True, null=True)
    usuario          = models.CharField(max_length=50, unique=True)
    clave            = models.CharField(max_length=128)
    rol              = models.CharField(max_length=20, choices=ROL_CHOICES, default='empleado')
    activo           = models.BooleanField(default=True)
    fecha_registro   = models.DateTimeField(auto_now_add=True)
    reset_token      = models.CharField(max_length=64, blank=True, null=True)
    reset_token_expira = models.DateTimeField(blank=True, null=True)
 
    class Meta:
        verbose_name        = "Usuario"
        verbose_name_plural = "Usuarios"
        ordering            = ["-fecha_registro"]
 
    def __str__(self):
        return f"{self.nombre} {self.apellidos} ({self.get_rol_display()})"
 
    @property
    def nombre_completo(self):
        return f"{self.nombre} {self.apellidos}"
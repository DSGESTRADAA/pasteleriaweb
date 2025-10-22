# core/models.py

from django.db import models
from django.contrib.auth.models import User


class PerfilEmpleado(models.Model):
    """Modelo para almacenar información adicional del empleado."""
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    # Campos adicionales requeridos:
    fecha_nacimiento = models.DateField(null=True, blank=True)
    numero_telefono = models.CharField(max_length=15, null=True, blank=True)

    def __str__(self):
        return f'Perfil de {self.user.username}'


from django.db import models

# Create your models here.

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


# -------------------------------------------------------------------------
# Modelo de Extensión del Usuario (ya lo tenías, ajustado ligeramente)
# -------------------------------------------------------------------------
class PerfilEmpleado(models.Model):
    """Modelo para almacenar información adicional del empleado/usuario."""
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    # Campos adicionales que coinciden con tu diagrama:
    fecha_nacimiento = models.DateField(null=True, blank=True)
    numero_telefono = models.CharField(max_length=15, null=True, blank=True)

    # El campo 'rol' de tu diagrama (si aplica a todos los usuarios)
    ROL_CHOICES = [
        ('cliente', 'Cliente'),
        ('administrador', 'Administrador'),
        ('repartidor', 'Repartidor'),
    ]
    rol = models.CharField(max_length=20, choices=ROL_CHOICES, default='cliente')

    def __str__(self):
        return f'Perfil de {self.user.username} ({self.rol})'


# -------------------------------------------------------------------------
# Modelos de Productos, Promociones y Pedidos
# -------------------------------------------------------------------------

class Producto(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    tamano = models.CharField(max_length=50, blank=True, null=True)
    stock = models.IntegerField(default=0)
    # ¡Importante! Aquí está el campo de la imagen
    imagen = models.ImageField(upload_to='productos/', blank=True, null=True)

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name_plural = "Productos"


class Promocion(models.Model):

    id = models.AutoField(primary_key=True)
    titulo = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)
    # Usamos DecimalField para porcentajes
    descuento = models.DecimalField(max_digits=5, decimal_places=2)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    activa = models.BooleanField(default=True)
    productos = models.ManyToManyField(
        'Producto',
        through='ProductoPromocion',
        related_name='promociones'  # Permite consultar: producto.promociones.all()
    )

    def __str__(self):
        return self.titulo

    class Meta:
        verbose_name_plural = "Promociones"


# Tabla intermedia para la relación N:M entre Producto y Promocion
class ProductoPromocion(models.Model):
    # La clave ManyToMany la gestionaremos a través de esta tabla
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    promocion = models.ForeignKey(Promocion, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.producto.nombre} en {self.promocion.titulo}"

    class Meta:
        unique_together = ('producto', 'promocion')
        verbose_name_plural = "Productos en Promoción"


class Pedido(models.Model):
    id = models.AutoField(primary_key=True)
    # Relacionado con el usuario (cliente) que realiza el pedido
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)

    # Campos del pedido (personalización del pastel/producto)
    tamano = models.CharField(max_length=50, blank=True, null=True)
    sabor_pan = models.CharField(max_length=50, blank=True, null=True)
    relleno = models.CharField(max_length=100, blank=True, null=True)
    descripcion = models.TextField(blank=True, null=True)

    # Información de estado y fechas
    fecha_pedido = models.DateTimeField(default=timezone.now)
    fecha_entrega = models.DateField(null=True, blank=True)

    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('en_preparacion', 'En Preparación'),
        ('en_entrega', 'En Entrega'),
        ('entregado', 'Entregado'),
        ('cancelado', 'Cancelado'),
    ]
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='pendiente')
    precio_establecido = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Pedido #{self.id} de {self.usuario.username}"

    class Meta:
        verbose_name_plural = "Pedidos"


class DetallePedido(models.Model):
    id = models.AutoField(primary_key=True)
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.IntegerField()
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.cantidad}x {self.producto.nombre} - Pedido #{self.pedido.id}"

    class Meta:
        verbose_name_plural = "Detalles de Pedidos"


class RespuestaPedido(models.Model):
    id = models.AutoField(primary_key=True)
    # OneToOneField: Un pedido solo puede tener una respuesta
    pedido = models.OneToOneField(Pedido, on_delete=models.CASCADE)
    cliente_acepta = models.BooleanField()
    comentario = models.TextField(blank=True, null=True)
    fecha_respuesta = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Respuesta Pedido #{self.pedido.id}"

    class Meta:
        verbose_name_plural = "Respuestas de Pedidos"


class InteraccionCliente(models.Model):

    # usuario_id INT (Relación: Un usuario puede tener muchas interacciones)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='interacciones_cliente')

    # fecha DATETIME
    fecha = models.DateTimeField(default=timezone.now)

    # tipo ENUM(...) (Usamos CharField con choices en Django)
    TIPO_INTERACCION = [
        ('vista_producto', 'Vista de Producto'),
        ('solicitud_simple', 'Pedido Simple (en Stock)'),
        ('solicitud_personalizada', 'Pedido Personalizado'),
        ('compra_final', 'Pago/Compra Final'),
    ]
    tipo = models.CharField(max_length=30, choices=TIPO_INTERACCION, verbose_name="Tipo de Interacción")

    # detalle TEXT
    detalles = models.TextField(null=True, blank=True, verbose_name="Detalles/Datos del Producto")

    def __str__(self):
        return f"{self.usuario.username} - {self.get_tipo_display()} ({self.fecha.strftime('%Y-%m-%d')})"

    class Meta:
        verbose_name = "Interacción de Cliente"
        verbose_name_plural = "Interacciones de Clientes"
        ordering = ['-fecha']
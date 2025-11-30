from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


# --------------------------------------------------------
# PERFIL DEL EMPLEADO / USUARIO
# --------------------------------------------------------
class PerfilEmpleado(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    fecha_nacimiento = models.DateField(null=True, blank=True)
    numero_telefono = models.CharField(max_length=15, null=True, blank=True)

    ROL_CHOICES = [
        ('cliente', 'Cliente'),
        ('admin', 'Administrador'),
        ('repartidor', 'Repartidor'),
    ]
    rol = models.CharField(max_length=20, choices=ROL_CHOICES, default='cliente')

    def __str__(self):
        return f'Perfil de {self.user.username} ({self.rol})'


# --------------------------------------------------------
# CATEGORÍAS (NUEVO)
# --------------------------------------------------------
class Categoria(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(null=True, blank=True)
    activa = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name_plural = "Categorías"


# --------------------------------------------------------
# PRODUCTOS
# --------------------------------------------------------
class Producto(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=150)
    descripcion = models.TextField(blank=True, null=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    inventario = models.IntegerField(default=0)
    activo = models.BooleanField(default=True)

    categoria = models.ForeignKey(
        Categoria, on_delete=models.CASCADE, related_name="productos", null=True, blank=True
    )

    imagen = models.ImageField(upload_to='productos/', blank=True, null=True)

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name_plural = "Productos"


# --------------------------------------------------------
# CARRITO (NUEVO)
# --------------------------------------------------------
class Carrito(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    fecha_creacion = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Carrito #{self.id} de {self.usuario.username}"

    class Meta:
        verbose_name_plural = "Carritos"


class CarritoItem(models.Model):
    carrito = models.ForeignKey(Carrito, on_delete=models.CASCADE, related_name='items')
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.IntegerField()
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)

    def subtotal(self):
        return self.cantidad * self.precio_unitario

    def __str__(self):
        return f"{self.cantidad}x {self.producto.nombre} (Carrito {self.carrito.id})"

    class Meta:
        verbose_name_plural = "Items del Carrito"


# --------------------------------------------------------
# PROMOCIONES (YA LO TENÍAS)
# --------------------------------------------------------
class Promocion(models.Model):
    id = models.AutoField(primary_key=True)
    titulo = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)
    descuento = models.DecimalField(max_digits=5, decimal_places=2)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    activa = models.BooleanField(default=True)
    productos = models.ManyToManyField(
        'Producto',
        through='ProductoPromocion',
        related_name='promociones'
    )

    def __str__(self):
        return self.titulo

    class Meta:
        verbose_name_plural = "Promociones"


class ProductoPromocion(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    promocion = models.ForeignKey(Promocion, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('producto', 'promocion')
        verbose_name_plural = "Productos en Promoción"

    def __str__(self):
        return f"{self.producto.nombre} en {self.promocion.titulo}"


# --------------------------------------------------------
# ENVÍOS (NUEVO)
# --------------------------------------------------------
class Envio(models.Model):
    TIPO_ENTREGA = [
        ('domicilio', 'Entrega a Domicilio'),
        ('recoger', 'Recoger en Tienda'),
    ]

    tipo_entrega = models.CharField(max_length=20, choices=TIPO_ENTREGA)
    direccion = models.CharField(max_length=255, null=True, blank=True)
    ciudad = models.CharField(max_length=100, null=True, blank=True)
    estado = models.CharField(max_length=100, null=True, blank=True)
    fecha_envio = models.DateField(null=True, blank=True)
    fecha_entrega = models.DateField()
    costo_envio = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return f"Envío #{self.id} ({self.tipo_entrega})"

    class Meta:
        verbose_name_plural = "Envíos"


# --------------------------------------------------------
# PEDIDOS (ACTUALIZADO)
# --------------------------------------------------------
class Pedido(models.Model):
    id = models.AutoField(primary_key=True)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    tamano = models.CharField(max_length=50)
    sabor_pan = models.CharField(max_length=50)
    relleno = models.CharField(max_length=100)
    descripcion = models.TextField()
    cantidad = models.IntegerField(default=1)

    fecha_pedido = models.DateTimeField(default=timezone.now)
    fecha_entrega = models.DateField()

    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('confirmado', 'Confirmado'),
        ('en proceso', 'En Proceso'),
        ('enviado', 'Enviado'),
        ('entregado', 'Entregado'),
        ('cancelado', 'Cancelado'),
    ]
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='pendiente')

    precio_establecido = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    envio = models.ForeignKey('Envio', on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"Pedido #{self.id} de {self.usuario.username}"

    class Meta:
        verbose_name_plural = "Pedidos"


# --------------------------------------------------------
# DETALLE DE PEDIDO (OK)
# --------------------------------------------------------
class DetallePedido(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.IntegerField()
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.cantidad}x {self.producto.nombre} - Pedido #{self.pedido.id}"

    class Meta:
        verbose_name_plural = "Detalles de Pedidos"


# --------------------------------------------------------
# RESPUESTA A PEDIDO (OK)
# --------------------------------------------------------
class RespuestaPedido(models.Model):
    pedido = models.OneToOneField(Pedido, on_delete=models.CASCADE)
    cliente_acepta = models.BooleanField(null=True)
    comentario = models.TextField(null=True, blank=True)
    fecha_respuesta = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Respuesta Pedido #{self.pedido.id}"

    class Meta:
        verbose_name_plural = "Respuestas de Pedidos"


# --------------------------------------------------------
# INTERACCIONES DEL CLIENTE (ACTUALIZADO)
# --------------------------------------------------------
class InteraccionCliente(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name="interacciones_cliente")
    fecha = models.DateTimeField(default=timezone.now)

    TIPO = [
        ('consulta', 'Consulta'),
        ('queja', 'Queja'),
        ('sugerencia', 'Sugerencia'),
        ('otro', 'Otro'),
    ]
    tipo = models.CharField(max_length=20, choices=TIPO)
    detalle = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.usuario.username} - {self.tipo} ({self.fecha})"

    class Meta:
        verbose_name_plural = "Interacciones de Clientes"
        ordering = ['-fecha']


# --------------------------------------------------------
# FAQ (NUEVO)
# --------------------------------------------------------
class FAQ(models.Model):
    pregunta = models.TextField()
    respuesta = models.TextField()
    activa = models.BooleanField(default=True)

    def __str__(self):
        return self.pregunta[:50]

    class Meta:
        verbose_name_plural = "FAQs"

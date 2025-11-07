# core/admin.py

from django.contrib import admin
from .models import (
    PerfilEmpleado,
    Producto,
    Promocion,
    ProductoPromocion,
    Pedido,
    DetallePedido,
    RespuestaPedido
)

# -------------------------------------------------------------------------
# 1. Registro de Modelos Simples
# -------------------------------------------------------------------------
admin.site.register(Producto)
admin.site.register(RespuestaPedido)

# Nota: PerfilEmpleado se registra a menudo de forma personalizada
# para integrarlo mejor con el modelo User, como veremos a continuación.
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User

from .models import InteraccionCliente


# ... (otras importaciones como PerfilEmpleado, Producto, etc.)

# ... (clases Admin existentes como PedidoAdmin, PromocionAdmin) ...


@admin.register(InteraccionCliente)
class InteraccionClienteAdmin(admin.ModelAdmin):
    """
    Configuración de la tabla Interacción de Cliente en el panel de administración.
    """
    # Define los campos que se mostrarán en la vista de lista (la tabla principal)
    list_display = (
        'usuario',
        'tipo',
        'fecha',
        'detalles_resumen'  # Usaremos un método para truncar el detalle
    )

    # Define los filtros laterales (útil para ver interacciones por tipo o fecha)
    list_filter = ('tipo', 'fecha')

    # Define los campos por los cuales se puede buscar
    search_fields = ('usuario__username', 'detalles')

    # Define los campos que no deben ser editados manualmente
    readonly_fields = ('usuario', 'fecha')

    # Método para mostrar solo una parte del campo 'detalles' en la lista
    def detalles_resumen(self, obj):
        if obj.detalles:
            # Mostrar solo los primeros 50 caracteres del detalle
            return obj.detalles[:50] + ('...' if len(obj.detalles) > 50 else '')
        return "-"

    detalles_resumen.short_description = 'Detalle'
# Inline para PerfilEmpleado
class PerfilEmpleadoInline(admin.StackedInline):
    model = PerfilEmpleado
    can_delete = False  # No permitir eliminar el perfil si existe el usuario
    verbose_name_plural = 'Perfil'


# Define un nuevo administrador de Usuario (UserAdmin)
class UsuarioAdmin(BaseUserAdmin):
    # Añade el PerfilEmpleadoInline a la vista de edición de Usuario
    inlines = (PerfilEmpleadoInline,)

    # Personaliza el formulario de Usuario si es necesario
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Información Personal', {'fields': ('first_name', 'last_name', 'email')}),
        ('Permisos', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Fechas Importantes', {'fields': ('last_login', 'date_joined')}),
    )


# Des-registra el administrador de Usuario original
admin.site.unregister(User)

# Registra el nuevo administrador personalizado
admin.site.register(User, UsuarioAdmin)

class DetallePedidoInline(admin.TabularInline):
    model = DetallePedido
    extra = 1 # Muestra un campo extra vacío para agregar un producto

@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ('id', 'usuario', 'fecha_pedido', 'estado', 'precio_establecido')
    list_filter = ('estado', 'fecha_entrega')
    search_fields = ('usuario__username', 'id')
    inlines = [DetallePedidoInline] # Aquí se agrega el inline

class ProductoPromocionInline(admin.TabularInline):
    model = ProductoPromocion
    extra = 1

@admin.register(Promocion)
class PromocionAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'descuento', 'fecha_inicio', 'fecha_fin', 'activa')
    list_filter = ('activa', 'fecha_fin')
    inlines = [ProductoPromocionInline] # Agregamos el inline



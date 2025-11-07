# core/forms.py

from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from django import forms
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.utils import timezone # ¡Importar timezone para comparar fechas!<
from .models import PerfilEmpleado # <--- ¡Asegúrate de que esta línea esté correcta!
from .models import Producto, Promocion, Pedido,RespuestaPedido
from datetime import date, timedelta

User = get_user_model()


class CustomUserCreationForm(UserCreationForm):
    """
    Formulario personalizado con orden de campos modificado.
    """

    # 1. Campos que ya existen en el modelo base (Nombre y Apellido)
    first_name = forms.CharField(label=_("Nombre"), max_length=150)
    last_name = forms.CharField(label=_("Apellido"), max_length=150)

    # 2. Campos del modelo PerfilEmpleado (Fecha Nacimiento y Teléfono)
    fecha_nacimiento = forms.DateField(
        label=_("Fecha de Nacimiento"),
        widget=forms.DateInput(attrs={'type': 'date'}),
        required=False
    )
    numero_telefono = forms.CharField(
        label=_("Teléfono"),
        max_length=15,
        required=False
    )

    class Meta:
        model = User
        # Definimos el orden de los campos que SÍ están en el modelo User.
        # Los campos de contraseña y password2 son agregados automáticamente.
        fields = ('first_name', 'last_name', 'username')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # 3. Reordenar Campos y Limpiar Textos

        # Definir la lista de campos en el orden deseado, incluyendo los campos del Perfil:
        field_order = [
            'first_name',
            'last_name',
            'fecha_nacimiento',
            'numero_telefono',
            'username',
            'password1',
            'password2'
        ]

        # Asignar el nuevo orden
        self.order_fields(field_order)

        # Traducción de etiquetas
        self.fields['username'].label = _("Usuario")
        self.fields['password2'].label = _("Confirmación de Contraseña")

        for field_name in self.fields:
            try:
                self.fields[field_name].help_text = ""
            except Exception:
                pass

    def save(self, commit=True):
        # 1. Crea el usuario (User) sin guardar.
        user = super().save(commit=False)
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']

        # CLAVE: Encriptar la contraseña
        password = self.cleaned_data.get("password")
        if password:
            user.set_password(password)

        if commit:
            user.save()

            # 2. Crea y guarda el PerfilEmpleado
            # Nota: rol='cliente' se añade aquí explícitamente
            perfil = PerfilEmpleado.objects.create(
                user=user,
                fecha_nacimiento=self.cleaned_data.get('fecha_nacimiento'),
                numero_telefono=self.cleaned_data.get('numero_telefono'),
                rol='cliente'
            )
            # La línea perfil.save() no es necesaria aquí porque objects.create() ya lo guarda.

        return user

class ProductoForm(forms.ModelForm):
    """
    Formulario para la creación y edición del modelo Producto.
    Incluye todos los campos, incluyendo la imagen.
    """
    class Meta:
        model = Producto
        # Incluir todos los campos necesarios para la edición
        fields = [
            'nombre',
            'descripcion',
            'precio',
            'tamano',
            'stock',
            'imagen'
        ]
        # Opcional: Personalizar etiquetas si es necesario
        labels = {
            'nombre': 'Nombre del Producto',
            'descripcion': 'Descripción',
            'precio': 'Precio ($)',
            'tamano': 'Tamaño',
            'stock': 'Stock Actual',
            'imagen': 'Foto del Producto',
        }

class PromocionForm(forms.ModelForm):
    class Meta:
        model = Promocion
        fields = [
            'titulo',
            'descripcion',
            'descuento',
            'fecha_inicio',
            'fecha_fin',
            'activa',
            'productos' # <-- CLAVE: Incluir el campo Many-to-Many
        ]
        # Esto hace que el campo sea un selector de fecha en HTML
        widgets = {
            'fecha_inicio': forms.DateInput(attrs={'type': 'date'}),
            'fecha_fin': forms.DateInput(attrs={'type': 'date'}),
        }
        labels = {
            'titulo': 'Título de la Promoción',
            'descuento': 'Descuento (%)',
            'fecha_inicio': 'Fecha de Inicio',
            'fecha_fin': 'Fecha de Fin',
            'activa': 'Activa',
            'productos': 'Productos a los que aplica la promoción' # <-- NUEVO Label
        }


class PedidoForm(forms.ModelForm):
    # Campos que necesitamos que el cliente rellene para la personalización

    # Cantidad debe ser un campo regular, no parte del modelo Pedido en este contexto
    cantidad = forms.IntegerField(
        label="Cantidad",
        min_value=1,
        initial=1,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Pedido
        fields = [
            'tamano',
            'sabor_pan',
            'relleno',
            'descripcion',
            'fecha_entrega',
        ]
        widgets = {
            'tamano': forms.TextInput(attrs={'class': 'form-control'}),
            'sabor_pan': forms.TextInput(attrs={'class': 'form-control'}),
            'relleno': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'fecha_entrega': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }
        labels = {
            'tamano': 'Tamaño/Porciones Deseadas',
            'sabor_pan': 'Sabor del Pan',
            'relleno': 'Relleno o Frosting',
            'descripcion': 'Descripción y Decoración Especial (Opcional)',
            'fecha_entrega': 'Fecha de Entrega Deseada',
        }

    # El campo 'cantidad' se maneja fuera del Meta model fields
    field_order = ['tamano', 'sabor_pan', 'relleno', 'descripcion', 'cantidad', 'fecha_entrega']


class RespuestaPedidoForm(forms.ModelForm):
    # Campo para la cotización (que actualizará el precio_establecido en el Pedido)
    precio_cotizado = forms.DecimalField(
        label=_("Precio Final Cotizado"),
        max_digits=10,
        decimal_places=2,
        required=True,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'})
    )

    # Campo para el comentario/razón de rechazo
    comentario = forms.CharField(
        label=_("Comentario para el Cliente (razón de rechazo o detalles)"),
        widget=forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        required=False
    )

    class Meta:
        model = RespuestaPedido
        fields = ['cliente_acepta', 'comentario']
        # Usaremos cliente_acepta para guardar si la cotización es APROBADA (True) o RECHAZADA (False)
        widgets = {
            # Ocultamos este campo ya que será manejado por el botón que pulse el admin
            'cliente_acepta': forms.HiddenInput(),
        }

    # Sobrescribimos __init__ para manejar el precio_cotizado
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Eliminamos cliente_acepta si existe, ya que lo estamos manejando con HiddenInput
        if 'cliente_acepta' in self.fields:
            del self.fields['cliente_acepta']


class SolicitudSimpleForm(forms.Form):
    """Formulario para capturar cantidad y fecha de entrega para un producto en stock."""

    cantidad = forms.IntegerField(
        label='Cantidad a Solicitar',
        min_value=1,
        initial=1,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'type': 'number'})
    )

    fecha_entrega = forms.DateField(
        label='Fecha de Entrega Requerida',
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        input_formats=['%Y-%m-%d']
    )

    def clean_fecha_entrega(self):
        """Asegura que la fecha de entrega sea al menos 2 días después de hoy."""
        fecha = self.cleaned_data.get('fecha_entrega')
        min_fecha_entrega = date.today() + timedelta(days=2)

        if fecha and fecha < min_fecha_entrega:
            raise ValidationError("La fecha de entrega debe ser al menos 2 días después de hoy para la preparación.")

        return fecha
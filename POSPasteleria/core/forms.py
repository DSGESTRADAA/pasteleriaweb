# core/forms.py

from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from django import forms
from django.utils.translation import gettext_lazy as _
from .models import PerfilEmpleado # <--- ¡Asegúrate de que esta línea esté correcta!


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
        # 1. Guarda el usuario base
        user = super().save(commit=False)
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']

        if commit:
            user.save()

            # 2. Crea y guarda el PerfilEmpleado
            perfil = PerfilEmpleado.objects.create(
                user=user,
                fecha_nacimiento=self.cleaned_data['fecha_nacimiento'],
                numero_telefono=self.cleaned_data['numero_telefono']
            )
            perfil.save()

        return user
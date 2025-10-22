# core/views.py
from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required
from .forms import CustomUserCreationForm # <--- ¡Debe usar este!

from django.contrib.auth.forms import UserCreationForm # Importa el formulario de registro de Django

# La vista de control que solo los usuarios autenticados pueden ver
# core/views.py

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required


# Importa otros módulos si es necesario (forms.py)

# La vista de control que actúa como router
@login_required
def dashboard_view(request):
    user = request.user

    if user.is_superuser:
        # Si es Superusuario, lo enviamos al dashboard de administración (admin_dashboard)
        return redirect('admin_dashboard')
    else:
        # Si es un usuario normal (cajero, empleado), lo enviamos al dashboard de usuario (user_dashboard)
        return redirect('user_dashboard')

@login_required
def admin_dashboard_view(request):
    """Dashboard completo para Superusuarios/Administradores."""
    context = {
        'title': 'Panel de Administración (Completo)',
        'username': request.user.username,
        # Aquí iría la lógica para gestión de inventario, usuarios, reportes.
    }
    return render(request, 'admin_dashboard.html', context)

@login_required
def user_dashboard_view(request):
    """Dashboard de usuario (cajero/empleado) limitado al POS."""
    context = {
        'title': 'Punto de Venta (POS)',
        'username': request.user.username,
        # Aquí iría la lógica de ventas y pedidos.
    }
    return render(request, 'user_dashboard.html', context)


def registro_usuario(request):
    # 1. Manejo del POST
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            # Si es válido, redirige y termina la función aquí
            return redirect('login')

            # 2. Manejo del GET (o si el POST falló la validación)
    # Si el metodo no fue POST, o si la validación falló, crea un formulario vacío (GET) o
    # muestra el formulario con errores (POST inválido)
    else:
        form = CustomUserCreationForm()

    # 3. DEFINICIÓN DEL CONTEXTO (¡MOVEMOS ESTO AL FINAL!)
    # Esta variable DEBE existir antes del return render.
    context = {'form': form, 'title': 'Registro de Nuevo Usuario'}

    return render(request, 'registro.html', context)
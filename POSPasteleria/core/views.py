from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.contrib import messages
from django.utils import timezone # ¡Importar timezone para comparar fechas!
from .models import Producto, Pedido, DetallePedido, User, Promocion # Asegúrate de importar Promocion
from .forms import ProductoForm,CustomUserCreationForm, PromocionForm # ¡Importar PromocionForm!
from .decorators import admin_required # <-- NUEVA IMPORTACIÓN
import math
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
    # Productos (lógica de carrusel existente)
    productos = Producto.objects.all().filter(stock__gt=0)
    productos_por_slide = 4
    carrusel_slides = [
        productos[i:i + productos_por_slide]
        for i in range(0, len(productos), productos_por_slide)
    ]

    # Nuevas: Obtener promociones activas
    today = timezone.now().date()
    promociones_activas = Promocion.objects.filter(
        activa=True,
        fecha_inicio__lte=today,
        fecha_fin__gte=today
    ).prefetch_related('productos').order_by('-fecha_inicio')

    context = {
        'titulo': 'Chispitas de Arcoíris',
        'carrusel_slides': carrusel_slides,
        'promociones_activas': promociones_activas,  # Pasar las promos al contexto
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

def pedidos_view(request):
    return render(request, 'pedidos.html')

def promociones_view(request):
    return render(request, 'promociones.html')


from django.contrib import messages  # Importamos para mensajes de éxito/error


def gestion_producto_view(request):
    # Si la petición es POST, el usuario envió datos
    if request.method == 'POST':
        # Instanciamos el formulario con los datos POST y los archivos (FILES, para la imagen)
        form = ProductoForm(request.POST, request.FILES)

        # Validamos el formulario
        if form.is_valid():
            # Guarda la instancia del modelo Producto en la base de datos
            form.save()
            messages.success(request, '🎉 Producto guardado exitosamente.')
            # Redirecciona a la misma página para limpiar el formulario o a otra página
            return redirect('gestion_producto')
        else:
            # Si no es válido, agrega un mensaje de error
            messages.error(request, 'Hubo un error al guardar el producto. Revisa los campos.')

    # Si la petición es GET o si el POST falló la validación
    else:
        # Instanciamos un formulario vacío
        form = ProductoForm()

    context = {
        'form': form,
        'titulo': 'Alta de Nuevo Producto'
    }
    return render(request, 'core/gestion_producto.html', context)

def menu_gestion_view(request): # <-- ¡Asegúrate que el nombre sea EXACTO!
    """
    Vista para mostrar el menú principal de gestión.
    """
    return render(request, 'core/menu_gestion.html', {'titulo': 'Menú de Gestión Administrativa'})


@admin_required(redirect_url='dashboard')  # Redirige al dashboard si el rol no es 'administrador'
def gestion_promocion_view(request):
    if request.method == 'POST':
        form = PromocionForm(request.POST)

        if form.is_valid():
            form.save()
            messages.success(request, '🎉 Promoción guardada exitosamente.')
            # Redireccionamos a la misma página para limpiar el formulario
            return redirect('gestion_promocion')
        else:
            messages.error(request, 'Hubo un error al guardar la promoción. Revisa los campos.')
    else:
        form = PromocionForm()

    context = {
        'form': form,
        'titulo': 'Alta de Nueva Promoción'
    }
    return render(request, 'core/gestion_promocion.html', context)
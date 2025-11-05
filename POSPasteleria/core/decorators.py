from django.shortcuts import redirect
from django.contrib.auth.decorators import user_passes_test

# ----------------------------------------------------------------
# Función de verificación para el decorador
# ----------------------------------------------------------------
def is_admin(user):
    """Verifica si el usuario es superusuario o tiene el rol 'administrador'."""
    if user.is_superuser:
        return True
    try:
        # Intenta acceder al PerfilEmpleado y verificar el rol
        return user.perfilempleado.rol == 'administrador'
    except:
        # Si el usuario no tiene un perfil asociado, no es administrador
        return False

# ----------------------------------------------------------------
# Decorador de uso
# ----------------------------------------------------------------
def admin_required(function=None, redirect_url='dashboard'):
    """
    Decorador que restringe el acceso a la vista solo a administradores.
    Redirige a 'dashboard' si no se cumple.
    """
    # user_passes_test toma la función de verificación (is_admin)
    actual_decorator = user_passes_test(is_admin,login_url=redirect_url)
    if function:
        return actual_decorator(function)
    return actual_decorator
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.views.generic.base import RedirectView  # Importación para la redirección
from core import views  # Importamos las vistas de la app 'core'
from django.conf import settings # ¡Necesitas importar settings!
from django.conf.urls.static import static # ¡Necesitas importar static!

urlpatterns = [
    # 1. Redirección de la Raíz: Envía '/' directamente a '/login/'
    path('', RedirectView.as_view(url='/login/', permanent=True)),
    path('admin/', admin.site.urls),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='/login/'), name='logout'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('registro/', views.registro_usuario, name='registro'),
    path('panel/admin/', views.admin_dashboard_view, name='admin_dashboard'),
    path('pos/venta/', views.user_dashboard_view, name='user_dashboard'),
    path('pedidos/', views.pedidos_view, name='pedidos'),
    path('promociones/', views.promociones_view, name='promociones'),
    path('gestion/', views.menu_gestion_view, name='menu_gestion'),
    path('gestion/producto/nuevo/', views.gestion_producto_view, name='gestion_producto'),
    path('gestion/promocion/nueva/', views.gestion_promocion_view, name='gestion_promocion'), # NUEVA URL
]

if settings.DEBUG:
    # Esto le dice a Django que sirva archivos de la ruta MEDIA_ROOT
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
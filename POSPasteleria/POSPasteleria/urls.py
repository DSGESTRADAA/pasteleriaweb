from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.views.generic.base import RedirectView  # Importación para la redirección
from core import views  # Importamos las vistas de la app 'core'
from django.conf import settings # ¡Necesitas importar settings!
from django.conf.urls.static import static # ¡Necesitas importar static!
from core import views

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
    path('pedidos/', views.cliente_pedidos_view, name='pedidos'),
    path('gestion/', views.menu_gestion_view, name='menu_gestion'),
    path('gestion/inventario/', views.gestion_inventario_view, name='gestion_inventario'),
    path('gestion/producto/', views.gestion_producto_view, name='gestion_producto'),
    path('gestion/productos/editar/<int:producto_id>/', views.gestion_editar_producto_view,name='gestion_editar_producto'),
    path('gestion/producto/nuevo/', views.gestion_producto_view, name='gestion_producto_nuevo'),
    path('gestion/promocion/nueva/', views.gestion_promocion_view, name='gestion_promocion'), # NUEVA URL
    path('pedido/personalizado/', views.hacer_pedido_personalizado_view, name='hacer_pedido_personalizado'),
    path('gestion/pedidos/pendientes/', views.admin_pedidos_pendientes_view, name='admin_pedidos_pendientes'),
    path('gestion/pedidos/aprobar/<int:pedido_id>/', views.admin_aprobar_pedido_view, name='admin_aprobar_pedido'),
    path('cliente/pedidos/', views.cliente_pedidos_view, name='cliente_pedidos'),
    path('cliente/pedidos/<int:pedido_id>/', views.cliente_detalle_pedido_view, name='cliente_detalle_pedido'),
    path('cliente/pagar/<int:pedido_id>/', views.cliente_pagar_pedido_view, name='cliente_pagar_pedido'),
    path('gestion/calendario/', views.admin_calendario_produccion_view, name='admin_calendario_produccion'),
    path('gestion/cambiar-estado/<int:pedido_id>/', views.admin_cambiar_estado_pedido_view,name='admin_cambiar_estado_pedido'),
    path('pedido/solicitar-simple/<int:producto_id>/', views.solicitar_pedido_simple_view, name='solicitar_pedido_simple'),
    path('api/faqs/', views.obtener_faqs, name='obtener_faqs'),
    path('api/chat/send/', views.api_send_message, name='api_chat_send'),
    path('api/chat/get/', views.api_get_messages, name='api_chat_get'),
    path('cart/add/<int:producto_id>/', views.cart_add, name='cart_add'),
    path('cart/remove/<int:producto_id>/', views.cart_remove, name='cart_remove'),
    path('cart/', views.detalles_carrito, name='detalles_carrito'),
    path('procesar-compra/', views.procesar_compra_view, name='procesar_compra'),
]

if settings.DEBUG:
    # Esto le dice a Django que sirva archivos de la ruta MEDIA_ROOT
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
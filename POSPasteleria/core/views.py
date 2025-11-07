from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.contrib import messages
from datetime import timedelta
from django.utils import timezone # ¡Importar timezone para comparar fechas!
from .models import Producto, Pedido, DetallePedido, User, Promocion, RespuestaPedido,InteraccionCliente # Asegúrate de importar Promocion
from .forms import ProductoForm,CustomUserCreationForm, PromocionForm, PedidoForm,RespuestaPedidoForm # ¡Importar PromocionForm!
from .decorators import admin_required # <-- NUEVA IMPORTACIÓN
from .models import PerfilEmpleado # Asegúrate de importar tu modelo de perfil
from django.views.decorators.http import require_http_methods # Útil para la vista POST
from .forms import SolicitudSimpleForm
from django.db.models import Count # Importar para contar interacciones
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


@login_required(login_url='login')
def user_dashboard_view(request):
    """Dashboard de usuario (cajero/empleado) limitado al POS."""

    # 1. Lógica de Producto y Carrusel (se usa para el POS, mostrando items)
    productos = Producto.objects.all().filter(stock__gt=0).order_by('nombre')

    # Esta parte se usa si el POS tuviera carrusel, pero generalmente es lista:
    productos_por_slide = 3
    carrusel_slides = [
        productos[i:i + productos_por_slide]
        for i in range(0, len(productos), productos_por_slide)
    ]

    # 2. Obtener promociones activas (Generalmente NO necesario en el POS,
    # pero si necesitas mostrarlas, mantenemos la lógica)
    today = timezone.now().date()
    promociones_activas = Promocion.objects.filter(
        activa=True,
        fecha_inicio__lte=today,
        fecha_fin__gte=today
    ).prefetch_related('productos').order_by('-fecha_inicio')


    # 🚨 NUEVA LÓGICA: Recomendaciones (Moviendo la lógica de la vista original del cliente)
    recomendaciones = []
    if request.user.is_authenticated:
        # Llama a la función que calcula las recomendaciones
        recomendaciones = get_recommendations(request.user)

    context = {
        'titulo': 'Chispitas de Arcoíris',
        'username': request.user.username,
        'carrusel_slides': carrusel_slides,
        'promociones_activas': promociones_activas,
        'recomendaciones': recomendaciones,  # <-- VARIABLE AÑADIDA
        # ... Aquí iría el resto del contexto del POS (cart_items, total_venta, etc.)
    }
    return render(request, 'user_dashboard.html', context)


def registro_usuario(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)

        if form.is_valid():
            # 1. Crear el objeto User, pero NO lo guardamos aún en la DB (commit=False)
            user = form.save(commit=False)

            # 2. Configurar y hashear la contraseña de forma segura

            # 3. Guardar el objeto User en la base de datos
            user.save()

            # 4. CREAR EL PERFIL Y ASIGNAR EL ROL POR DEFECTO 'cliente'
            # (Este paso resuelve el IntegrityError)
            PerfilEmpleado.objects.create(
                user=user,
                rol='cliente',  # Asignamos explícitamente el rol por defecto
                # Nota: Si tu CustomUserCreationForm maneja campos del PerfilEmpleado,
                # tendrías que pasarlos aquí (ej. telefono=form.cleaned_data.get('telefono')).
            )

            messages.success(request, '¡Registro exitoso! Ya puedes iniciar sesión.')
            # Redirige y termina la función aquí
            return redirect('login')

            # Si la validación falla (el código continúa hacia abajo, renderizando el formulario con errores)

    # 2. Manejo del GET (o si el POST falló la validación)
    else:
        form = CustomUserCreationForm()

    # 3. DEFINICIÓN DEL CONTEXTO (¡DEBE estar al final!)
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


@login_required(login_url='login')
def hacer_pedido_personalizado_view(request):
    # Ya no necesitamos el producto, es 100% personalizado

    if request.method == 'POST':
        form = PedidoForm(request.POST)  # Usamos el PedidoForm que ya existe
        if form.is_valid():

            pedido = form.save(commit=False)

            pedido.usuario = request.user
            pedido.estado = 'pendiente'  # El admin debe cotizarlo

            # El precio es 0 porque el admin debe cotizarlo
            pedido.precio_establecido = 0

            pedido.save()

            # NO CREAMOS DetallePedido (porque no hay producto)

            messages.success(request,
                             f"🎉 Tu solicitud de pedido personalizado ha sido enviada. Recibirás una cotización pronto.")
            return redirect('cliente_pedidos')  # Lo mandamos a sus pedidos
        else:
            messages.error(request, 'Hubo un error al procesar tu solicitud.')

    else:
        form = PedidoForm()

    context = {
        'form': form,
        'titulo': 'Solicitar Pedido Personalizado',
    }
    return render(request, 'core/hacer_pedido.html', context)


@admin_required(redirect_url='dashboard')
def admin_pedidos_pendientes_view(request):
    """
    Muestra todos los pedidos que están en estado 'pendiente' para revisión del administrador.
    """
    # Usamos prefetch_related para obtener los detalles del pedido y el producto
    # en pocas consultas, mejorando la velocidad.
    pedidos_pendientes = Pedido.objects.filter(estado='pendiente').order_by('fecha_pedido').prefetch_related(
        'detallepedido_set__producto',  # Accede a los detalles y luego al producto asociado
        'usuario'  # Accede al usuario que hizo el pedido
    )

    context = {
        'pedidos': pedidos_pendientes,
        'titulo': 'Pedidos Especiales Pendientes de Aprobación',
    }
    return render(request, 'core/admin_pedidos_pendientes.html', context)


@admin_required(redirect_url='dashboard')
def admin_aprobar_pedido_view(request, pedido_id):
    pedido = get_object_or_404(Pedido.objects.prefetch_related('detallepedido_set__producto'), id=pedido_id)

    # Si ya existe una respuesta (para evitar duplicados)
    try:
        respuesta = RespuestaPedido.objects.get(pedido=pedido)
    except RespuestaPedido.DoesNotExist:
        respuesta = None

    if request.method == 'POST':
        form = RespuestaPedidoForm(request.POST)
        action = request.POST.get('action')  # Captura la acción del botón (cotizar/rechazar)

        if form.is_valid():
            precio_cotizado = form.cleaned_data.get('precio_cotizado')
            comentario = form.cleaned_data.get('comentario')

            with transaction.atomic():
                if action == 'aprobar_cotizar':
                    # 1. Actualizar el precio cotizado en el Pedido
                    pedido.precio_establecido = precio_cotizado
                    pedido.estado = 'confirmado'  # El admin lo confirma (a la espera del pago del cliente)
                    pedido.save()

                    # 2. Crear la respuesta para el cliente
                    RespuestaPedido.objects.create(
                        pedido=pedido,
                        cliente_acepta=True,  # Admin aprueba la cotización
                        comentario=comentario
                    )
                    messages.success(request,
                                     f'Cotización (${precio_cotizado}) enviada al cliente para el Pedido #{pedido_id}.')

                elif action == 'rechazar':
                    # 1. Actualizar estado y crear respuesta de rechazo
                    pedido.estado = 'cancelado'
                    pedido.save()
                    RespuestaPedido.objects.create(
                        pedido=pedido,
                        cliente_acepta=False,  # Admin lo rechaza
                        comentario=comentario or "El pedido fue rechazado por razones de logística o capacidad."
                    )
                    messages.warning(request, f'Pedido #{pedido_id} rechazado y notificado al cliente.')

            return redirect('admin_pedidos_pendientes')

    else:
        # Inicializar el formulario con el precio sugerido (si no hay respuesta)
        initial_data = {}
        if not respuesta:
            # Si no hay respuesta previa, usa el precio estimado del pedido
            initial_data['precio_cotizado'] = pedido.precio_establecido

        form = RespuestaPedidoForm(initial=initial_data)

    context = {
        'pedido': pedido,
        'form': form,
        'respuesta': respuesta,
        'titulo': f'Revisar Pedido #{pedido_id}',
    }
    return render(request, 'core/admin_aprobar_pedido.html', context)


@login_required(login_url='login')
def cliente_pedidos_view(request):
    # Obtener pedidos del usuario actual
    pedidos_cliente = Pedido.objects.filter(usuario=request.user).order_by('-fecha_pedido').prefetch_related(
        'detallepedido_set__producto',

        'respuestapedido'  # <-- ¡CLAVE! SIN _set

    )

    context = {
        'pedidos': pedidos_cliente,
        # ...
    }
    return render(request, 'core/cliente_pedidos.html', context)


@login_required(login_url='login')
def cliente_pagar_pedido_view(request, pedido_id):
    if request.method == 'POST':
        pedido = get_object_or_404(Pedido, id=pedido_id, usuario=request.user, estado='confirmado')

        # 1. Actualizar el estado del Pedido:
        # Antes era 'entregado', ahora es 'en_preparacion'
        pedido.estado = 'en_preparacion'  # <-- ¡CLAVE!
        pedido.save()

        messages.success(request, f"Pago del Pedido #{pedido.id} exitoso. ¡Tu pedido está en preparación!")

    return redirect('cliente_pedidos')


@admin_required(redirect_url='dashboard')
def admin_calendario_produccion_view(request):
    # Ahora incluimos el estado 'en_preparacion'
    estados_activos = ['en_preparacion', 'listo_para_entrega']  # <-- ¡CLAVE!

    # ... (el resto de la consulta es igual) ...
    pedidos_produccion = Pedido.objects.filter(
        estado__in=estados_activos
    ).order_by('fecha_entrega').prefetch_related(
        'detallepedido_set__producto'  # Optimizar la carga de detalles
    )

    # Agrupar pedidos por fecha de entrega para el formato de "calendario"
    pedidos_agrupados = {}
    for pedido in pedidos_produccion:
        # Formatear la fecha para usarla como clave
        fecha_str = pedido.fecha_entrega.strftime('%Y-%m-%d')
        if fecha_str not in pedidos_agrupados:
            pedidos_agrupados[fecha_str] = []
        pedidos_agrupados[fecha_str].append(pedido)

    context = {
        'pedidos_agrupados': pedidos_agrupados,
        # Estados disponibles para que el administrador pueda cambiar:
        'estados_disponibles': ['confirmado', 'en_produccion', 'listo_para_entrega', 'entregado', 'cancelado']
    }
    return render(request, 'core/admin_calendario_produccion.html', context)


# Vista para manejar la solicitud POST de cambio de estado
@admin_required(redirect_url='dashboard')
@require_http_methods(["POST"])
def admin_cambiar_estado_pedido_view(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id)
    nuevo_estado = request.POST.get('nuevo_estado')

    # Lista de estados válidos para validación
    estados_validos = ['confirmado', 'en_produccion', 'listo_para_entrega', 'entregado', 'cancelado']

    if nuevo_estado in estados_validos:
        # Actualizar el estado y guardar
        pedido.estado = nuevo_estado
        pedido.save()

        # Mostrar mensaje de éxito
        messages.success(request,
                         f"El estado del Pedido #{pedido.id} ha sido actualizado a: {nuevo_estado.replace('_', ' ').title()}")
    else:
        # Mostrar mensaje de error
        messages.error(request, "Error: El estado seleccionado no es válido.")

    # Redirigir de vuelta al calendario de producción
    return redirect('admin_calendario_produccion')


@login_required(login_url='login')
def solicitar_pedido_simple_view(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)

    # Si no hay stock para al menos 1 unidad, redirigir inmediatamente
    if producto.stock <= 0:
        messages.error(request, f"Lo sentimos, {producto.nombre} está agotado.")
        return redirect('dashboard')

    if request.method == 'POST':
        form = SolicitudSimpleForm(request.POST)
        if form.is_valid():
            cantidad = form.cleaned_data['cantidad']
            fecha_entrega = form.cleaned_data['fecha_entrega']

            # Re-verificar stock con la cantidad solicitada
            if cantidad > producto.stock:
                messages.error(request,
                               f"Solo quedan {producto.stock} unidades de {producto.nombre}. No se pueden solicitar {cantidad}.")
                return render(request, 'core/solicitar_simple.html', {'producto': producto, 'form': form})

            # --- Lógica de Creación del Pedido (si todo es válido) ---
            subtotal = producto.precio * cantidad

            try:
                # 1. Crear el Pedido (estado pendiente)
                nuevo_pedido = Pedido.objects.create(
                    usuario=request.user,
                    estado='pendiente',
                    precio_establecido=subtotal,
                    fecha_entrega=fecha_entrega,
                )

                # 2. Crear el Detalle del Pedido
                DetallePedido.objects.create(
                    pedido=nuevo_pedido,
                    producto=producto,
                    cantidad=cantidad,
                    precio_unitario=producto.precio,
                    subtotal=subtotal
                )

                # 3. Descontar el stock
                producto.stock -= cantidad
                producto.save()

                # 4. REGISTRO DE INTERACCIÓN DE CONSUMO (MOVIDO AQUÍ)
                InteraccionCliente.objects.create(
                    usuario=request.user,
                    tipo='solicitud_simple',
                    detalles=f"Solicitó {cantidad}x {producto.nombre} (ID: {producto_id}, Subtotal: {subtotal})"
                )

                messages.success(request,
                                 f"Solicitud para {cantidad}x {producto.nombre} enviada para el {fecha_entrega}. Un administrador confirmará su pago.")

            except Exception as e:
                messages.error(request, f"Error al procesar la solicitud: {e}")
                # Si falla la creación, el redirect igual debe funcionar

            return redirect('cliente_pedidos')  # Redirige después de que el POST termina

    else:
        # GET request: Display the form
        form = SolicitudSimpleForm()

    context = {
        'producto': producto,
        'form': form,
    }

    # ❌ ELIMINAMOS EL BLOQUE try/except EXTRAÑO AL FINAL
    return render(request, 'core/solicitar_simple.html', context)


@login_required(login_url='login')
def cliente_detalle_pedido_view(request, pedido_id):
    """Muestra los detalles completos de un solo pedido al cliente."""

    # 1. Obtener el pedido, asegurándose de que pertenezca al usuario logueado
    pedido = get_object_or_404(
        Pedido.objects.prefetch_related('detallepedido_set__producto', 'respuestapedido'),
        id=pedido_id,
        usuario=request.user  # CLAVE: Seguridad para que solo vea sus pedidos
    )

    # 2. Obtener la respuesta del administrador (si existe)
    try:
        respuesta = pedido.respuestapedido
    except RespuestaPedido.DoesNotExist:
        respuesta = None

    # 3. Obtener los detalles del pedido (productos)
    detalles = pedido.detallepedido_set.all()

    context = {
        'pedido': pedido,
        'respuesta': respuesta,
        'detalles': detalles,
        'titulo': f'Detalles del Pedido #{pedido_id}',
    }
    return render(request, 'core/cliente_detalle_pedido.html', context)


@admin_required
def gestion_inventario_view(request):
    """Muestra la lista de todos los productos para que el admin pueda editarlos."""

    productos = Producto.objects.all().order_by('nombre')

    context = {
        'productos': productos,
        'titulo': 'Gestión de Inventario y Precios',
    }
    return render(request, 'core/gestion_inventario.html', context)


@admin_required
def gestion_editar_producto_view(request, producto_id):
    """Permite al admin editar un producto existente."""

    producto_instancia = get_object_or_404(Producto, id=producto_id)
    titulo_pagina = f'Editar Producto: {producto_instancia.nombre}'

    if request.method == 'POST':
        # Usamos la instancia para EDITAR el objeto existente
        form = ProductoForm(request.POST, request.FILES, instance=producto_instancia)

        if form.is_valid():
            form.save()
            messages.success(request, f"🎉 Producto '{producto_instancia.nombre}' actualizado correctamente.")
            return redirect('gestion_inventario')
        else:
            messages.error(request, "Hubo un error en los datos. Por favor, revisa el formulario.")

    else:
        # Petición GET: Cargar el formulario con los datos de la instancia
        form = ProductoForm(instance=producto_instancia)

    context = {
        'form': form,
        'titulo': titulo_pagina,
        'producto_id': producto_id,
    }
    return render(request, 'core/gestion_editar_producto.html', context)


from django.db.models import Count, Sum
from .models import Producto, Pedido, DetallePedido
from itertools import chain


def get_recommendations(user):
    """
    Genera recomendaciones estrictas: solo los 4 productos con la mayor frecuencia
    total de solicitud (popularidad), siempre que estén en stock.
    """
    RECOMMENDATION_LIMIT = 3

    # 1. Obtener todos los productos que están en stock (stock__gt=0)
    #    y anotarlos con su frecuencia total de solicitud (popularidad).
    productos_populares = Producto.objects.filter(stock__gt=0).annotate(
        # Contar cuántas veces aparece este producto en la tabla DetallePedido
        frecuencia_solicitud=Count('detallepedido')
    ).filter(
        frecuencia_solicitud__gt=0  # CLAVE: Excluir productos que NUNCA han sido pedidos
    ).order_by('-frecuencia_solicitud', 'nombre')[:RECOMMENDATION_LIMIT]  # Tomar solo los 4 primeros

    # Nota: Ya no excluimos lo que el usuario compró, sino que asumimos
    # que si lo compró mucho, es su favorito y debemos seguir recomendándolo.

    return list(productos_populares)
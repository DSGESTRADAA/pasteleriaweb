# core/cart.py
from decimal import Decimal
from django.conf import settings
from .models import Producto


class Cart:
    def __init__(self, request):
        """Inicializa el carrito."""
        self.session = request.session
        cart = self.session.get('cart')
        if not cart:
            # Si no hay carrito en la sesión, creamos uno vacío
            cart = self.session['cart'] = {}
        self.cart = cart

    def add(self, producto, cantidad=1, override_quantity=False):
        """Agrega un producto al carrito o actualiza su cantidad."""
        product_id = str(producto.id)  # Las claves en sesión deben ser strings

        if product_id not in self.cart:
            self.cart[product_id] = {
                'cantidad': 0,
                'precio': str(producto.precio)  # Convertimos a string para serializar JSON
            }

        if override_quantity:
            self.cart[product_id]['cantidad'] = cantidad
        else:
            self.cart[product_id]['cantidad'] += cantidad

        self.save()

    def save(self):
        """Marca la sesión como modificada para asegurar que se guarde."""
        self.session.modified = True

    def remove(self, producto):
        """Elimina un producto del carrito."""
        product_id = str(producto.id)
        if product_id in self.cart:
            del self.cart[product_id]
            self.save()

    def __iter__(self):
        """
        Itera sobre los elementos del carrito y obtiene los productos
        de la base de datos.
        """
        product_ids = self.cart.keys()
        # Obtenemos los objetos Producto de la BD
        productos = Producto.objects.filter(id__in=product_ids)
        cart = self.cart.copy()

        for producto in productos:
            cart[str(producto.id)]['producto'] = producto

        for item in cart.values():
            item['precio'] = Decimal(item['precio'])
            item['total_precio'] = item['precio'] * item['cantidad']
            yield item

    def __len__(self):
        """Cuenta la cantidad de items en el carrito."""
        return sum(item['cantidad'] for item in self.cart.values())

    def get_total_price(self):
        """Calcula el costo total del carrito."""
        return sum(Decimal(item['precio']) * item['cantidad'] for item in self.cart.values())

    def clear(self):
        """Vacía el carrito (usar después de completar la compra)."""
        del self.session['cart']
        self.save()
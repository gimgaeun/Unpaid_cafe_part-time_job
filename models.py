class Product:
    def __init__(self, name, price, category, sold_out, options):
        self.name = name
        self.price = price
        self.category = category
        self.sold_out = sold_out
        self.options = options


class Order:
    def __init__(self, order_id, order_time, products, total_price):
        self.order_id = order_id
        self.order_time = order_time
        self.products = products
        self.total_price = total_price


class OrderItem:
    def __init__(self, product, quantity, options):
        self.product = product
        self.quantity = quantity
        self.options = options

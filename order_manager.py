import csv
from models import Order
from datetime import datetime


class OrderManager:
    def __init__(self):
        self.orders = []
        self.current_order_date = None

    @staticmethod
    def extract_date_str(order_time):
        return str(order_time).strip().split(" ")[0]

    def read_order_file(self, filename):
        loaded = []
        try:
            with open(filename, "r", encoding="utf-8-sig", newline="") as file:
                reader = csv.DictReader(file)
                for row in reader:
                    try:
                        products = self.parse_order_products(row["products"])
                        order = Order(
                            int(row["order_id"]),
                            row["order_time"],
                            products,
                            int(row["total_price"]),
                        )
                        loaded.append(order)
                    except (KeyError, ValueError):
                        print("주문 데이터 형식이 잘못됨")
                        continue
        except FileNotFoundError:
            print()
            print(f"주문 데이터 파일을 찾을 수 없습니다: {filename}")
        return loaded

    # 주문 정보 파일 불러오기
    def load_order(self, filename):
        self.orders = self.read_order_file(filename)
        return self.orders

    # 주문 정보 파일 저장
    def save_orders(self, filename, orders_to_save, retries=3):
        for i in range(retries):
            try:
                with open(filename, "w", encoding="utf-8-sig", newline="") as file:
                    writer = csv.writer(file)
                    writer.writerow(
                        ["order_id", "order_time", "products", "total_price"]
                    )
                    for order in orders_to_save:
                        if type(order.products) == list:
                            products_text = self.make_products_text(order.products)
                        else:
                            products_text = order.products
                        writer.writerow(
                            [
                                order.order_id,
                                order.order_time,
                                products_text,
                                order.total_price,
                            ]
                        )
                return True
            except OSError:
                print(f"파일 저장 실패({i + 1}회)")
                continue
        return False

    # 주문 생성
    def create_order(self, order_id, order_time, products, total_price):
        order = Order(
            order_id,
            order_time,
            products,
            total_price,
        )
        self.orders.append(order)
        return order

    # 다음 주문 번호 계산
    def get_next_order_id(
        self, order_file, sales_file="data/sales.csv", target_date=None
    ):
        if target_date is None:
            target_date = datetime.now().strftime("%Y-%m-%d")

        max_today_id = 0
        for filename in [order_file, sales_file]:
            orders = self.read_order_file(filename)
            for order in orders:
                if self.extract_date_str(order.order_time) == target_date:
                    if order.order_id > max_today_id:
                        max_today_id = order.order_id
        next_id = max_today_id + 1
        self.current_order_date = target_date
        return next_id

    # 주문 수량 제한
    def check_order_limit(self, order_items, quantity):
        if quantity <= 0:
            print("수량은 1개 이상이어야함")
            return False
        if quantity > 10:
            print("한 상품은 최대 10개까지만 주문 가능")
            return False
        total_quantity = sum(item["quantity"] for item in order_items)
        if total_quantity + quantity > 50:
            print("전체 주문은 최대 50개까지만 주문 가능")
            return False
        return True

    # 주문 내역 출력
    def show_cart_items(self, order_items):
        print("\n-장바구니 내역-")
        if not order_items:
            print("담긴 상품 없음")
            return
        for i, item in enumerate(order_items, 1):
            product = item["product"]
            quantity = item["quantity"]
            options = item["options"]
            print(f"{i}. {product.name}\n   수량: {quantity}")
            print("   옵션:", ", ".join(options) if options else "없음")
        print("====================")

    # 주문 완료 처리
    def complete_order(self, order_id, order_file, sales_file, target_date=None):
        orders = self.read_order_file(order_file)
        target_order = None
        for order in orders:
            order_date = self.extract_date_str(order.order_time)
            if order.order_id == order_id and (
                target_date is None or order_date == target_date
            ):
                target_order = order
                break
        if target_order is None:
            print("해당 주문을 찾을 수 없음")
            return False
        target_order_date = self.extract_date_str(target_order.order_time)
        sales = self.read_order_file(sales_file)
        for sale in sales:
            if (
                sale.order_id == order_id
                and self.extract_date_str(sale.order_time) == target_order_date
            ):
                print("이미 완료된 주문")
                return False
        remaining_orders = [order for order in orders if order is not target_order]
        sales.append(target_order)
        if not self.save_orders(sales_file, sales, retries=3):
            return False
        if not self.save_orders(order_file, remaining_orders, retries=3):
            return False
        self.orders = remaining_orders
        print(f"{order_id}번 주문 완료")
        return True

    # 상품 정보 변환
    def parse_order_products(self, products_text):
        products = []
        if not products_text:
            return products
        for product_text in products_text.split("|"):
            parts = product_text.split(":")
            if len(parts) < 2:
                continue
            name = parts[0]
            try:
                quantity = int(parts[1])
                price = int(parts[2]) if len(parts) >= 3 else None
            except ValueError:
                continue
            options = []
            if len(parts) >= 4 and parts[3]:
                for option_text in parts[3].split("+"):
                    opt_parts = option_text.split("=")
                    if len(opt_parts) != 2:
                        continue
                    try:
                        options.append(
                            {
                                "name": opt_parts[0],
                                "price": int(opt_parts[1]),
                            }
                        )
                    except ValueError:
                        continue
            products.append(
                {
                    "name": name,
                    "quantity": quantity,
                    "price": price,
                    "options": options,
                }
            )
        return products

    # 주문 데이터 -> 문자열
    def make_products_text(self, order_items):
        if not order_items:
            return ""
        product_texts = []
        for item in order_items:
            if "product" in item:
                product = item["product"]
                name = product.name
                price = product.price
                quantity = item["quantity"]
                option_texts = [
                    f"{opt_name}={product.options[opt_name]}"
                    for opt_name in item["options"]
                    if opt_name in product.options
                ]
            else:
                name = item["name"]
                price = item["price"] if item["price"] is not None else 0
                quantity = item["quantity"]
                option_texts = [
                    f"{opt['name']}={opt['price']}" for opt in item.get("options", [])
                ]
            options_text = "+".join(option_texts)
            product_texts.append(f"{name}:{quantity}:{price}:{options_text}")
        return "|".join(product_texts)

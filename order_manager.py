import csv
from models import Order


class OrderManager:
    def __init__(self):
        self.orders = []

    # 주문 정보 파일 불러오기
    def load_order(self, filename):
        self.orders = []
        try:
            with open(filename, "r", encoding="utf-8-sig", newline="") as file:
                reader = csv.DictReader(file)
                for row in reader:
                    try:
                        order = Order(
                            int(row["order_id"]),
                            row["order_time"],
                            row["products"],
                            int(row["total_price"]),
                        )
                        self.orders.append(order)
                    except (KeyError, ValueError):
                        print("주문 데이터 형식이 잘못됨")
                        continue
        except FileNotFoundError:
            print()
            print(f"주문 데이터 파일을 찾을 수 없습니다: {filename}")

    # 주문 정보 파일 저장
    def save_orders(self, filename):
        with open(filename, "w", encoding="utf-8-sig", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["order_id", "order_time", "products", "total_price"])
            for order in self.orders:
                writer.writerow(
                    [
                        order.order_id,
                        order.order_time,
                        order.products,
                        order.total_price,
                    ]
                )

    # 다음 주문 번호
    def get_next_order_id(self, order_file, sales_file="data/sales.csv"):
        max_order_id = 0
        for filename in [order_file, sales_file]:
            try:
                with open(filename, "r", encoding="utf-8-sig", newline="") as file:
                    reader = csv.DictReader(file)
                    for row in reader:
                        try:
                            order_id = int(row["order_id"])
                            if order_id > max_order_id:
                                max_order_id = order_id
                        except (ValueError, KeyError):
                            continue
            except FileNotFoundError:
                continue
        return max_order_id + 1

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
    def show_orders(self, order_items):
        print("\n-주문 내역-")
        if not order_items:
            print("주문 상품 없음")
            return

        for i, item in enumerate(order_items, 1):
            product = item["product"]
            quantity = item["quantity"]
            options = item["options"]

            print(f"{i}. {product.name}\n   수량: {quantity}")
            print("   옵션:", ", ".join(options) if options else "없음")
        print("====================")

    # 주문 완료 처리

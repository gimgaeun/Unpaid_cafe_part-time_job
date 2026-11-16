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

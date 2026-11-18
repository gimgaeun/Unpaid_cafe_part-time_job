import csv
from models import Order
from datetime import datetime
from order_manager import OrderManager


class SalesManager:
    def __init__(self):
        self.sales = []

    # 매출 기록 파일 불러오기
    def load_sales(self, filename):
        self.sales = []
        try:
            with open(filename, "r", encoding="utf-8-sig", newline="") as file:
                reader = csv.DictReader(file)
                for row in reader:
                    try:
                        sale = Order(
                            int(row["order_id"]),
                            row["order_time"],
                            OrderManager.parse_order_products(row["products"]),
                            int(row["total_price"]),
                        )
                        self.sales.append(sale)
                    except (KeyError, ValueError):
                        print("매출 데이터 형식이 잘못됨.")
                        continue
        except FileNotFoundError:
            print()
            print(f"매출 데이터 파일을 찾을 수 없습니다: {filename}")

    # 전체 매출 계산
    def calculate_total_sales(self):
        total = 0
        for sale in self.sales:
            total += sale.total_price
        return total

    # 매출 내역 출력
    def show_sales(self):
        print("\n-매출 내역-")
        if not self.sales:
            print("매출 내역 없음")
            return
        for sale in self.sales:
            print(f"주문번호 : {sale.order_id}")
            print(f"주문시간 : {sale.order_time}")
            product_summaries = []
            for product in sale.products:
                product_summaries.append(f"{product['name']}x{product['quantity']}")
            print(f"상품: {', '.join(product_summaries)}")
            print(f"매출금액 : {sale.total_price}")

    # 전체 매출 확인
    def check_sales(self):
        print("\n-매출 확인-")
        print(f"판매 건수: {len(self.sales)}건")
        print(f"총 매출: {self.calculate_total_sales()}원")

    # 날짜 입력
    def input_date_range(self):
        while True:
            try:
                start_date = input("시작 날짜 입력 (YYYY-MM-DD) : ").strip()
                end_date = input("종료 날짜 입력 (YYYY-MM-DD) : ").strip()
                start = datetime.strptime(start_date, "%Y-%m-%d").date()
                end = datetime.strptime(end_date, "%Y-%m-%d").date()
                if start > end:
                    print("시작 날짜가 종료 날짜보다 늦을 수 없음")
                    continue
                return (start_date, end_date, start, end)
            except ValueError:
                print("날짜 형식이 올바르지 않음")

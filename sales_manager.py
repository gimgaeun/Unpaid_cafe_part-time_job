import csv
from datetime import datetime
from models import Order
from order_manager import OrderManager


class SalesManager:
    def __init__(self):
        self.sales = []
        self.order_manager = OrderManager()

    # 매출 기록 파일 불러오기
    def load_sales(self, filename):
        self.sales = []
        try:
            with open(filename, "r", encoding="utf-8-sig", newline="") as file:
                reader = csv.DictReader(file)
                for row in reader:
                    try:
                        parsed_products = self.order_manager.parse_order_products(
                            row["products"]
                        )
                        sale = Order(
                            int(row["order_id"]),
                            row["order_time"],
                            parsed_products,
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

    # 기간 매출 필터링
    def filter_date_sales(self, start, end):
        filtered_sales = []
        for sale in self.sales:
            order_date = datetime.strptime(sale.order_time, "%Y-%m-%d %H:%M:%S").date()
            if start <= order_date <= end:
                filtered_sales.append(sale)
        return filtered_sales

    # 기간별 매출 출력
    def show_period_sales(self):
        print("\n-기간별 매출-")
        start_date, end_date, start, end = self.input_date_range()
        filtered_sales = self.filter_date_sales(start, end)
        print(f"조회 기간 : {start_date}~{end_date}")
        if not filtered_sales:
            print("해당 기간 매출 없음")
            return
        total_sales = 0
        for sale in filtered_sales:
            total_sales += sale.total_price
        print(f"주문 건수 : {len(filtered_sales)}건")
        print(f"총 매출 : {total_sales}원")

    # 상품별 매출 출력
    def show_product_sales(self):
        print("\n-상품별 매출-")
        start_date, end_date, start, end = self.input_date_range()
        filtered_sales = self.filter_date_sales(start, end)
        product_sales = {}
        for sale in filtered_sales:
            for product in sale.products:
                name = product["name"]
                quantity = product["quantity"]
                price = product["price"] or 0
                option_price = 0
                for option in product["options"]:
                    option_price += option["price"]
                item_price = (price + option_price) * quantity
                if name not in product_sales:
                    product_sales[name] = {"quantity": 0, "sales": 0}
                product_sales[name]["quantity"] += quantity
                product_sales[name]["sales"] += item_price
        print(f"조회 기간 : {start_date}~{end_date}")
        if not product_sales:
            print("해당 기간 매출 없음")
            return
        total_sales = 0
        for name, data in sorted(product_sales.items()):
            print(f"{name} : {data['quantity']}개 / {data['sales']}원")
            total_sales += data["sales"]
        print(f"상품별 매출 합계 : {total_sales}원")

    # 카테고리별 매출 출력
    def show_category_sales(self, products):
        print("\n-카테고리별 매출-")
        start_date, end_date, start, end = self.input_date_range()
        filtered_sales = self.filter_date_sales(start, end)
        product_categories = {}
        for product in products:
            product_categories[product.name] = product.category
        category_sales = {}
        for sale in filtered_sales:
            for product in sale.products:
                name = product["name"]
                if name not in product_categories:
                    continue
                category = product_categories[name]
                quantity = product["quantity"]
                price = product["price"] or 0
                option_price = 0
                for option in product["options"]:
                    option_price += option["price"]
                item_price = (price + option_price) * quantity
                if category not in category_sales:
                    category_sales[category] = {"quantity": 0, "sales": 0}
                category_sales[category]["quantity"] += quantity
                category_sales[category]["sales"] += item_price

        print(f"조회 기간 : {start_date} ~ {end_date}")
        if not category_sales:
            print("해당 기간 매출 없음")
            return
        total_sales = 0
        for category, data in sorted(category_sales.items()):
            print(f"{category} : {data['quantity']}개 / {data['sales']}원")
            total_sales += data["sales"]
        print(f"\n카테고리별 매출 합계: {total_sales}원")

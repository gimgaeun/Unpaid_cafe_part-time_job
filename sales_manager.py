import csv
from models import Order


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
                            row["products"],
                            int(row["total_price"]),
                        )
                        self.sales.append(sale)
                    except (KeyError, ValueError):
                        print("매출 데이터 형식이 잘못됨.")
                        continue
        except FileNotFoundError:
            print()
            print(f"매출 데이터 파일을 찾을 수 없습니다: {filename}")

    # 매출 기록 파일 저장
    # def save_sales()

    # 매출 정보 조회
    # def check_sales

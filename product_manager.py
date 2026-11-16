import csv
from models import Product


class ProductManager:
    def __init__(self):
        self.products = []

    # 상품 정보 파일 읽기
    def load_products(self, filename):
        self.products = []
        try:
            with open(filename, "r", encoding="utf-8-sig", newline="") as file:
                reader = csv.DictReader(file)
                for row in reader:
                    try:
                        options = {}
                        if row["options"]:
                            option_list = row["options"].split("|")
                            for option in option_list:
                                option_name, option_price = option.split(":")
                                options[option_name] = int(option_price)

                        product = Product(
                            row["name"],
                            int(row["price"]),
                            row["category"],
                            row["sold_out"] == "1",
                            options,
                        )
                        self.products.append(product)

                    except (KeyError, ValueError):
                        print("상품 데이터 형식이 잘못됨")
                        continue

        except FileNotFoundError:
            print()
            print(f"상품 파일을 찾을 수 없습니다: {filename}")


# 상품 정보 저장
def save_products(self, filename):
    with open(filename, "w", encoding="utf-8-sig", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(
            [
                "name",
                "price",
                "category",
                "sold_out",
                "options",
            ]
        )
        for product in self.products:
            options_text = []
            for option_name, option_price in product.options.items():
                options_text.append(f"{option_name}:{option_price}")
            options_value = "|".join(options_text)
            writer.writerow(
                [
                    product.name,
                    product.price,
                    product.category,
                    1 if product.sold_out else 0,
                    options_value,
                ]
            )

    # 상품 추가
    def add_products(self):
        print("\n-상품 추가-")
        name = input("상품명을 입력 : ").strip()
        if not name:
            print("상품명을 입력")
            return
        if any(p.name == name for p in self.products):
            print("이미 존재하는 상품")
            return
        try:
            price = int(input("가격을 입력 : ").strip())
        except ValueError:
            print("가격은 숫자로 입력")
            return
        if price < 0:
            print("가격은 음수 일 수 없음")
            return

        category = input("카테고리를 입력 : ").strip()
        if not category:
            print("카테고리 입력")
            return

        product = Product(
            Product(
                name,
                price,
                category,
                False,
                {},
            )
        )
        self.products.append(product)
        print(f"{name}이 상품으로 추가됨")

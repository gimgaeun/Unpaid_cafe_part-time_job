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

    # 상품 찾기
    def find_product(self, product_name):
        for product in self.products:
            if product.name == product_name:
                return product
        return None

    # 상품 가격 수정
    def update_product_price(self):
        print("\n-상품 가격 수정-")
        name = input("수정할 상품명 : ").strip()
        product = self.find_product(name)
        if product is None:
            print("상품을 찾을 수 없음")
            return
        while True:
            try:
                price = int(input("새로운 가격 입력 : ").strip())
                if price < 0:
                    print("가격은 음수일 수 없음")
                    continue
                break
            except ValueError:
                print("가격은 숫자로 입력")
        product.price = price
        print(f"{product.name}의 가격이 {product.price}원으로 변경됨")

    # 품절 상태 변경
    def change_sold_out(self):
        print("\n-품절 상태 변경-")
        name = input("수정할 상품명 : ").strip()
        product = self.find_product(name)
        if product is None:
            print("상품을 찾을 수 없음")
            return
        if product.sold_out:
            product.sold_out = False
            print(f"{product.name} 판매 상태로 변경")
        else:
            product.sold_out = True
            print(f"{product.name} 품절 상태로 변경")

    # 상품 삭제
    def delete_product(self):
        print("\n-상품 삭제-")
        name = input("삭제할 상품명 : ").strip()
        product = self.find_product(name)
        if product is None:
            print("상품을 찾을 수 없음")
            return
        confirm = input("정말 삭제? (y/n)")
        if confirm.lower() != "y":
            print("삭제를 취소")
            return
        self.products.remove(product)
        print(f"{product.name} 삭제")

    # 카테고리 값별 리스트 분류
    def build_category_lists(self):
        category_lists = {}
        for product in self.products:
            if product.category not in category_lists:
                category_lists[product.category] = []
            category_lists[product.category].append(product)
        return category_lists

    # 상품 가격 반환
    def get_product_price(self, product):
        return product.price

    # 카테고리별 상품 정렬 (가격순)
    def sort_products(self, category_lists):
        for category in category_lists:
            category_lists[category].sort(
                key=self.get_product_price,
                reverse=True,
            )
        return category_lists

    # 카테고리별 필터링
    def filter_category(self, category):
        if category == "전체":
            return self.products
        filter_products = []
        for product in self.products:
            if product.category == category:
                filter_products.append(product)
        return filter_products

    # 상품 목록 출력
    def show_product_list(self):
        print("\n-상품 목록-")

        if not self.products:
            print("상품이 없음")
            return

        category_lists = self.build_category_lists()
        category_lists = self.sort_products(category_lists)

        for category, category_products in category_lists.items():
            print(f"\n[{category}]")

            for i, product in enumerate(category_products, 1):
                if product.sold_out:
                    print(f"{i}. {product.name} - 품절")
                else:
                    print(f"{i}. {product.name} - {product.price:,}원")

                    if product.options:
                        print("   옵션:", end=" ")

                        option_names = list(product.options.keys())

                        print(", ".join(option_names))

        print("====================")

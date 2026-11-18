class OptionManager:
    def __init__(self):
        self.selected_options = []

    # 옵션 선택
    def select_option(self, product):
        self.select_options = []
        if not product.options:
            print("옵션이 존재하지 않음")
            return self.select_options
        print(f"\n-{product.name} 옵션 선택-")
        option_names = list(product.options.key())
        for i, option_name in enumerate(option_names):
            print(f"({i + 1}.{option_name} + {product.options[option_name]}원)")
        print("0. 선택 완료")
        while True:
            try:
                choice = int(input("추가할 옵션 번호 선택 : ").strip())
                if choice < 0 or choice > len(option_name):
                    print("올바른 번호 입력")
                    continue

                if choice == 0:
                    break
                option_name = option_name[choice - 1]
                self.select_options.append(option_name)
                print(f"{option_name} 추가")
                print(f"현재 선택 옵션: {self.selected_options}")
            except ValueError:
                print("숫자를 입력하세요.")
        return self.selected_options

    # 옵션 추가
    def add_product_option(self, product_manager):
        print("\n-옵션 추가-")
        name = input("옵션을 추가할 상품명 입력 : ").strip()
        product = product_manager.find_product(name)
        if product is None:
            print("상품이 없음")
            return
        option_name = input("옵션명 입력 : ").strip()
        if not option_name:
            print("옵션명 입력")
            return
        if option_name in product.options:
            print("이미 존재하는 옵션")
            return
        try:
            option_price = int(input("금액 입력 : ").strip())
        except ValueError:
            print("가격은 숫자로 입력")
            return
        if option_price < 0:
            print("가격은 음수 일 수 없음")
            return
        product.options[option_name] = option_price
        print(f"{product.name}에 {option_name} 옵션 추가")

    # 옵션 삭제
    def delete_product_option(self, product_manager):
        print("\n-옵션 삭제-")
        name = input("옵션을 삭제할 상품명 입력 : ").strip()
        product = product_manager.find_product(name)
        if product is None:
            print("상품이 없음")
            return
        if not product.options:
            print("옵션이 존재하지 않음")
            return
        # 미완성

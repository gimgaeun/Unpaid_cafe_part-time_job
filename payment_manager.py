class PaymentManager:
    def __init__(self):
        self.payment_method = None
        self.total_price = 0
        self.input_money = 0
        self.change = 0

    # 상품 하나 가격 계산
    def calculate_item_price(self, product, options, quantity):
        option_price = 0
        for option in options:
            option_price += product.options.get(option, 0)
        return (product.price + option_price) * quantity

    # 전체 주문 금액 계산
    def calculate_total(self, order_items):
        total = 0
        for item in order_items:
            product = item["product"]
            quantity = item["quantity"]
            options = item["options"]
            item_price = self.calculate_item_price(product, options, quantity)
            total += item_price
        return total

    # 현금 결제
    def process_cash(self, input_money):
        self.payment_method = "cash"
        self.input_money = input_money
        if input_money < self.total_price:
            shortage_money = self.total_price - input_money
            print(f"{shortage_money}원 부족")
            return False
        self.change = self.input_money - self.total_price
        print("현금 결제 완료")
        print(f"거스름돈 : {self.change}원")
        return True

    # 현금 투입 및 추가 투입
    def collect_cash(self, total_price):
        self.total_price = total_price
        self.payment_method = "cash"
        accumulated_money = 0
        while True:
            try:
                add_money = int(input("투입할 현금 금액 (0: 결제 취소) : ").strip())
                if add_money == 0:
                    print("결제 취소")
                    return False
                if add_money < 0:
                    print("금액은 0 이상 입력")
                    continue
            except ValueError:
                print("금액은 숫자로 입력")
                continue
            accumulated_money += add_money
            if self.process_cash(accumulated_money):
                return True
            print("부족한 금액을 추가로 투입")

    # 카드 결제
    def process_card(self):
        self.payment_method = "card"
        print("카드 결제 완료")
        self.change = 0
        return True

    # 결제 처리
    def process_payment(self, payment_method, total_price, input_money=None):
        self.total_price = total_price
        if payment_method == "cash":
            if input_money is None:
                print("현금 투입 금액 없음")
                return False
            return self.process_cash(input_money)
        if payment_method == "card":
            return self.process_card()
        print("잘못된 결제 수단")
        return False

    # 결제 금액 출력
    def show_price_total(self, order_items):
        self.total_price = self.calculate_total(order_items)
        print(f"총 결제 금액 : {self.total_price}원")
        return self.total_price

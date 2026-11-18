from models import Product
from payment_manager import PaymentManager


# 테스트용 상품
americano = Product(
    "아메리카노",
    2000,
    "커피",
    False,
    {
        "샷 추가": 500,
        "시럽 추가": 300,
    },
)

latte = Product(
    "카페라떼",
    3200,
    "커피",
    False,
    {
        "샷 추가": 500,
    },
)


# 테스트용 주문 목록
order_items = [
    {
        "product": americano,
        "quantity": 2,
        "options": ["샷 추가"],
    },
    {
        "product": latte,
        "quantity": 1,
        "options": [],
    },
]


payment_manager = PaymentManager()


print("================================")
print("      PaymentManager 테스트")
print("================================")


# 1. 상품 하나 가격 계산
print("\n[1. 상품 하나 가격 계산 테스트]")

item_price = payment_manager.calculate_item_price(
    americano,
    ["샷 추가"],
    2,
)

print("상품: 아메리카노")
print("수량: 2")
print("옵션: 샷 추가")
print(f"계산된 금액: {item_price:,}원")


# 2. 전체 주문 금액 계산
print("\n[2. 전체 주문 금액 계산 테스트]")

total_price = payment_manager.calculate_total(order_items)

print(f"전체 주문 금액: {total_price:,}원")


# 3. 결제 금액 출력
print("\n[3. 결제 금액 출력 테스트]")

total_price = payment_manager.show_price_total(order_items)


# 4. 현금 결제 성공
print("\n[4. 현금 결제 성공 테스트]")

success = payment_manager.process_payment(
    "cash",
    total_price,
    10000,
)

print("결제 성공 여부:", success)


# 5. 현금 부족
print("\n[5. 현금 부족 테스트]")

success = payment_manager.process_payment(
    "cash",
    total_price,
    5000,
)

print("결제 성공 여부:", success)


# 6. 카드 결제
print("\n[6. 카드 결제 테스트]")

success = payment_manager.process_payment(
    "card",
    total_price,
)

print("결제 성공 여부:", success)


# 7. 잘못된 결제 방식
print("\n[7. 잘못된 결제 방식 테스트]")

success = payment_manager.process_payment(
    "bitcoin",
    total_price,
)

print("결제 성공 여부:", success)


print("\n================================")
print("          테스트 종료")
print("================================")

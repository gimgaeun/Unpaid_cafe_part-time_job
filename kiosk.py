import threading
from datetime import datetime

from models import Order, OrderItem
from product_manager import ProductManager
from order_manager import OrderManager
from payment_manager import PaymentManager
from receipt_manager import ReceiptManager
from signal_manager import SignalManager
from option_manager import OptionManager


class Kiosk:
    def __init__(self):
        self.product_manager = ProductManager()
        self.order_manager = OrderManager()
        self.payment_manager = PaymentManager()
        self.receipt_manager = ReceiptManager()
        self.signal_manager = SignalManager()
        self.option_manager = OptionManager()

        self.products_file = "data/products.csv"
        self.orders_file = "data/orders.csv"
        self.sales_file = "data/sales.csv"
        self.running = True

        self.order_items = []

    # 상품 정보 새로 불러오기
    def refresh_products(self):
        print("\n상품 정보가 변경되었습니다.")

        self.product_manager.load_products(self.products_file)

        print("상품 목록을 새로 불러왔습니다.")

    # 신호 검사 시작
    def start_signal_check(self):
        self.signal_manager.init_signal()
        signal_thread = threading.Thread(
            target=self.signal_manager.check_signal,
            args=(self.refresh_products,),
            kwargs={"interval": 0.7},
            daemon=True,
        )
        signal_thread.start()

    # 상품 보기
    def show_products(self):
        while True:
            print("\n===== 상품 목록 =====")
            categories = ["전체"]
            for product in self.product_manager.products:
                if product.category not in categories:
                    categories.append(product.category)
            for i, category in enumerate(categories, 1):
                print(f"{i}. {category}")
            print("0. 뒤로가기")
            try:
                choice = int(input("카테고리 번호 선택 : ").strip())
                if choice == 0:
                    return
                if choice < 1 or choice > len(categories):
                    print("올바른 번호 입력")
                    continue
            except ValueError:
                print("숫자 입력")
                continue
            selected_category = categories[choice - 1]
            target_products = self.product_manager.filter_category(selected_category)
            print(f"\n[{selected_category} 상품]")
            if not target_products:
                print("표시할 상품이 없습니다.")
                continue
            for i, product in enumerate(target_products, 1):
                if product.sold_out:
                    print(f"{i}. {product.name} - 품절")
                else:
                    print(f"{i}. {product.name} - {product.price}원")
                    if product.options:
                        option_text = ", ".join(
                            f"{k}(+{v}원)" for k, v in product.options.items()
                        )
                        print(f"   옵션: {option_text}")

    # 상품 장바구니 담기
    def add_product_to_cart(self):
        available_products = [
            product for product in self.product_manager.products if not product.sold_out
        ]
        if not available_products:
            print("\n주문 가능한 상품 없음")
            return
        print("\n===== 주문할 상품 선택 =====")
        for i, product in enumerate(available_products, 1):
            print(f"{i}. {product.name} - {product.price}원")
        print("0. 취소")
        try:
            choice = int(input("상품 번호 선택 : ").strip())
        except ValueError:
            print("숫자 입력")
            return
        if choice == 0:
            print("상품 선택을 취소")
            return
        if choice < 1 or choice > len(available_products):
            print("올바른 번호 입력")
            return
        selected_product = available_products[choice - 1]
        selected_options = list(self.option_manager.select_option(selected_product))
        try:
            quantity = int(input("수량 입력 : ").strip())
        except ValueError:
            print("수량은 숫자로 입력하세요.")
            return
        if not self.order_manager.check_order_limit(self.order_items, quantity):
            return
        for item in self.order_items:
            if (
                item["product"].name == selected_product.name
                and item["options"] == selected_options
            ):
                if not self.order_manager.check_order_limit(
                    [i for i in self.order_items if i is not item],
                    item["quantity"] + quantity,
                ):
                    return
                item["quantity"] += quantity
                print(
                    f"{selected_product.name} 수량이 {item['quantity']}개로 변경되었습니다."
                )
                return
        self.order_items.append(
            {
                "product": selected_product,
                "quantity": quantity,
                "options": selected_options,
            }
        )
        print(f"{selected_product.name} {quantity}개가 장바구니에 담겼습니다.")

    # 장바구니 비우기
    def clear_cart(self):
        if not self.order_items:
            print("\n장바구니가 이미 비어 있음")
            return
        confirm = input("장바구니를 모두 비울까요? (y/n) : ").strip().lower()
        if confirm == "y":
            self.order_items.clear()
            print("장바구니를 비움")
        else:
            print("취소 완료")

    # 결제 및 주문 저장
    def checkout(self):
        if not self.order_items:
            print("\n장바구니가 비어 있음")
            return
        self.order_manager.show_cart_items(self.order_items)
        total_price = self.payment_manager.show_price_total(self.order_items)
        print("\n결제 수단을 선택")
        print("1. 카드 결제")
        print("2. 현금 결제")
        print("0. 결제 취소")
        method_choice = input("선택 : ").strip()
        if method_choice == "0":
            print("결제를 취소했습니다.")
            return
        if method_choice == "1":
            paid = self.payment_manager.process_payment("card", total_price)
        elif method_choice == "2":
            paid = self.payment_manager.collect_cash(total_price)
        else:
            print("잘못된 선택입니다.")
            return
        if not paid:
            print("결제에 실패했습니다.")
            return

        self.order_manager.load_order(self.orders_file)
        order_id = self.order_manager.get_next_order_id(
            self.orders_file, self.sales_file
        )
        order_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        products_text = self.order_manager.make_products_text(self.order_items)
        self.order_manager.create_order(
            order_id, order_time, products_text, total_price
        )
        saved = self.order_manager.save_orders(
            self.orders_file, self.order_manager.orders, retries=3
        )
        receipt_items = [
            OrderItem(item["product"], item["quantity"], list(item["options"]))
            for item in self.order_items
        ]
        receipt_order = Order(order_id, order_time, receipt_items, total_price)
        if not saved:
            print(
                "주문 저장 중 오류가 발생했습니다. 포스기 직원에게 직접 문의해 주세요."
            )
            self.receipt_manager.print_order_slip(receipt_order)
            self.order_items.clear()
            return

        payment_method = "card" if method_choice == "1" else "cash"
        change = self.payment_manager.change if payment_method == "cash" else None
        self.signal_manager.update_signal()
        self.receipt_manager.print_order_slip(receipt_order)
        try:
            slip_path = self.receipt_manager.save_order_slip_txt(receipt_order)
            print(f"주문표 파일 저장 완료: {slip_path}")
        except OSError:
            print("주문표 텍스트 파일 저장 실패")

        want_recipt = input("영수증 여부 (y/n) : ").strip().lower()
        if want_recipt == "y":
            self.receipt_manager.print_recipt(
                receipt_order, payment_method=payment_method, change=change
            )
            try:
                receipt_path = self.receipt_manager.save_receipt_txt(
                    receipt_order, payment_method=payment_method, change=change
                )
                print(f"영수증 파일 저장 완료: {receipt_path}")
            except OSError:
                print("영수증 텍스트 파일 저장에 실패했습니다.")
        self.order_items.clear()
        print("주문이 정상적으로 접수")

    # 메뉴 출력
    def show_menu(self):
        print("\n===== 카페 키오스크 =====")
        print("1. 상품 목록 보기")
        print("2. 상품 담기")
        print("3. 장바구니 확인")
        print("4. 장바구니 비우기")
        print("5. 결제하기")
        print("0. 종료")
        print("========================")

    # 실행
    def run(self):
        self.product_manager.load_products(self.products_file)
        self.start_signal_check()
        try:
            while self.running:
                self.show_menu()
                choice = input("메뉴 선택 : ").strip()
                if choice == "1":
                    self.show_products()
                elif choice == "2":
                    self.add_product_to_cart()
                elif choice == "3":
                    self.order_manager.show_cart_items(self.order_items)
                    if self.order_items:
                        self.payment_manager.show_price_total(self.order_items)
                elif choice == "4":
                    self.clear_cart()
                elif choice == "5":
                    self.checkout()
                elif choice == "0":
                    print("키오스크 종료")
                    self.running = False
                else:
                    print("올바른 메뉴 번호 입력")
        finally:
            self.signal_manager.stop()


if __name__ == "__main__":
    app = Kiosk()
    app.run()

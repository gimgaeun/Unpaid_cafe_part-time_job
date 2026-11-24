import threading
from datetime import datetime

from product_manager import ProductManager
from order_manager import OrderManager
from payment_manager import PaymentManager
from signal_manager import SignalManager
from option_manager import OptionManager
from sales_manager import SalesManager


class Pos:
    def __init__(self):
        self.product_manager = ProductManager()
        self.order_manager = OrderManager()
        self.payment_manager = PaymentManager()
        self.signal_manager = SignalManager()
        self.option_manager = OptionManager()
        self.sales_manager = SalesManager()

        self.products_file = "data/products.csv"
        self.orders_file = "data/orders.csv"
        self.sales_file = "data/sales.csv"
        self.running = True

        self.active_orders = []

    # 현재 대기 주문 목록 출력
    def show_order_list(self):
        print("\n====== 주문 내역 ======")
        print(f"대기 주문 수: {len(self.active_orders)}건")
        if not self.active_orders:
            print("현재 대기 중인 주문 없음")
            return
        for order in self.active_orders:
            print(f"[주문 번호 : {order.order_id}] (주문시간 : {order.order_time})")
            if not order.products:
                print(" - 상품 정보 없음")
            else:
                for product in order.products:
                    option_names = [
                        option["name"] for option in product.get("options", [])
                    ]
                    option_text = (
                        f" (옵션: {', '.join(option_names)})" if option_names else ""
                    )
                    print(f"  - {product['name']} x {product['quantity']}{option_text}")
            print(f"  총 금액: {order.total_price}원")

    # 새 주문 신호 감지
    def refresh_orders(self):
        self.active_orders = self.order_manager.load_order(self.orders_file)
        self.show_order_list()

    # 신호 검사 시작
    def start_signal_check(self):
        self.signal_manager.init_signal()
        signal_thread = threading.Thread(
            target=self.signal_manager.check_signal,
            args=(self.refresh_orders,),
            kwargs={"interval": 0.7},
            daemon=True,
        )
        signal_thread.start()

    # 주문 완료 처리
    def complete_order_menu(self):
        self.active_orders = self.order_manager.load_order(self.orders_file)
        self.show_order_list()
        if not self.active_orders:
            return
        try:
            order_id = int(input("\n완료 처리할 주문번호 입력 (0: 취소) : ").strip())
        except ValueError:
            print("숫자를 입력")
            return
        if order_id == 0:
            print("주문 완료 처리 취소")
            return
        today_str = datetime.now().strftime("%Y-%m-%d")
        target_date = None
        for order in self.active_orders:
            if order.order_id == order_id:
                order_date = self.order_manager.extract_date_str(order.order_time)
                if order_date == today_str:
                    target_date = today_str
                    break
                if target_date is None:
                    target_date = order_date
        done = self.order_manager.complete_order(
            order_id, self.orders_file, self.sales_file
        )
        if done:
            self.active_orders = self.order_manager.load_order(self.orders_file)
            self.show_order_list()

    def _apply_product_change(self, action):
        action()
        self.product_manager.save_products(self.products_file)
        self.signal_manager.update_signal()

    # 메뉴 관리
    def manage_menu(self):
        while True:
            print("\n===== 메뉴 관리 =====")
            print("1. 상품 목록 보기")
            print("2. 상품 추가")
            print("3. 상품 이름 수정")
            print("4. 상품 가격 수정")
            print("5. 품절 상태 변경")
            print("6. 상품 삭제")
            print("7. 옵션 추가")
            print("8. 옵션 삭제")
            print("0. 뒤로가기")
            print("===================")
            choice = input("메뉴 선택 : ").strip()
            if choice == "0":
                return
            if choice == "1":
                self.product_manager.show_product_list()
            elif choice == "2":
                self._apply_product_change(self.product_manager.add_products)
            elif choice == "3":
                self._apply_product_change(self.product_manager.update_product_name)
            elif choice == "4":
                self._apply_product_change(self.product_manager.update_product_price)
            elif choice == "5":
                self._apply_product_change(self.product_manager.change_sold_out)
            elif choice == "6":
                self._apply_product_change(self.product_manager.delete_product)
            elif choice == "7":
                self._apply_product_change(
                    lambda: self.option_manager.add_product_option(self.product_manager)
                )
            elif choice == "8":
                self._apply_product_change(
                    lambda: self.option_manager.delete_product_option(
                        self.product_manager
                    )
                )
            else:
                print("올바른 번호를 입력")

    def analysis_menu(self):
        self.sales_manager.load_sales(self.sales_file)
        while True:
            print("\n===== 매출 분석 =====")
            print("1. 전체 매출 확인")
            print("2. 기간별 매출 조회")
            print("3. 상품별 매출 조회")
            print("4. 카테고리별 매출 조회")
            print("0. 뒤로가기")
            choice = input("메뉴 선택 : ").strip()
            if choice == "0":
                return
            elif choice == "1":
                self.sales_manager.check_sales()
            elif choice == "2":
                self.sales_manager.show_period_sales()
            elif choice == "3":
                self.sales_manager.show_product_sales()
            elif choice == "4":
                self.sales_manager.show_category_sales(self.product_manager.products)
            else:
                print("올바른 번호를 입력")

    def show_menu(self):
        print("\n===== 카페 포스기 =====")
        print("1. 주문 내역 보기")
        print("2. 주문 완료 처리")
        print("3. 메뉴 관리")
        print("4. 매출 분석")
        print("5. 직접 결제")
        print("0. 종료")
        print("=======================")

    # 직접 결제 상품 선택
    def collect_direct_items(self):
        available_products = [
            product for product in self.product_manager.products if not product.sold_out
        ]
        if not available_products:
            print("주문 가능한 상품 없음")
            return []
        direct_items = []
        while True:
            print("\n===== 직접 결제 상품 선택 =====")
            for i, product in enumerate(available_products, 1):
                print(f"{i}. {product.name} - {product.price}원")
            print("0. 상품 선택 완료")
            try:
                choice = int(input("상품 번호 선택 : ").strip())
            except ValueError:
                print("숫자를 입력")
                continue
            if choice == 0:
                break
            if choice < 1 or choice > len(available_products):
                print("올바른 번호를 입력")
                continue
            selected_product = available_products[choice - 1]
            selected_options = list(self.option_manager.select_option(selected_product))
            try:
                quantity = int(input("수량 입력 : ").strip())
            except ValueError:
                print("수량은 숫자로 입력")
                continue
            if not self.order_manager.check_order_limit(direct_items, quantity):
                continue

            direct_items.append(
                {
                    "product": selected_product,
                    "quantity": quantity,
                    "options": selected_options,
                }
            )
            print(f"{selected_product.name} {quantity}개 추가")
        return direct_items

    # 직접 결제 수단 선택 및 결제
    def direct_payment(self, total_price):
        print("\n결제 수단 선택")
        print("1. 카드 결제")
        print("2. 현금 결제")
        print("0. 취소")
        method = input("선택 : ").strip()
        if method == "0":
            print("직접 결제를 취소했습니다.")
            return False
        if method == "1":
            return self.payment_manager.process_payment("card", total_price)
        if method == "2":
            return self.payment_manager.collect_cash(total_price)

        print("잘못된 선택입니다.")
        return False

    # 주문 저장
    def save_direct_order(self, items, total_price):
        self.order_manager.load_order(self.orders_file)
        order_id = self.order_manager.get_next_order_id(
            self.orders_file, self.sales_file
        )
        order_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        products_text = self.order_manager.make_products_text(items)
        self.order_manager.create_order(
            order_id, order_time, products_text, total_price
        )
        if not self.order_manager.save_orders(
            self.orders_file, self.order_manager.orders, retries=3
        ):
            print("주문 저장 실패")
            return False
        self.signal_manager.update_signal()
        self.refresh_orders()
        return True

    # 직접 결제
    def pay_direct(self):
        direct_items = self.collect_direct_items()
        if not direct_items:
            print("선택한 상품이 없어 결제를 취소")
            return
        self.order_manager.show_cart_items(direct_items)
        total_price = self.payment_manager.show_price_total(direct_items)
        if not self.direct_payment(total_price):
            print("결제 실패")
            return
        self.save_direct_order(direct_items, total_price)

    # 실행
    def run(self):
        self.product_manager.load_products(self.products_file)
        self.refresh_orders()
        self.start_signal_check()
        try:
            while self.running:
                self.show_menu()
                choice = input("메뉴 선택 : ").strip()
                if choice == "1":
                    self.show_order_list()
                elif choice == "2":
                    self.complete_order_menu()
                elif choice == "3":
                    self.manage_menu()
                elif choice == "4":
                    self.analysis_menu()
                elif choice == "5":
                    self.pay_direct()
                elif choice == "0":
                    print("포스기 종료")
                    self.running = False
                else:
                    print("올바른 번호를 입력")
        finally:
            self.signal_manager.stop()


if __name__ == "__main__":
    app = Pos()
    app.run()

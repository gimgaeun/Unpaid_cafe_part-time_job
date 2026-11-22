import os


class ReceiptManager:
    def __init__(self, output_dir="data/receipts"):
        self.output_dir = output_dir

    def format_payment_method(self, payment_method):
        if payment_method == "card":
            return "카드 결제"
        if payment_method == "cash":
            return "현금 결제"
        return payment_method or "미지정"

    # txt 파일 쓰기
    def write_txt(self, filename, content):
        os.makedirs(self.output_dir, exist_ok=True)
        filepath = os.path.join(self.output_dir, filename)
        with open(filepath, "w", encoding="utf-8-sig") as file:
            file.write(content)
        return filepath

    # 주문표 내용 만들기
    def make_order_slip(self, order):
        lines = [
            "================================",
            "             주문표",
            "================================",
            f"주문번호: {order.order_id}",
            f"주문시간: {order.order_time}",
            "--------------------------------",
        ]
        for item in order.products:
            options_text = ", ".join(item.options) if item.options else "없음"
            lines.append(f"{item.product.name} x {item.quantity}")
            lines.append(f"  옵션: {options_text}")
        lines.append("================================")
        return "\n".join(lines)

    # 영수증 내용 만들기
    def make_receipt(self, order, payment_method=None, change=None):
        lines = [
            "================================",
            "          카페 영수증",
            "================================",
            f"주문번호: {order.order_id}",
            f"주문시간: {order.order_time}",
            "--------------------------------",
        ]
        for item in order.products:
            product = item.product
            quantity = item.quantity
            options = item.options
            lines.append(f"{product.name} x {quantity}")
            if options:
                option_names = []
                item_price = product.price
                for option_name in options:
                    option_price = product.options.get(option_name, 0)
                    option_names.append(f"{option_name} (+{option_price}원)")
                    item_price += option_price
                lines.append(f"  옵션: {', '.join(option_names)}")
            else:
                lines.append("  옵션: 없음")
                item_price = product.price
            lines.append(f"  금액: {item_price * quantity}원")

        lines.extend(
            [
                "--------------------------------",
                f"결제수단: {self.format_payment_method(payment_method)}",
            ]
        )
        if payment_method == "cash" and change is not None:
            lines.append(f"거스름돈: {change}원")
        lines.extend(
            [
                "--------------------------------",
                f"총 결제 금액: {order.total_price}원",
                "================================",
                "    이용해 주셔서 감사합니다.     ",
                "================================",
            ]
        )
        return "\n".join(lines)

    # 주문표 txt 저장
    def save_order_slip_txt(self, order):
        filename = f"order_slip_{order.order_id}.txt"
        return self.write_txt(filename, self.make_order_slip(order))

    # 영수증 txt 저장
    def save_receipt_txt(self, order, payment_method=None, change=None):
        filename = f"receipt_{order.order_id}.txt"
        content = self.make_receipt(order, payment_method=payment_method, change=change)
        return self.write_txt(filename, content)

    # 주문표 출력
    def print_order_slip(self, order):
        print(f"\n{self.make_order_slip(order)}")

    # 영수증 출력
    def print_recipt(self, order, payment_method=None, change=None):
        print(
            f"\n{self.make_receipt(order, payment_method=payment_method, change=change)}"
        )

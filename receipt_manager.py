class ReceiptManager:
    # 영수증 내용 만들기
    def make_receipt(self, order):
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
            product_name = product.name
            quantity = item.quantity
            options = item.options

            lines.append(f"{product_name} x {quantity}")

            if options:
                option_names = []

                for option_name in options:
                    option_price = product.options[option_name]

                    option_names.append(f"{option_name} (+{option_price}원)")

                lines.append(f"  옵션: {', '.join(option_names)}")

                item_price = product.price

                for option_name in options:
                    item_price += product.options[option_name]

            else:
                lines.append("  옵션: 없음")

                item_price = product.price

            lines.append(f"  금액: {item_price * quantity}원")

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

    # 영수증 출력
    def print_recipt(self, order):
        print(f"\n{self.make_receipt(order)}")

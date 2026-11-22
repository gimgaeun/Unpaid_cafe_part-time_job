import os
import threading
import tkinter as tk
from datetime import datetime
from tkinter import messagebox, simpledialog, ttk

try:
    from PIL import Image, ImageTk

    HAS_PIL = True
except ImportError:
    HAS_PIL = False

from models import Order, OrderItem
from option_manager import OptionManager
from order_manager import OrderManager
from payment_manager import PaymentManager
from product_manager import ProductManager
from receipt_manager import ReceiptManager
from signal_manager import SignalManager


class KioskUI:
    def __init__(self, root):
        self.root = root
        self.root.title("카페 키오스크")
        self.root.geometry("1120x720")
        self.root.configure(bg="#f5f6f8")

        self.product_manager = ProductManager()
        self.order_manager = OrderManager()
        self.payment_manager = PaymentManager()
        self.receipt_manager = ReceiptManager()
        self.signal_manager = SignalManager()
        self.option_manager = OptionManager()

        self.products_file = "data/products.csv"
        self.orders_file = "data/orders.csv"
        self.sales_file = "data/sales.csv"
        self.images_dir = "data/images"

        self.selected_category = "전체"
        self.order_items = []  # {"product": Product, "quantity": int, "options": list[str]}
        self.photo_images = []  # PhotoImage 가비지 컬렉션 방지용 참조 보관
        self.running = True

        self._build_layout()
        self.reload_products_and_ui()
        self.start_signal_check()
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    # ---------------- 이미지 로딩 헬퍼 ----------------
    def _load_product_image(self, product_name, width=180, height=105):
        image_path = os.path.join(self.images_dir, f"{product_name}.png")
        if not os.path.isfile(image_path):
            return None

        try:
            if HAS_PIL:
                pil_img = Image.open(image_path)
                pil_img = pil_img.resize((width, height), Image.Resampling.LANCZOS)
                tk_img = ImageTk.PhotoImage(pil_img)
            else:
                tk_img = tk.PhotoImage(file=image_path)
            self.photo_images.append(tk_img)
            return tk_img
        except Exception:
            return None

    # ---------------- 레이아웃 구성 ([3.2] 인터페이스 설계 반영) ----------------
    def _build_layout(self):
        self.main_container = tk.Frame(self.root, bg="#f5f6f8")
        self.main_container.pack(fill=tk.BOTH, expand=True)

        # 1. 키오스크 – 메인 화면
        self.order_frame = tk.Frame(self.main_container, bg="#f5f6f8")
        self.order_frame.pack(fill=tk.BOTH, expand=True)

        left_frame = tk.Frame(self.order_frame, bg="#f5f6f8")
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(14, 8), pady=14)

        self.category_bar = tk.Frame(left_frame, bg="#f5f6f8")
        self.category_bar.pack(fill=tk.X, pady=(0, 12))

        product_canvas_wrap = tk.Frame(left_frame, bg="#f5f6f8")
        product_canvas_wrap.pack(fill=tk.BOTH, expand=True)

        self.product_canvas = tk.Canvas(
            product_canvas_wrap, bg="#f5f6f8", highlightthickness=0
        )
        scrollbar = ttk.Scrollbar(
            product_canvas_wrap, orient=tk.VERTICAL, command=self.product_canvas.yview
        )
        self.product_grid_frame = tk.Frame(self.product_canvas, bg="#f5f6f8")

        self.product_grid_frame.bind(
            "<Configure>",
            lambda e: self.product_canvas.configure(
                scrollregion=self.product_canvas.bbox("all")
            ),
        )
        self.canvas_window = self.product_canvas.create_window(
            (0, 0), window=self.product_grid_frame, anchor="nw"
        )
        self.product_canvas.bind("<Configure>", self._on_canvas_configure)
        self.product_canvas.configure(yscrollcommand=scrollbar.set)

        self.product_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # 우측 주문 목록 패널
        right_frame = tk.Frame(
            self.order_frame,
            bg="#ffffff",
            width=320,
            highlightbackground="#d9dfe6",
            highlightthickness=1,
        )
        right_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(8, 14), pady=14)
        right_frame.pack_propagate(False)

        tk.Label(
            right_frame,
            text="주문 목록",
            font=("맑은 고딕", 15, "bold"),
            bg="#ffffff",
            fg="#1f2937",
            anchor="w",
        ).pack(fill=tk.X, padx=16, pady=(16, 10))

        ttk.Separator(right_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, padx=12)

        cart_wrap = tk.Frame(right_frame, bg="#ffffff")
        cart_wrap.pack(fill=tk.BOTH, expand=True, padx=12, pady=8)

        self.cart_canvas = tk.Canvas(cart_wrap, bg="#ffffff", highlightthickness=0)
        cart_scroll = ttk.Scrollbar(
            cart_wrap, orient=tk.VERTICAL, command=self.cart_canvas.yview
        )
        self.cart_items_frame = tk.Frame(self.cart_canvas, bg="#ffffff")
        self.cart_items_frame.bind(
            "<Configure>",
            lambda e: self.cart_canvas.configure(
                scrollregion=self.cart_canvas.bbox("all")
            ),
        )
        self.cart_canvas.create_window(
            (0, 0), window=self.cart_items_frame, anchor="nw"
        )
        self.cart_canvas.configure(yscrollcommand=cart_scroll.set)
        self.cart_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        cart_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        ttk.Separator(right_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, padx=12)

        bottom_panel = tk.Frame(right_frame, bg="#ffffff")
        bottom_panel.pack(fill=tk.X, padx=16, pady=14)

        total_row = tk.Frame(bottom_panel, bg="#ffffff")
        total_row.pack(fill=tk.X, pady=(0, 12))

        tk.Label(
            total_row,
            text="합계",
            font=("맑은 고딕", 13),
            bg="#ffffff",
            fg="#374151",
        ).pack(side=tk.LEFT)

        self.total_label = tk.Label(
            total_row,
            text="0원",
            font=("맑은 고딕", 16, "bold"),
            bg="#ffffff",
            fg="#111827",
        )
        self.total_label.pack(side=tk.RIGHT)

        self.pay_button = tk.Button(
            bottom_panel,
            text="결제하기",
            font=("맑은 고딕", 13, "bold"),
            bg="#2b7de9",
            fg="#ffffff",
            activebackground="#1d63c2",
            activeforeground="#ffffff",
            relief=tk.FLAT,
            height=2,
            cursor="hand2",
            command=self.open_payment_screen,
        )
        self.pay_button.pack(fill=tk.X)

        # 2. 키오스크 – 결제 화면
        self.payment_frame = tk.Frame(self.main_container, bg="#f3f4f6")
        self._build_payment_screen()

    def _on_canvas_configure(self, event):
        self.product_canvas.itemconfig(self.canvas_window, width=event.width)

    def _build_payment_screen(self):
        center_box = tk.Frame(self.payment_frame, bg="#f3f4f6")
        center_box.place(relx=0.5, rely=0.45, anchor="center")

        tk.Label(
            center_box,
            text="결제 방법을 선택해 주세요",
            font=("맑은 고딕", 20, "bold"),
            bg="#f3f4f6",
            fg="#1f2937",
        ).pack(pady=(0, 32))

        btn_row = tk.Frame(center_box, bg="#f3f4f6")
        btn_row.pack()

        tk.Button(
            btn_row,
            text="현금 결제",
            font=("맑은 고딕", 18, "bold"),
            bg="#ffffff",
            fg="#2b7de9",
            activebackground="#eef4fc",
            activeforeground="#1d63c2",
            highlightbackground="#2b7de9",
            highlightthickness=1,
            width=18,
            height=5,
            cursor="hand2",
            command=lambda: self.handle_payment("cash"),
        ).pack(side=tk.LEFT, padx=16)

        tk.Button(
            btn_row,
            text="카드 결제",
            font=("맑은 고딕", 18, "bold"),
            bg="#ffffff",
            fg="#2b7de9",
            activebackground="#eef4fc",
            activeforeground="#1d63c2",
            highlightbackground="#2b7de9",
            highlightthickness=1,
            width=18,
            height=5,
            cursor="hand2",
            command=lambda: self.handle_payment("card"),
        ).pack(side=tk.LEFT, padx=16)

        back_bar = tk.Frame(self.payment_frame, bg="#f3f4f6")
        back_bar.pack(side=tk.BOTTOM, fill=tk.X, padx=24, pady=20)

        tk.Button(
            back_bar,
            text="뒤로가기",
            font=("맑은 고딕", 12),
            bg="#ffffff",
            fg="#1f2937",
            activebackground="#e5e7eb",
            highlightbackground="#cbd5e1",
            highlightthickness=1,
            width=12,
            height=2,
            cursor="hand2",
            command=self.show_order_screen,
        ).pack(side=tk.RIGHT)

    # ---------------- 신호 및 상품 갱신 ----------------
    def start_signal_check(self):
        self.signal_manager.init_signal()

        def on_changed():
            if self.running:
                self.root.after(0, self.reload_products_and_ui)

        thread = threading.Thread(
            target=self.signal_manager.check_signal,
            args=(on_changed,),
            kwargs={"interval": 0.7},
            daemon=True,
        )
        thread.start()

    def reload_products_and_ui(self):
        self.photo_images.clear()
        self.product_manager.load_products(self.products_file)
        self.render_categories()
        self.render_products()
        self.render_cart()

    def render_categories(self):
        for widget in self.category_bar.winfo_children():
            widget.destroy()

        categories = ["전체"]
        for product in self.product_manager.products:
            if product.category not in categories:
                categories.append(product.category)

        if self.selected_category not in categories:
            self.selected_category = "전체"

        for cat in categories:
            is_selected = cat == self.selected_category
            btn = tk.Button(
                self.category_bar,
                text=cat,
                font=("맑은 고딕", 12, "bold" if is_selected else "normal"),
                bg="#2b7de9" if is_selected else "#ffffff",
                fg="#ffffff" if is_selected else "#1f2937",
                activebackground="#2b7de9",
                activeforeground="#ffffff",
                relief=tk.FLAT,
                highlightbackground="#cbd5e1",
                highlightthickness=1,
                padx=18,
                pady=8,
                cursor="hand2",
                command=lambda c=cat: self.select_category(c),
            )
            btn.pack(side=tk.LEFT, padx=(0, 8))

    def select_category(self, category):
        self.selected_category = category
        self.render_categories()
        self.render_products()

    def render_products(self):
        for widget in self.product_grid_frame.winfo_children():
            widget.destroy()

        products = self.product_manager.filter_category(self.selected_category)
        if not products:
            tk.Label(
                self.product_grid_frame,
                text="표시할 상품이 없습니다.",
                font=("맑은 고딕", 13),
                bg="#f5f6f8",
                fg="#6b7280",
            ).pack(pady=40)
            return

        cols = 3
        for idx, product in enumerate(products):
            row = idx // cols
            col = idx % cols

            card = tk.Frame(
                self.product_grid_frame,
                bg="#ffffff",
                highlightbackground="#e5e7eb",
                highlightthickness=1,
                padx=12,
                pady=12,
            )
            card.grid(row=row, column=col, padx=6, pady=6, sticky="nsew")
            self.product_grid_frame.grid_columnconfigure(col, weight=1, uniform="prod")

            img_box = tk.Frame(card, bg="#e5e7eb", height=110)
            img_box.pack(fill=tk.X)
            img_box.pack_propagate(False)

            tk_img = self._load_product_image(product.name, width=190, height=104)
            if tk_img is not None:
                img_label = tk.Label(img_box, image=tk_img, bg="#e5e7eb")
                img_label.image = tk_img
                img_label.place(relx=0.5, rely=0.5, anchor="center")
            else:
                tk.Label(
                    img_box,
                    text="음식 이미지",
                    font=("맑은 고딕", 11),
                    bg="#e5e7eb",
                    fg="#6b7280",
                ).place(relx=0.5, rely=0.5, anchor="center")

            info_row = tk.Frame(card, bg="#ffffff")
            info_row.pack(fill=tk.X, pady=(10, 8))

            tk.Label(
                info_row,
                text=product.name,
                font=("맑은 고딕", 12, "bold"),
                bg="#ffffff",
                fg="#111827",
                anchor="w",
            ).pack(side=tk.LEFT)

            price_text = "품절" if product.sold_out else f"{product.price:,}원"
            tk.Label(
                info_row,
                text=price_text,
                font=("맑은 고딕", 12, "bold"),
                bg="#ffffff",
                fg="#dc2626" if product.sold_out else "#111827",
            ).pack(side=tk.RIGHT)

            btn_text = "품절" if product.sold_out else "주문하기"
            btn_bg = "#9ca3af" if product.sold_out else "#2b7de9"
            tk.Button(
                card,
                text=btn_text,
                font=("맑은 고딕", 11, "bold"),
                bg=btn_bg,
                fg="#ffffff",
                activebackground=btn_bg,
                activeforeground="#ffffff",
                relief=tk.FLAT,
                state=tk.DISABLED if product.sold_out else tk.NORMAL,
                cursor="hand2" if not product.sold_out else "arrow",
                command=lambda p=product: self.on_click_order_product(p),
            ).pack(fill=tk.X, ipady=4)

    # ---------------- 주문 담기 및 목록 관리 ----------------
    def on_click_order_product(self, product):
        if product.sold_out:
            messagebox.showwarning("품절", f"{product.name}은(는) 현재 품절입니다.")
            return

        selected_options = []
        if product.options:
            selected_options = self._ask_options_dialog(product)
            if selected_options is None:
                return

        if not self.order_manager.check_order_limit(self.order_items, 1):
            messagebox.showwarning("주문 제한", "주문 수량 제한을 초과했습니다.")
            return

        for item in self.order_items:
            if (
                item["product"].name == product.name
                and item["options"] == selected_options
            ):
                if not self.order_manager.check_order_limit(
                    [i for i in self.order_items if i is not item],
                    item["quantity"] + 1,
                ):
                    messagebox.showwarning(
                        "주문 제한", "주문 수량 제한을 초과했습니다."
                    )
                    return
                item["quantity"] += 1
                self.render_cart()
                return

        self.order_items.append(
            {
                "product": product,
                "quantity": 1,
                "options": selected_options,
            }
        )
        self.render_cart()

    def _ask_options_dialog(self, product):
        dialog = tk.Toplevel(self.root)
        dialog.title(f"{product.name} 옵션 선택")
        dialog.geometry("340x320")
        dialog.transient(self.root)
        dialog.grab_set()

        tk.Label(
            dialog,
            text=f"{product.name} 옵션을 선택하세요",
            font=("맑은 고딕", 13, "bold"),
        ).pack(pady=(14, 8))

        vars_map = {}
        for opt_name, opt_price in product.options.items():
            var = tk.BooleanVar(value=False)
            tk.Checkbutton(
                dialog,
                text=f"{opt_name} (+{opt_price:,}원)",
                font=("맑은 고딕", 11),
                variable=var,
                anchor="w",
            ).pack(fill=tk.X, padx=28, pady=4)
            vars_map[opt_name] = var

        result = {"options": None}

        def confirm():
            result["options"] = [name for name, var in vars_map.items() if var.get()]
            dialog.destroy()

        def cancel():
            result["options"] = None
            dialog.destroy()

        btn_frame = tk.Frame(dialog)
        btn_frame.pack(side=tk.BOTTOM, pady=16)
        tk.Button(btn_frame, text="확인", width=10, command=confirm).pack(
            side=tk.LEFT, padx=8
        )
        tk.Button(btn_frame, text="취소", width=10, command=cancel).pack(
            side=tk.LEFT, padx=8
        )

        self.root.wait_window(dialog)
        return result["options"]

    def change_item_quantity(self, index, delta):
        if index < 0 or index >= len(self.order_items):
            return
        item = self.order_items[index]
        new_qty = item["quantity"] + delta
        if new_qty <= 0:
            del self.order_items[index]
        else:
            if not self.order_manager.check_order_limit(
                [i for idx, i in enumerate(self.order_items) if idx != index],
                new_qty,
            ):
                messagebox.showwarning("주문 제한", "주문 수량 제한을 초과했습니다.")
                return
            item["quantity"] = new_qty
        self.render_cart()

    def remove_item(self, index):
        if 0 <= index < len(self.order_items):
            del self.order_items[index]
            self.render_cart()

    def render_cart(self):
        for widget in self.cart_items_frame.winfo_children():
            widget.destroy()

        if not self.order_items:
            tk.Label(
                self.cart_items_frame,
                text="담긴 상품이 없습니다.",
                font=("맑은 고딕", 11),
                bg="#ffffff",
                fg="#6b7280",
            ).pack(pady=30)
            self.total_label.config(text="0원")
            return

        for idx, item in enumerate(self.order_items):
            product = item["product"]
            qty = item["quantity"]
            opts = item["options"]

            row = tk.Frame(self.cart_items_frame, bg="#ffffff", pady=6)
            row.pack(fill=tk.X)

            top = tk.Frame(row, bg="#ffffff")
            top.pack(fill=tk.X)
            tk.Label(
                top,
                text=product.name,
                font=("맑은 고딕", 12),
                bg="#ffffff",
                fg="#111827",
                anchor="w",
            ).pack(side=tk.LEFT)
            tk.Label(
                top,
                text=f"× {qty}",
                font=("맑은 고딕", 12),
                bg="#ffffff",
                fg="#374151",
            ).pack(side=tk.RIGHT)

            if opts:
                tk.Label(
                    row,
                    text="옵션: " + ", ".join(opts),
                    font=("맑은 고딕", 10),
                    bg="#ffffff",
                    fg="#6b7280",
                    anchor="w",
                ).pack(fill=tk.X)

            ctrl = tk.Frame(row, bg="#ffffff")
            ctrl.pack(fill=tk.X, pady=(4, 0))
            tk.Button(
                ctrl,
                text="-",
                width=3,
                command=lambda i=idx: self.change_item_quantity(i, -1),
            ).pack(side=tk.LEFT, padx=(0, 4))
            tk.Button(
                ctrl,
                text="+",
                width=3,
                command=lambda i=idx: self.change_item_quantity(i, 1),
            ).pack(side=tk.LEFT, padx=(0, 8))
            tk.Button(
                ctrl,
                text="삭제",
                width=5,
                command=lambda i=idx: self.remove_item(i),
            ).pack(side=tk.RIGHT)

            ttk.Separator(self.cart_items_frame, orient=tk.HORIZONTAL).pack(
                fill=tk.X, pady=(6, 0)
            )

        total = self.payment_manager.calculate_total(self.order_items)
        self.total_label.config(text=f"{total:,}원")

    # ---------------- 화면 전환 및 결제 ----------------
    def open_payment_screen(self):
        if not self.order_items:
            messagebox.showinfo("안내", "장바구니가 비어 있습니다.")
            return
        self.order_frame.pack_forget()
        self.payment_frame.pack(fill=tk.BOTH, expand=True)

    def show_order_screen(self):
        self.payment_frame.pack_forget()
        self.order_frame.pack(fill=tk.BOTH, expand=True)
        self.render_cart()

    def handle_payment(self, method):
        total_price = self.payment_manager.calculate_total(self.order_items)
        self.payment_manager.total_price = total_price

        if method == "card":
            paid = self.payment_manager.process_payment("card", total_price)
            if not paid:
                messagebox.showerror("결제 실패", "카드 결제에 실패했습니다.")
                return
        elif method == "cash":
            accumulated = 0
            paid = False
            while True:
                raw = simpledialog.askstring(
                    "현금 결제",
                    f"총 결제 금액: {total_price:,}원\n"
                    f"현재 투입 금액: {accumulated:,}원\n"
                    "투입할 현금 금액을 입력하세요 (0 또는 취소 시 중단):",
                    parent=self.root,
                )
                if raw is None or raw.strip() == "0":
                    messagebox.showinfo("취소", "현금 결제를 취소했습니다.")
                    return
                try:
                    money = int(raw.strip())
                except ValueError:
                    messagebox.showwarning("입력 오류", "금액은 숫자로 입력하세요.")
                    continue
                if money < 0:
                    messagebox.showwarning("입력 오류", "금액은 0 이상으로 입력하세요.")
                    continue

                accumulated += money
                if self.payment_manager.process_payment(
                    "cash", total_price, accumulated
                ):
                    paid = True
                    messagebox.showinfo(
                        "현금 결제 완료",
                        f"결제가 완료되었습니다.\n거스름돈: {self.payment_manager.change:,}원",
                    )
                    break
                shortage = total_price - accumulated
                messagebox.showwarning(
                    "금액 부족", f"{shortage:,}원이 부족합니다. 추가로 투입해 주세요."
                )
            if not paid:
                return
        else:
            return

        self._finalize_order(total_price, method)

    def _finalize_order(self, total_price, payment_method):
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
            self.receipt_manager.print_order_slip(receipt_order)
            messagebox.showerror(
                "저장 오류",
                "주문 저장에 실패했습니다. 주문표가 출력되었으니 포스기 직원에게 직접 문의해 주세요.",
            )
            self.order_items.clear()
            self.show_order_screen()
            return

        self.signal_manager.update_signal()
        self.receipt_manager.print_order_slip(receipt_order)
        try:
            self.receipt_manager.save_order_slip_txt(receipt_order)
        except OSError:
            pass

        want_receipt = messagebox.askyesno("영수증", "영수증을 받으시겠습니까?")
        if want_receipt:
            change = self.payment_manager.change if payment_method == "cash" else None
            self.receipt_manager.print_recipt(
                receipt_order, payment_method=payment_method, change=change
            )
            try:
                self.receipt_manager.save_receipt_txt(
                    receipt_order, payment_method=payment_method, change=change
                )
            except OSError:
                pass

        self.order_items.clear()
        messagebox.showinfo(
            "주문 접수", f"주문번호 {order_id}번 주문이 접수되었습니다."
        )
        self.show_order_screen()

    def on_close(self):
        self.running = False
        self.signal_manager.stop()
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = KioskUI(root)
    root.mainloop()

import os
import time


class SignalManager:
    def __init__(self, signal_file="data/signal.txt"):
        self.signal_file = signal_file
        self.last_signal = 0
        self.running = False

    # 신호 파일 초기화
    def init_signal(self):
        self.last_signal = 0
        folder = os.path.dirname(self.signal_file)
        if folder:
            os.makedirs(folder, exist_ok=True)
        try:
            with open(self.signal_file, "w", encoding="utf-8-sig") as file:
                file.write("0")
        except OSError:
            print("신호 파일 초기화 실패")

    # 신호 파일 읽기
    def read_signal(self):
        try:
            with open(self.signal_file, "r", encoding="utf-8-sig") as file:
                value = file.read().strip()
                if not value:
                    return None
                return int(value)
        except FileNotFoundError:
            self.init_signal()
            return 0
        except ValueError:
            print("신호 파일 형식이 잘못됨")
            return None
        except OSError:
            return None

    # 신호 파일 검사
    def check_signal(self, on_signal_changed, interval=0.7, once=False):
        self.running = True
        while self.running:
            current_signal = self.read_signal()
            if current_signal is not None:
                if current_signal != self.last_signal:
                    self.last_signal = current_signal
                    if on_signal_changed is not None:
                        on_signal_changed()
            if once:
                break
            time.sleep(interval)

    # 신호값 갱신
    def update_signal(self):
        current_signal = self.read_signal()
        if current_signal is None:
            current_signal = self.last_signal

        previous_last_signal = self.last_signal
        next_signal = current_signal + 1

        self.last_signal = next_signal
        try:
            with open(self.signal_file, "w", encoding="utf-8-sig") as file:
                file.write(str(next_signal))
        except OSError:
            self.last_signal = previous_last_signal
            print("신호 파일 업데이트 실패")

    def stop(self):
        self.running = False

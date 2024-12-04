import flet as ft  # Fletライブラリのインポート
import math  # 数学関数用ライブラリ

# 数字ボタンや操作ボタンの基本クラス
class CalcButton(ft.ElevatedButton):
    def __init__(self, text, button_clicked, expand=1):
        super().__init__()
        self.text = text  # ボタンの表示テキスト
        self.expand = expand  # ボタンの拡張サイズ
        self.on_click = button_clicked  # ボタンがクリックされたときのイベントハンドラー
        self.data = text  # ボタンデータとしてテキストを保存


# 数字用ボタンのクラス
class DigitButton(CalcButton):
    def __init__(self, text, button_clicked, expand=1):
        CalcButton.__init__(self, text, button_clicked, expand)
        self.bgcolor = ft.colors.WHITE24  # 背景色
        self.color = ft.colors.WHITE  # 文字色


# 四則演算用ボタンのクラス
class ActionButton(CalcButton):
    def __init__(self, text, button_clicked):
        CalcButton.__init__(self, text, button_clicked)
        self.bgcolor = ft.colors.ORANGE  # 背景色
        self.color = ft.colors.WHITE  # 文字色


# ACや+/-などの特殊操作ボタンのクラス
class ExtraActionButton(CalcButton):
    def __init__(self, text, button_clicked):
        CalcButton.__init__(self, text, button_clicked)
        self.bgcolor = ft.colors.BLUE_GREY_100  # 背景色
        self.color = ft.colors.BLACK  # 文字色


# 電卓アプリケーションのメインコンポーネント
class CalculatorApp(ft.Container):
    def __init__(self):
        super().__init__()
        self.reset()  # 初期状態にリセット

        # 表示部分（結果を表示するテキスト）
        self.result = ft.Text(value="0", color=ft.colors.WHITE, size=20)

        # コンテナのスタイル設定
        self.width = 350
        self.bgcolor = ft.colors.BLACK
        self.border_radius = ft.border_radius.all(20)
        self.padding = 20

        # ボタンレイアウトの設定
        self.content = ft.Column(
            controls=[
                ft.Row(controls=[self.result], alignment="end"),  # 結果表示行
                # 各行にボタンを配置
                ft.Row(
                    controls=[
                        ExtraActionButton(
                            text="AC", button_clicked=self.button_clicked
                        ),
                        ExtraActionButton(
                            text="+/-", button_clicked=self.button_clicked
                        ),
                        ExtraActionButton(text="%", button_clicked=self.button_clicked),
                        ActionButton(text="/", button_clicked=self.button_clicked),
                    ]
                ),
                ft.Row(
                    controls=[
                        DigitButton(text="7", button_clicked=self.button_clicked),
                        DigitButton(text="8", button_clicked=self.button_clicked),
                        DigitButton(text="9", button_clicked=self.button_clicked),
                        ActionButton(text="*", button_clicked=self.button_clicked),
                    ]
                ),
                ft.Row(
                    controls=[
                        DigitButton(text="4", button_clicked=self.button_clicked),
                        DigitButton(text="5", button_clicked=self.button_clicked),
                        DigitButton(text="6", button_clicked=self.button_clicked),
                        ActionButton(text="-", button_clicked=self.button_clicked),
                    ]
                ),
                ft.Row(
                    controls=[
                        DigitButton(text="1", button_clicked=self.button_clicked),
                        DigitButton(text="2", button_clicked=self.button_clicked),
                        DigitButton(text="3", button_clicked=self.button_clicked),
                        ActionButton(text="+", button_clicked=self.button_clicked),
                    ]
                ),
                ft.Row(
                    controls=[
                        DigitButton(
                            text="0", expand=2, button_clicked=self.button_clicked
                        ),  # 0ボタンは2倍幅
                        DigitButton(text=".", button_clicked=self.button_clicked),
                        ActionButton(text="=", button_clicked=self.button_clicked),
                    ]
                ),
                ft.Row(  # 三角関数・平方根ボタンの行
                    controls=[
                        ExtraActionButton(text="sin", button_clicked=self.button_clicked),
                        ExtraActionButton(text="cos", button_clicked=self.button_clicked),
                        ExtraActionButton(text="tan", button_clicked=self.button_clicked),

                        ExtraActionButton(text="x^y", button_clicked=self.button_clicked),  # x^yボタンを追加

                        ExtraActionButton(text="√", button_clicked=self.button_clicked),  # 平方根ボタン
                    ]
                ),
                ft.Row(  # 階乗ボタンの行
                    controls=[
                        ExtraActionButton(text="!", button_clicked=self.button_clicked),  # 階乗ボタン

                    ]
                ),
            ]
        )

    # ボタンがクリックされたときの処理
    def button_clicked(self, e):
        data = e.control.data  # クリックされたボタンのデータ
        print(f"Button clicked with data = {data}")  # デバッグ用の出力

        # ACまたはエラー状態のリセット
        if self.result.value == "Error" or data == "AC":
            self.result.value = "0"
            self.reset()

        # 数字または小数点の処理
        elif data in ("1", "2", "3", "4", "5", "6", "7", "8", "9", "0", "."):
            if self.result.value == "0" or self.new_operand:
                self.result.value = data
                self.new_operand = False
            else:
                self.result.value = self.result.value + data

        # 演算子の処理
        elif data in ("+", "-", "*", "/", "x^y"):
            if data == "x^y":
                self.operator = "**"  # Exponentiation operator in Python
            else:
                self.operator = data
            self.operand1 = float(self.result.value)
            self.new_operand = True

        # イコール（計算結果の表示）
        elif data == "=":
            self.result.value = self.calculate(
                self.operand1, float(self.result.value), self.operator
            )
            self.reset()

        # パーセント処理
        elif data == "%":
            self.result.value = float(self.result.value) / 100
            self.reset()

        # +/-（符号の切り替え）
        elif data == "+/-":
            if float(self.result.value) > 0:
                self.result.value = "-" + str(self.result.value)
            elif float(self.result.value) < 0:
                self.result.value = str(
                    self.format_number(abs(float(self.result.value)))
                )

        # 三角関数の処理
        elif data in ("sin", "cos", "tan"):
            try:
                angle = math.radians(float(self.result.value))  # ラジアンに変換
                if data == "sin":
                    self.result.value = self.format_number(math.sin(angle))
                elif data == "cos":
                    self.result.value = self.format_number(math.cos(angle))
                elif data == "tan":
                    self.result.value = (
                        "Error" if math.isclose(math.cos(angle), 0) else self.format_number(math.tan(angle))
                    )
            except ValueError:
                self.result.value = "Error"
            self.reset()

        # 平方根（√）の処理
        elif data == "√":
            try:
                value = float(self.result.value)
                if value < 0:  # 負の数の場合はエラーを表示
                    self.result.value = "Error"
                else:
                    self.result.value = self.format_number(math.sqrt(value))
            except ValueError:
                self.result.value = "Error"  # 不正な入力の場合エラーを表示
            self.reset()

        # 階乗（!）の処理
        elif data == "!":
            try:
                value = int(float(self.result.value))  # 階乗計算のため整数に変換
                if value < 0:
                    self.result.value = "Error"  # 負の数に対する階乗はエラー
                else:
                    self.result.value = self.format_number(math.factorial(value))
            except ValueError:
                self.result.value = "Error"  # 不正な入力の場合エラーを表示
            self.reset()

        self.update()  # 表示を更新

    # 数値のフォーマット処理（整数か小数かを判別）
    def format_number(self, num):
        if num % 1 == 0:
            return int(num)
        else:
            return round(num, 6)  # 小数点以下6桁まで丸める

    # 計算処理
    def calculate(self, operand1, operand2, operator):
        if operator == "+":
            return self.format_number(operand1 + operand2)
        elif operator == "-":
            return self.format_number(operand1 - operand2)
        elif operator == "*":
            return self.format_number(operand1 * operand2)
        elif operator == "/":
            if operand2 == 0:
                return "Error"  # 0除算エラー
            else:
                return self.format_number(operand1 / operand2)
        elif operator == "**":
            return self.format_number(operand1 ** operand2)  # Exponentiation calculation

    # 状態リセット処理
    def reset(self):
        self.operator = "+"  # デフォルトの演算子
        self.operand1 = 0  # 最初のオペランド
        self.new_operand = True  # 新しいオペランドフラグ


# メイン関数
def main(page: ft.Page):
    page.title = "Calc App"  # アプリのタイトル
    calc = CalculatorApp()  # 電卓アプリのインスタンスを作成
    page.add(calc)  # ページに追加



ft.app(target=main)  # アプリケーションの実行


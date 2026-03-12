import tkinter as tk
from tkinter import font


class CalculatorApp:
    """Графический калькулятор на tkinter."""

    def __init__(self, root):
        self.root = root
        self.root.title("Калькулятор")
        self.root.resizable(False, False)

        self.expression = ""
        self.result_var = tk.StringVar()

        self._create_display()
        self._create_buttons()

    def _create_display(self):
        """Создаёт поле вывода."""
        display_font = font.Font(family="Consolas", size=20, weight="bold")

        frame = tk.Frame(self.root, bg="#2c3e50", height=80)
        frame.pack(fill=tk.X, padx=5, pady=5)

        display = tk.Entry(
            frame,
            textvariable=self.result_var,
            font=display_font,
            bg="#ecf0f1",
            fg="#2c3e50",
            bd=0,
            justify="right",
            state="readonly",
            readonlybackground="#ecf0f1",
        )
        display.pack(fill=tk.BOTH, ipady=15, padx=10, pady=10)

    def _create_buttons(self):
        """Создаёт кнопки калькулятора."""
        buttons_frame = tk.Frame(self.root, bg="#34495e")
        buttons_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        buttons = [
            ["7", "8", "9", "/", "C"],
            ["4", "5", "6", "*", "←"],
            ["1", "2", "3", "-", "="],
            ["0", ".", "(", ")", "+"],
        ]

        button_font = font.Font(family="Consolas", size=14, weight="bold")

        for row_idx, row in enumerate(buttons):
            buttons_frame.grid_rowconfigure(row_idx, weight=1)
            for col_idx, text in enumerate(row):
                buttons_frame.grid_columnconfigure(col_idx, weight=1)
                btn = self._create_button(
                    buttons_frame, text, button_font, row_idx, col_idx
                )
                btn.grid(row=row_idx, column=col_idx, sticky="nsew", padx=2, pady=2)

    def _create_button(self, parent, text, font, row, col):
        """Создаёт одну кнопку."""
        bg_color = "#e74c3c" if text in ["C", "←", "="] else "#95a5a6"
        fg_color = "white"

        button = tk.Button(
            parent,
            text=text,
            font=font,
            bg=bg_color,
            fg=fg_color,
            bd=0,
            activebackground="#c0392b" if text in ["C", "←", "="] else "#7f8c8d",
            activeforeground="white",
            command=lambda t=text: self._on_button_click(t),
        )
        return button

    def _on_button_click(self, text):
        """Обрабатывает нажатие кнопки."""
        if text == "C":
            self.expression = ""
            self.result_var.set("")
        elif text == "←":
            self.expression = self.expression[:-1]
            self.result_var.set(self.expression)
        elif text == "=":
            self._calculate()
        else:
            self.expression += text
            self.result_var.set(self.expression)

    def _calculate(self):
        """Вычисляет результат выражения."""
        try:
            allowed = set("0123456789+-*/.() ")
            if not all(c in allowed for c in self.expression):
                self.result_var.set("Ошибка")
                self.expression = ""
                return

            result = eval(self.expression)
            self.result_var.set(str(result))
            self.expression = str(result)
        except ZeroDivisionError:
            self.result_var.set("Ошибка: деление на 0")
            self.expression = ""
        except SyntaxError:
            self.result_var.set("Ошибка синтаксиса")
            self.expression = ""
        except Exception:
            self.result_var.set("Ошибка")
            self.expression = ""


def main():
    root = tk.Tk()
    app = CalculatorApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()

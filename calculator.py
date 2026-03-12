def calculator():
    """Простой консольный калькулятор."""
    print("Калькулятор. Введите 'q' для выхода.")
    
    while True:
        try:
            expr = input("\nВведите выражение: ").strip()
            if expr.lower() == 'q':
                print("Выход из программы.")
                break
            
            # Проверка на допустимые символы
            allowed = set("0123456789+-*/.() ")
            if not all(c in allowed for c in expr):
                print("Ошибка: недопустимые символы. Используйте только цифры, +, -, *, /, ., (, )")
                continue
            
            result = eval(expr)
            print(f"Результат: {result}")
        except ZeroDivisionError:
            print("Ошибка: деление на ноль.")
        except SyntaxError:
            print("Ошибка: неверный формат выражения.")
        except Exception as e:
            print(f"Ошибка: {e}")


if __name__ == "__main__":
    calculator()

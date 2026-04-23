import ast
import itertools
import re


class UnsafeExpressionError(Exception):
    pass


class KLogicCalculator:

    def __init__(self, k: int):
        if k < 2:
            raise ValueError("k должно быть ≥ 2")
        self.k = k

    POST_NEGATION_SYMBOL = "¬"  # символ отрицания Поста в пользовательском вводе
    LUK_NEGATION_SYMBOL = "~"  # символ отрицания Лукашевича в пользовательском вводе
    ADD_SYMBOL = "+"  # символ суммы по модулю k
    MUL_SYMBOL = "*"  # символ произведения по модулю k
    TRUNCATED_SUB_SYMBOL = "/"  # символ усечённой разности
    DIFF_SYMBOL = "-"  # символ разности по модулю k
    IMPLICATION_SYMBOL = "→"  # символ импликации

    def normalize_expression(self, expression: str) -> str:
        if expression is None:
            raise UnsafeExpressionError("Формула не задана")

        expression = expression.strip()
        if not expression:
            raise UnsafeExpressionError("Формула не задана")

        normalized, position = self._parse_implication(expression,0)
        position = self._skip_spaces(expression, position)
        if position != len(
                expression):
            raise UnsafeExpressionError(
                f"Ошибка синтаксиса возле: {expression[position:]}")

        return normalized

    def _skip_spaces(self, text: str,
                     pos: int) -> int:  # вспомогательный метод для пропуска пробелов с произвольной позиции
        while pos < len(text) and text[pos].isspace():  # двигаемся вправо, пока встречаем пробельные символы
            pos += 1  # сдвигаем индекс на следующий символ
        return pos  # возвращаем первую непробельную позицию

    def _parse_implication(self, text: str, pos: int):  # разбираем импликацию как оператор самого низкого приоритета
        left, pos = self._parse_additive(text,
                                         pos)  # сначала разбираем всё, что сильнее импликации: +, -, *, /, унарные и атомы
        pos = self._skip_spaces(text, pos)  # пропускаем пробелы перед возможным символом импликации

        if pos < len(text) and text[pos] == self.IMPLICATION_SYMBOL:  # если после левой части стоит символ импликации
            right, pos = self._parse_implication(text,
                                                 pos + 1)  # рекурсивно разбираем правую часть, делая импликацию правоассоциативной
            return f"imp({left},{right})", pos  # превращаем инфиксную запись в внутренний вызов imp(...)

        return left, pos  # если импликации нет, просто возвращаем разобранную левую часть

    def _parse_additive(self, text: str, pos: int):  # разбираем бинарные операторы среднего приоритета: + и -
        left, pos = self._parse_multiplicative(text, pos)  # сначала разбираем всё, что сильнее: *, /, унарные и атомы

        while True:  # цикл нужен для цепочек вида A+B-C+D
            pos = self._skip_spaces(text, pos)  # перед оператором игнорируем пробелы

            if pos < len(text) and text[pos] in {self.ADD_SYMBOL, self.DIFF_SYMBOL}:  # если нашли + или -
                operator = text[pos]  # запоминаем, какой именно оператор встретился
                right, pos = self._parse_multiplicative(text,
                                                        pos + 1)  # разбираем правую часть этого бинарного оператора

                if operator == self.ADD_SYMBOL:  # если оператор — сумма по модулю k
                    left = f"add({left},{right})"  # превращаем левую и правую часть во внутренний вызов add(...)
                else:  # если оператор — разность по модулю k
                    left = f"sub({left},{right})"  # превращаем левую и правую часть во внутренний вызов sub(...)

                continue  # продолжаем, чтобы поддержать длинные цепочки слева направо

            break  # если + или - не нашли, завершаем цикл

        return left, pos  # возвращаем разобранную аддитивную часть и текущую позицию

    def _parse_multiplicative(self, text: str,
                              pos: int):  # разбираем бинарные операторы более высокого приоритета: * и /
        left, pos = self._parse_unary(text, pos)  # сначала разбираем унарные операторы и атомарные выражения

        while True:  # цикл нужен для цепочек вида A*B/C*D
            pos = self._skip_spaces(text, pos)  # игнорируем пробелы перед оператором

            if pos < len(text) and text[pos] in {self.MUL_SYMBOL, self.TRUNCATED_SUB_SYMBOL}:  # если нашли * или /
                operator = text[pos]  # сохраняем найденный оператор
                right, pos = self._parse_unary(text, pos + 1)  # разбираем правую часть бинарной операции

                if operator == self.MUL_SYMBOL:  # если это произведение по модулю k
                    left = f"mul({left},{right})"  # заменяем инфиксную запись на внутренний вызов mul(...)
                else:  # если это усечённая разность
                    left = f"tsub({left},{right})"  # заменяем инфиксную запись на внутренний вызов tsub(...)

                continue  # продолжаем разбор цепочки слева направо

            break  # если операторов * или / больше нет, выходим из цикла

        return left, pos  # возвращаем разобранное выражение этого приоритета

    def _parse_unary(self, text: str, pos: int):  # разбираем унарные операторы ¬ и ~
        pos = self._skip_spaces(text, pos)  # сначала пропускаем пробелы перед выражением

        if pos >= len(text):  # если выражение неожиданно закончилось
            raise UnsafeExpressionError("Ожидалось выражение")  # сообщаем о незавершённой формуле

        ch = text[pos]  # читаем текущий символ

        if ch == self.POST_NEGATION_SYMBOL:  # если встретили отрицание Поста
            next_pos = self._skip_spaces(text,
                                         pos + 1)  # проверяем, что после символа есть аргумент, а не только пробелы
            if next_pos >= len(text):  # если после ¬ ничего нет
                raise UnsafeExpressionError(
                    "После символа ¬ отсутствует аргумент")  # отдаём точную ошибку по пользовательскому вводу
            operand, pos = self._parse_unary(text, pos + 1)  # рекурсивно разбираем аргумент отрицания
            return f"post({operand})", pos  # переводим ¬x во внутренний вызов post(x)

        if ch == self.LUK_NEGATION_SYMBOL:  # если встретили отрицание Лукашевича
            next_pos = self._skip_spaces(text, pos + 1)  # проверяем, что после ~ действительно есть аргумент
            if next_pos >= len(text):  # если после ~ ничего нет
                raise UnsafeExpressionError("После символа ~ отсутствует аргумент")  # возвращаем понятную ошибку
            operand, pos = self._parse_unary(text, pos + 1)  # рекурсивно разбираем аргумент отрицания
            return f"luk({operand})", pos  # переводим ~x во внутренний вызов luk(x)

        return self._parse_primary(text, pos)  # если унарного оператора нет, разбираем обычное атомарное выражение

    def _parse_primary(self, text: str, pos: int):  # разбираем числа, имена, вызовы функций и выражения в скобках
        pos = self._skip_spaces(text, pos)  # игнорируем пробелы перед атомом

        if pos >= len(text):  # если дошли до конца строки там, где ожидали атом
            raise UnsafeExpressionError("Ожидалось выражение")  # сообщаем о незавершённой формуле

        ch = text[pos]  # читаем текущий символ

        if ch.isdigit():  # если атом начинается с цифры, это числовая константа
            start = pos  # запоминаем начало числа
            while pos < len(text) and text[pos].isdigit():  # дочитываем все цифры подряд
                pos += 1  # двигаем позицию, пока число не закончится
            return text[start:pos], pos  # возвращаем число как строку и новую позицию

        if ch.isalpha() or ch == "_":  # если атом начинается с буквы или underscore, это переменная или имя функции
            return self._parse_name_or_call(text, pos)  # делегируем разбор имени и возможного вызова функции

        if ch == "(":  # если встретили открывающую скобку
            inner, pos = self._parse_implication(text,
                                                 pos + 1)  # разбираем всё выражение внутри скобок с полным учётом всех приоритетов
            pos = self._skip_spaces(text, pos)  # игнорируем пробелы перед закрывающей скобкой

            if pos >= len(text) or text[pos] != ")":  # если закрывающая скобка не найдена
                raise UnsafeExpressionError("Ожидалась закрывающая скобка")  # сообщаем о незакрытом подвыражении

            return f"({inner})", pos + 1  # возвращаем нормализованное содержимое вместе со скобками

        raise UnsafeExpressionError(
            f"Недопустимый символ: {ch}")  # все остальные символы в позиции атома считаем ошибкой ввода

    def _parse_name_or_call(self, text: str, pos: int):  # разбираем переменную или вызов функции вида name(...)
        start = pos  # запоминаем начало имени
        pos += 1  # переходим к следующему символу после первой буквы

        while pos < len(text) and (
                text[pos].isalnum() or text[pos] == "_"):  # дочитываем оставшуюся часть идентификатора
            pos += 1  # двигаемся, пока имя не закончится

        name = text[start:pos]  # собираем итоговое имя, например A, min, const, webb
        pos = self._skip_spaces(text, pos)  # разрешаем пробел между именем функции и скобкой

        if pos < len(text) and text[pos] == "(":  # если после имени идёт открывающая скобка, значит это вызов функции
            args, pos = self._parse_call_args(text, pos + 1)  # разбираем список аргументов внутри скобок
            return f"{name}({','.join(args)})", pos  # возвращаем нормализованный вызов функции с уже разобранными аргументами

        return name, pos  # если скобок нет, значит это обычная переменная

    def _parse_call_args(self, text: str, pos: int):  # разбираем аргументы пользовательской функции в круглых скобках
        args = []  # сюда будем собирать нормализованные аргументы
        pos = self._skip_spaces(text, pos)  # пропускаем пробелы сразу после открывающей скобки

        if pos < len(text) and text[
            pos] == ")":  # разрешаем синтаксически пустой список аргументов, а бизнес-валидация ниже отловит недопустимые случаи
            return args, pos + 1  # возвращаем пустой список аргументов и позицию после закрывающей скобки

        while True:  # читаем аргументы до закрывающей скобки
            arg, pos = self._parse_implication(text,
                                               pos)  # каждый аргумент сам может содержать все поддерживаемые операторы
            args.append(arg)  # добавляем нормализованный аргумент в список
            pos = self._skip_spaces(text, pos)  # игнорируем пробелы перед разделителем или закрывающей скобкой

            if pos >= len(text):  # если строка закончилась до закрывающей скобки
                raise UnsafeExpressionError("Не закрыта скобка")  # возвращаем понятную ошибку о незакрытой функции

            if text[pos] == ",":  # если нашли запятую, значит впереди следующий аргумент
                pos += 1  # переходим на символ после запятой
                continue  # продолжаем цикл и читаем следующий аргумент

            if text[pos] == ")":  # если нашли закрывающую скобку, список аргументов завершён
                return args, pos + 1  # возвращаем все аргументы и позицию после скобки

            raise UnsafeExpressionError(
                f"Ожидалась ',' или ')', получено: {text[pos]}")  # любой другой символ в этом месте — синтаксическая ошибка

    def validate_expression(self, expression: str):
        expression = self.normalize_expression(
            expression)
        tree = ast.parse(expression, mode="eval")

        variables = self._extract_variables_from_normalized(expression)

        allowed_function_names = {
            "min", "max", "add", "mul", "imp", "post", "luk", "neg", "webb",
            "sub", "tsub", "j", "J", "const"

        }
        allowed_value_names = {
            "k"}
        allowed_names = set(
            variables) | allowed_function_names | allowed_value_names

        self._validate_ast(tree, allowed_names,
                           allowed_function_names)
        return tree

    def validate_const(self, value):
        if isinstance(value, bool) or not isinstance(value, int):
            raise UnsafeExpressionError("Константа должна быть целым числом")

        if value < 0 or value >= self.k:
            raise UnsafeExpressionError(
                f"Константа {value} недопустима при k={self.k}. "
                f"Разрешены значения от 0 до {self.k - 1}."
            )

        return int(value)

    def _validate_logic_value(self, value, func_name: str,
                              arg_label: str) -> int:  # проверяем одно значение k-значной логики для конкретной функции и аргумента
        if isinstance(value, bool) or not isinstance(value,
                                                     int):  # запрещаем bool и любые нецелые типы, потому что логические значения должны быть целыми числами
            raise ValueError(  # выбрасываем понятную ошибку уровня пользовательской функции
                f"Функция {func_name}: {arg_label} должен быть целым числом из диапазона 0..{self.k - 1}"
                # формируем единый текст ошибки для неверного типа аргумента
            )

        if value < 0 or value >= self.k:  # проверяем, что значение лежит в допустимом диапазоне k-значной логики
            raise ValueError(  # если аргумент вне диапазона, выбрасываем понятную ошибку
                f"Функция {func_name}: {arg_label} {value} выходит за допустимый диапазон 0..{self.k - 1}"
                # показываем, какое именно значение оказалось недопустимым
            )

        return int(value)  # возвращаем гарантированно корректное целое значение для дальнейшего вычисления

    def _validate_logic_args(self, args, func_name: str, exact_count: int | None = None,
                             min_count: int | None = None) -> list[
        int]:  # проверяем список аргументов функции и возвращаем уже валидированные значения
        if exact_count is not None and len(
                args) != exact_count:  # если для функции задано точное число аргументов, проверяем строгое совпадение
            raise ValueError(
                f"Функция {func_name} принимает ровно {exact_count} аргумента" if exact_count != 1 else f"Функция {func_name} принимает ровно 1 аргумент")  # возвращаем понятную ошибку по числу аргументов

        if min_count is not None and len(
                args) < min_count:  # если для функции задано минимальное число аргументов, проверяем нижнюю границу
            raise ValueError(
                f"Функция {func_name} принимает минимум {min_count} аргумента" if min_count != 1 else f"Функция {func_name} принимает минимум 1 аргумент")  # возвращаем понятную ошибку по минимальному числу аргументов

        normalized_args = []  # сюда собираем уже проверенные аргументы функции
        for index, value in enumerate(args,
                                      start=1):  # перебираем аргументы по порядку, чтобы формировать точные сообщения вида аргумент #1, #2 и т.д.
            normalized_args.append(self._validate_logic_value(value, func_name,
                                                              f"аргумент #{index}"))  # проверяем каждый аргумент как допустимое значение k-значной логики и сохраняем его
        return normalized_args  # возвращаем список уже валидированных целых значений

    def extract_variables(self,
                          expression: str):  # публичный метод извлечения переменных из пользовательского выражения
        expression = self.normalize_expression(
            expression)  # сначала приводим пользовательскую запись к внутреннему нормализованному виду
        return self._extract_variables_from_normalized(
            expression)  # после нормализации передаём работу внутреннему методу без повторения одной и той же логики

    def _extract_variables_from_normalized(self, expression: str) -> list[str]:  # извлекаем переменные из уже нормализованного выражения без повторной нормализации
        tokens = re.findall(r'\b[A-Za-z_][A-Za-z0-9_]*\b', expression)  # находим все идентификаторы вида A, x1, min, const, post и т.д. в уже подготовленной строке

        reserved_names = {  # перечисляем все служебные имена, которые не должны считаться пользовательскими переменными
            "min", "max", "add", "mul", "imp", "post", "luk", "neg",  # основные функции калькулятора
            "webb", "sub", "tsub", "j", "J", "const", "k"  # остальные поддерживаемые функции и специальное имя k
        }

        variables = []  # сюда будем собирать найденные переменные без повторов и с сохранением порядка первого появления
        for token in tokens:  # перебираем все найденные идентификаторы по порядку
            if token not in reserved_names and not token.isdigit():  # отбрасываем служебные имена и числовые токены
                if token not in variables:  # не добавляем одну и ту же переменную повторно
                    variables.append(token)  # сохраняем новую переменную в итоговый список

        return variables  # возвращаем итоговый список пользовательских переменных

    # 13 элементарных функций
    def constanta(self, c):
        return self.validate_const(c)

    def post_neg(self, *args):
        if len(args) != 1:
            raise ValueError(
                "Функция post принимает ровно 1 аргумент")

        x = self._validate_logic_value(args[0], "post","аргумент")
        return (x + 1) % self.k

    def luk_neg(self, *args):
        if len(args) != 1:
            raise ValueError(
                "Функция luk принимает ровно 1 аргумент")

        x = self._validate_logic_value(args[0], "luk","аргумент")
        return (self.k - 1) - x

    def j(self, i, x):
        i = self.validate_const(i)
        x = self._validate_logic_value(x, "j","второй аргумент")

        return 1 if x == i else 0

    def J(self, i, x):
        i = self.validate_const(i)
        x = self._validate_logic_value(x, "J","второй аргумент")

        return (self.k - 1) if x == i else 0

    def min_(self, *args):
        normalized_args = self._validate_logic_args(args, "min", min_count=2)
        return min(normalized_args)

    def max_(self, *args):
        normalized_args = self._validate_logic_args(args, "max", min_count=2)
        return max(normalized_args)

    def add_mod(self, *args):
        x, y = self._validate_logic_args(args, "add", exact_count=2)
        return (x + y) % self.k

    def mul_mod(self, *args):
        x, y = self._validate_logic_args(args, "mul", exact_count=2)
        return (x * y) % self.k

    def truncated_sub(self, *args):
        x, y = self._validate_logic_args(args, "tsub", exact_count=2)
        return max(x - y, 0)

    def implication(self, *args):
        x, y = self._validate_logic_args(args, "imp", exact_count=2)
        return min(self.k - 1, (self.k - 1) - x + y)

    def webb(self, *args):
        x, y = self._validate_logic_args(args, "webb", exact_count=2)
        return (max(x, y) + 1) % self.k

    def neg(self, *args):
        if len(args) != 1:
            raise ValueError("Функция neg принимает ровно 1 аргумент")

        x = self._validate_logic_value(args[0], "neg","аргумент")
        return (-x) % self.k

    def diff_mod(self, *args):
        x, y = self._validate_logic_args(args, "sub", exact_count=2)
        return (x - y) % self.k

    def expression_to_label(self, node):
        if isinstance(node, ast.Name):
            return node.id

        if isinstance(node, ast.Constant):
            return f"const({node.value})"

        if isinstance(node, ast.Call):
            func_name = node.func.id

            if func_name == "const" and len(node.args) == 1:
                arg = node.args[0]
                if isinstance(arg, ast.Constant):
                    return f"const({arg.value})"

            args_labels = [self.expression_to_label(arg) for arg in node.args]
            return f"{func_name}(" + ",".join(args_labels) + ")"

        raise ValueError("Не удалось преобразовать выражение в подпись")

    def _env(self, values: dict):  # собираем безопасное окружение для eval только из разрешённых функций и текущих переменных
        env = {  # словарь соответствия имён в формуле реальным методам калькулятора
            "min": self.min_,  # подключаем минимум
            "max": self.max_,  # подключаем максимум
            "add": self.add_mod,  # подключаем сумму по модулю k
            "mul": self.mul_mod,  # подключаем произведение по модулю k
            "imp": self.implication,  # подключаем импликацию
            "post": self.post_neg,  # подключаем отрицание Поста
            "luk": self.luk_neg,  # подключаем отрицание Лукашевича
            "neg": self.neg,  # подключаем обычное отрицание по модулю k
            "webb": self.webb,  # подключаем функцию Вебба
            "sub": self.diff_mod,  # подключаем разность по модулю k
            "tsub": self.truncated_sub,  # подключаем усечённую разность
            "j": self.j,  # добавляем характеристическую функцию 1-го рода, которая сейчас реализована, но не подключена
            "J": self.J,  # подключаем характеристическую функцию 2-го рода
            "const": self.constanta,  # подключаем константу
            "k": self.k,  # пробрасываем текущее значение k как доступное имя
        }
        env.update(values)  # добавляем в окружение реальные значения пользовательских переменных
        return env  # возвращаем готовое безопасное окружение для вычисления

    def _validate_ast(self, node: ast.AST, allowed_names: set, allowed_function_names: set):
        allowed_nodes = (
            ast.Expression,
            ast.Call,
            ast.Name,
            ast.Load,
            ast.Constant,
        )

        if not isinstance(node, allowed_nodes):
            raise UnsafeExpressionError(f"Запрещённая конструкция: {type(node).__name__}")

        if isinstance(node, ast.Call):
            if not isinstance(node.func, ast.Name):
                raise UnsafeExpressionError("Разрешены только вызовы функций вида name(...)")

            func_name = node.func.id

            if func_name not in allowed_function_names:
                raise UnsafeExpressionError(f"Недопустимая функция: {func_name}")

            if func_name in {"j", "J"}:
                if len(node.args) != 2:
                    raise UnsafeExpressionError(f"Функция {func_name} принимает ровно 2 аргумента")

                first_arg = node.args[0]
                second_arg = node.args[1]

                if not isinstance(first_arg, ast.Constant):
                    raise UnsafeExpressionError(
                        f"Функция {func_name}: первый аргумент i должен быть целочисленным литералом"
                    )

                self.validate_const(first_arg.value)
                self._validate_ast(second_arg, allowed_names, allowed_function_names)
                return

            if func_name == "const":
                if len(node.args) != 1:
                    raise UnsafeExpressionError("Функция const принимает ровно 1 аргумент")

                arg = node.args[0]

                if not isinstance(arg, ast.Constant):
                    raise UnsafeExpressionError(
                        "Функция const принимает только один числовой литерал, например const(2)"
                    )

                self.validate_const(arg.value)
                return

            for arg in node.args:
                self._validate_ast(arg, allowed_names, allowed_function_names)

            return

        if isinstance(node, ast.Name):
            if node.id not in allowed_names:
                raise UnsafeExpressionError(f"Недопустимое имя: {node.id}")
            return

        if isinstance(node, ast.Constant):
            self.validate_const(node.value)
            return

        for child in ast.iter_child_nodes(node):
            self._validate_ast(child, allowed_names, allowed_function_names)

    def evaluate_expression(self, expression: str,
                            values: dict):  # вычисляем значение выражения на конкретном наборе переменных
        expression = self.normalize_expression(
            expression)  # сначала нормализуем символьный ввод в каноническую внутреннюю форму
        tree = ast.parse(expression, mode="eval")  # затем строим AST уже по безопасной внутренней записи

        allowed_function_names = {
            # перечисляем только реальные функции, которые разрешены после нормализации выражения
            "min", "max", "add", "mul", "imp", "post", "luk", "neg", "webb",  # основные функции вычислителя
            "sub", "tsub", "j", "J", "const"  # оставшиеся допустимые функции без k, потому что k не является вызовом
        }
        allowed_value_names = {"k"}  # отдельно разрешаем имя k как значение, доступное в выражении
        allowed_names = set(
            values.keys()) | allowed_function_names | allowed_value_names  # объединяем переменные, функции и допустимые имена-значения

        self._validate_ast(tree, allowed_names, allowed_function_names)  # ещё раз проверяем AST перед выполнением eval

        code = compile(tree, "<expr>", "eval")  # компилируем уже проверенное выражение
        return eval(code, {"__builtins__": {}},
                    self._env(values))  # считаем результат в изолированном окружении без builtins

    def generate_function_rows(self, expression: str,
                               n: int):  # строим все строки значений функции для полного перебора переменных
        expression = self.normalize_expression(
            expression)  # сразу приводим формулу к внутреннему виду, чтобы дальше везде использовался один формат
        variables = self._extract_variables_from_normalized(expression)  # используем внутренний метод, потому что expression здесь уже нормализовано выше

        if len(variables) > n:  # проверяем ограничение на максимальное число переменных
            raise ValueError(  # если ограничение нарушено, прерываем построение понятной ошибкой
                f"В формуле используется {len(variables)} переменных, а разрешено только {n}"
                # показываем фактическое и допустимое число переменных
            )

        rows = []  # сюда будем складывать все строки функции

        if not variables:  # если в формуле нет переменных, это константная функция
            result = int(self.evaluate_expression(expression,
                                                  {})) % self.k  # вычисляем единственное значение константной формулы
            rows.append({  # добавляем единственную строку результата
                "assignment": {},  # у константной функции нет назначения переменных
                "result": result,  # сохраняем вычисленный результат
            })
            return variables, rows  # сразу возвращаем итог

        for combo in itertools.product(range(self.k), repeat=len(
                variables)):  # перебираем все возможные наборы значений переменных от 0 до k-1
            assignment = dict(zip(variables, combo))  # собираем словарь значений переменных для текущей строки
            result = int(
                self.evaluate_expression(expression, assignment)) % self.k  # вычисляем значение формулы на этом наборе
            rows.append({  # добавляем строку в итоговую таблицу
                "assignment": assignment,  # сохраняем значения переменных
                "result": result,  # сохраняем результат формулы
            })

        return variables, rows  # возвращаем список переменных и все построенные строки

    def _const_expr(self, value: int) -> str:
        return f"const({int(value)})"

    def _nest_binary(self, func_name: str, parts: list[str]) -> str:
        """
        Для бинарных функций add/mul строит вложенную запись:
        add(a,b,c) -> add(add(a,b),c)
        """
        if not parts:
            raise ValueError("Пустой список частей для вложенной бинарной функции")

        expr = parts[0]
        for part in parts[1:]:
            expr = f"{func_name}({expr},{part})"
        return expr

    def build_first_basic_form(self, variables: list[str], rows: list[
        dict]) -> dict:  # строим 1-ю основную форму сразу в полном и сокращённом виде по уже готовым строкам функции
        if not variables:  # если функция константная и не зависит от переменных
            const_value = str(rows[0]["result"])  # берём единственное значение константной функции
            return {"full": const_value, "reduced": const_value}  # для константы полная и сокращённая формы совпадают

        full_terms = []  # сюда собираем все члены полной 1-й формы без сокращений
        reduced_terms = []  # сюда собираем члены сокращённой 1-й формы после упрощений

        for row in rows:  # перебираем все строки таблицы функции
            value = row["result"]  # берём значение функции на текущем наборе переменных
            assignment = row["assignment"]  # получаем конкретные значения переменных для этой строки

            j_terms = [f"J({assignment[var_name]},{var_name})" for var_name in
                       variables]  # строим список всех индикаторов J(si, xi) для текущей строки
            full_parts = [str(value)] + j_terms  # в полной форме всегда явно пишем f(s) и все индикаторы J
            full_terms.append(
                f"min{{{', '.join(full_parts)}}}")  # добавляем полный член вида min{f(s), J(...), ..., J(...)}

            if value == 0:  # если f(s)=0, то такой член в сокращённой форме исчезает, потому что min{0, ...}=0 и он не влияет на внешний max
                continue  # пропускаем этот член для сокращённой формы

            reduced_parts = j_terms if value == self.k - 1 else [str(
                value)] + j_terms  # если f(s)=k-1, убираем константу из min, иначе оставляем её
            reduced_terms.append(
                reduced_parts[0] if len(reduced_parts) == 1 else f"min{{{', '.join(reduced_parts)}}}"
                # если после сокращения остался один элемент — пишем его как есть, иначе оставляем min{...}
            )

        full_form = f"max{{{', '.join(full_terms)}}}" if full_terms else "0"  # собираем полную 1-ю форму как max{...} по всем членам
        reduced_form = f"max{{{', '.join(reduced_terms)}}}" if reduced_terms else "0"  # собираем сокращённую 1-ю форму, а если членов нет — это нулевая функция

        return {"full": full_form, "reduced": reduced_form}  # возвращаем обе версии 1-й основной формы

    def build_second_basic_form(self, variables: list[str], rows: list[
        dict]) -> dict:  # строим 2-ю основную форму сразу в полном и сокращённом виде
        if not variables:  # если функция константная
            const_value = str(rows[0]["result"])  # берём значение константы
            return {"full": const_value, "reduced": const_value}  # для константы обе версии совпадают

        full_terms = []  # сюда собираем все слагаемые полной 2-й формы
        reduced_terms = []  # сюда собираем слагаемые сокращённой 2-й формы

        for row in rows:  # перебираем все строки таблицы функции
            value = row["result"]  # берём значение функции в текущей строке
            assignment = row["assignment"]  # получаем набор значений переменных для этой строки

            j_terms = [f"j({assignment[var_name]},{var_name})" for var_name in
                       variables]  # строим индикаторы первого рода j(si, xi) для текущей строки
            product_part = "·".join(j_terms)  # собираем произведение индикаторов в человекочитаемом виде через символ ·

            full_terms.append(
                f"{value}·{product_part}")  # в полной форме всегда пишем коэффициент явно, даже если он 0 или 1

            if value == 0:  # если коэффициент равен 0, то в сокращённой форме это слагаемое исчезает
                continue  # пропускаем нулевое слагаемое

            reduced_terms.append(
                product_part if value == 1 else f"{value}·{product_part}")  # если коэффициент 1, убираем его; иначе оставляем явно

        full_form = " + ".join(
            full_terms) if full_terms else "0"  # полную 2-ю форму показываем как обычную сумму всех слагаемых
        reduced_form = " + ".join(
            reduced_terms) if reduced_terms else "0"  # сокращённую 2-ю форму тоже показываем суммой, а если всё сократилось — это 0

        return {"full": full_form, "reduced": reduced_form}  # возвращаем обе версии 2-й основной формы

    def build_third_basic_form(self, variables: list[str],
                               rows: list[dict]) -> dict:  # строим 3-ю основную форму сразу в полном и сокращённом виде
        if not variables:  # если функция константная
            const_value = str(rows[0]["result"])  # получаем единственное значение функции
            return {"full": const_value,
                    "reduced": const_value}  # для константной функции полная и сокращённая формы совпадают

        full_terms = []  # сюда собираем все члены полной 3-й формы
        reduced_terms = []  # сюда собираем члены сокращённой 3-й формы

        for row in rows:  # перебираем все строки таблицы значений функции
            value = row["result"]  # берём значение функции на текущем наборе переменных
            assignment = row["assignment"]  # получаем конкретные значения переменных в текущей строке

            negated_j_terms = [f"~J({assignment[var_name]},{var_name})" for var_name in
                               variables]  # строим список отрицаний индикаторов второго рода для текущей строки
            full_parts = [str(
                value)] + negated_j_terms  # в полной 3-й форме всегда явно пишем и константу f(s), и все ~J-термы
            full_terms.append(
                f"max{{{', '.join(full_parts)}}}")  # добавляем полный член вида max{f(s), ~J(...), ..., ~J(...)}

            if value == self.k - 1:  # если f(s)=k-1, то такой член в сокращённой форме убирается, потому что max{k-1, ...}=k-1 и не влияет на внешний min
                continue  # пропускаем этот член при построении сокращённой формы

            reduced_parts = negated_j_terms if value == 0 else [str(
                value)] + negated_j_terms  # если f(s)=0, убираем ноль из max; иначе константу оставляем
            reduced_terms.append(
                reduced_parts[0] if len(reduced_parts) == 1 else f"max{{{', '.join(reduced_parts)}}}"
                # если после сокращения остался один элемент — пишем его как есть, иначе оставляем max{...}
            )

        full_form = f"min{{{', '.join(full_terms)}}}" if full_terms else str(
            self.k - 1)  # собираем полную 3-ю форму как min{...} по всем строкам
        reduced_form = f"min{{{', '.join(reduced_terms)}}}" if reduced_terms else str(
            self.k - 1)  # собираем сокращённую 3-ю форму, а если всё сократилось — это максимальная константа

        return {"full": full_form, "reduced": reduced_form}  # возвращаем обе версии 3-й основной формы

    def build_basic_forms(self, expression: str,
                          n: int) -> dict:
        variables, rows = self.generate_function_rows(expression,
                                                      n)

        return {  # возвращаем словарь со всеми тремя формами
            "first": self.build_first_basic_form(variables, rows),
            "second": self.build_second_basic_form(variables, rows),
            "third": self.build_third_basic_form(variables, rows),
        }

    def generate_table(self, expression: str, n: int):  # формируем данные для основной таблицы истинности
        expression = self.normalize_expression(
            expression)  # сначала приводим пользовательскую запись к внутреннему каноническому виду
        variables = self._extract_variables_from_normalized(
            expression)  # не нормализуем выражение повторно, потому что оно уже приведено к внутреннему виду в начале метода
        tree = ast.parse(expression, mode="eval")  # разбираем уже нормализованную формулу в AST
        root = tree.body  # получаем корневой узел выражения для определения имени результата

        if isinstance(root, ast.Constant):  # если формула — просто константа
            result_name = self.expression_to_label(root)  # делаем подпись результата по самой константе
        elif isinstance(root, ast.Call):  # если формула — вызов функции
            result_name = self.expression_to_label(root)  # строим подпись результата по внутренней канонической записи
        else:  # запасной случай на случай нетиповой структуры
            result_name = "F"  # используем стандартное имя столбца результата

        if len(variables) > n:  # проверяем, не превышено ли ограничение по числу переменных
            raise ValueError(  # если превышено — прерываем выполнение понятной ошибкой
                f"В формуле используется {len(variables)} переменных, а разрешено только {n}"
                # сообщаем фактическое и допустимое количество переменных
            )

        table = []  # подготавливаем список строк будущей таблицы

        if not variables:  # если формула не содержит переменных, значит это константная функция
            result = self.evaluate_expression(expression, {})  # вычисляем значение формулы без подстановки переменных
            result = int(result) % self.k  # приводим результат к диапазону k-значной логики

            table.append({  # добавляем единственную строку для константного выражения
                "values": [],  # у константной функции нет значений переменных
                "result": result,  # сохраняем вычисленный результат
            })

            return variables, table, result_name  # возвращаем пустой список переменных, таблицу и подпись результата

        for combo in itertools.product(range(self.k),
                                       repeat=len(variables)):  # перебираем все возможные наборы значений переменных
            assignment = dict(zip(variables, combo))  # собираем словарь значений переменных, например {"x": 3}
            result = self.evaluate_expression(expression, assignment)  # вычисляем значение формулы на текущем наборе
            result = int(result) % self.k  # приводим результат к диапазону k-значной логики

            row_values = [assignment[var] for var in
                          variables]  # формируем строку именно из значений переменных в правильном порядке

            table.append({  # добавляем строку в таблицу
                "values": row_values,  # сохраняем значения переменных, а не промежуточные вычисления верхнего уровня
                "result": result,  # сохраняем итоговое значение функции
            })

        return variables, table, result_name  # возвращаем переменные как заголовки, таблицу строк и имя результата
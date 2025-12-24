import re
import requests


def is_valid_card_number(card_number):
    """
    Проверяет номер карты по критериям:
    1. Ровно 16 цифр
    2. Первая цифра не 0
    3. Проходит алгоритм Луна
    """
    # Извлекаем только цифры
    digits = ''.join(filter(str.isdigit, card_number))

    # Критерий 1: ровно 16 цифр
    if len(digits) != 16:
        return False, f"Ошибка: найдено {len(digits)} цифр (нужно 16)"

    # Критерий 2: первая цифра не 0
    if digits[0] == '0':
        return False, "Ошибка: первая цифра не может быть 0"

    # Критерий 3: алгоритм Луна
    total = 0
    for i, digit in enumerate(reversed(digits)):
        n = int(digit)
        if i % 2 == 1:  # Каждая вторая цифра с конца
            n *= 2
            if n > 9:
                n -= 9
        total += n

    if total % 10 != 0:
        return False, "Ошибка: не проходит проверку алгоритмом Луна"

    return True, "Карта валидна"


def find_cards_in_text(text):
    """Находит валидные номера карт в тексте"""
    # Регулярное выражение: 16 цифр, первая не 0
    pattern = r'\b[1-9][0-9]{15}\b'
    matches = re.findall(pattern, text)

    valid_cards = []
    for card in matches:
        is_valid, message = is_valid_card_number(card)
        if is_valid:
            # Форматируем для вывода (XXXX XXXX XXXX XXXX)
            formatted = ' '.join([card[i:i + 4] for i in range(0, 16, 4)])
            valid_cards.append(formatted)

    return valid_cards


# 1. Режим пользовательского ввода
def user_input_mode():
    print("\n" + "=" * 50)
    print("РЕЖИМ РУЧНОГО ВВОДА")
    print("=" * 50)
    print("Вводите номера карт по одному.")
    print("Для завершения введите 'выход'")
    print("=" * 50)

    cards = []
    while True:
        card_input = input("\nВведите номер карты: ").strip()

        if card_input.lower() in ['выход', 'exit', 'quit']:
            break

        is_valid, message = is_valid_card_number(card_input)

        if is_valid:
            # Форматируем для вывода
            digits = ''.join(filter(str.isdigit, card_input))
            formatted = ' '.join([digits[i:i + 4] for i in range(0, 16, 4)])
            cards.append(formatted)
            print(message)
        else:
            print(message)

    return cards


# 2. Режим загрузки из файла
def file_input_mode():
    print("\n" + "=" * 50)
    print("РЕЖИМ ЗАГРУЗКИ ИЗ ФАЙЛА")
    print("=" * 50)

    filename = input("Введите имя файла: ").strip()

    try:
        with open(filename, 'r', encoding='utf-8') as file:
            content = file.read()

        cards = find_cards_in_text(content)

        print(f"\nЗагружено {len(content)} символов из файла")
        return cards

    except FileNotFoundError:
        print(f"Файл '{filename}' не найден")
        return []
    except Exception as e:
        print(f"Ошибка при чтении файла: {e}")
        return []


# 3. Режим загрузки с веб-страницы
def web_input_mode():
    print("\n" + "=" * 50)
    print("РЕЖИМ ЗАГРУЗКИ С ВЕБ-СТРАНИЦЫ")
    print("=" * 50)

    url = input("Введите URL: ").strip()

    try:
        print(f"Загружаем страницу: {url}")
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # Проверяем успешность запроса

        cards = find_cards_in_text(response.text)

        print(f"\nЗагружено {len(response.text)} символов с веб-страницы")
        return cards

    except requests.exceptions.RequestException as e:
        print(f"Ошибка при загрузке страницы: {e}")
        return []


def main():
    print("=" * 50)
    print("ПОИСК ВАЛИДНЫХ НОМЕРОВ БАНКОВСКИХ КАРТ")
    print("=" * 50)
    print("Критерии проверки:")
    print("1. Ровно 16 цифр")
    print("2. Первая цифра не 0")
    print("3. Проходит проверку алгоритмом Луна")
    print("=" * 50)

    while True:
        print("\nВыберите режим работы:")
        print("1. Ручной ввод номеров")
        print("2. Загрузка из файла")
        print("3. Загрузка с веб-страницы")
        print("4. Выход")

        choice = input("\nВаш выбор (1-4): ").strip()

        if choice == '1':
            cards = user_input_mode()
        elif choice == '2':
            cards = file_input_mode()
        elif choice == '3':
            cards = web_input_mode()
        elif choice == '4':
            print("\nВыход из программы...")
            break
        else:
            print("Неверный выбор. Попробуйте еще раз.")
            continue

        # Показываем результаты
        print("\n" + "=" * 50)
        print("РЕЗУЛЬТАТЫ ПОИСКА")
        print("=" * 50)

        if cards:
            print(f"Найдено валидных номеров карт: {len(cards)}")
            for i, card in enumerate(cards, 1):
                print(f"{i:3}. {card}")
        else:
            print("Валидные номера карт не найдены")

        print("=" * 50)

        # Спросим, хочет ли пользователь продолжить
        if choice != '4':
            continue_choice = input("\nПродолжить? (да/нет): ").strip().lower()
            if continue_choice not in ['да', 'д', 'yes', 'y']:
                print("\nВыход из программы...")
                break


if __name__ == "__main__":
    # Запускаем основную программу
    main()

# Пример URL: https://www.freeformatter.com/credit-card-number-generator-validator.html
import time


def apply_rule_110(left, center, right):
    """
    Математика Правила 110.
    111 -> 0, 110 -> 1, 101 -> 1, 100 -> 0
    011 -> 1, 010 -> 1, 001 -> 1, 000 -> 0
    """
    state = (left << 2) | (center << 1) | right
    # Вся магия вычислений Вселенной спрятана в одной битовой операции
    return (110 >> state) & 1


def run_turing_universe(width=120, steps=100, delay=0.05):
    # Создаем пустое пространство
    row = [0] * width

    # Для Правила 110 лучше всего "поджечь" Вселенную ближе к правому краю,
    # так как его структуры имеют тенденцию двигаться влево.
    row[width - 2] = 1

    print("Запуск Универсального Вычислителя (Правило 110)...")
    time.sleep(1)

    for step in range(steps):
        visual_row = "".join(['█' if cell else ' ' for cell in row])
        print(visual_row)

        time.sleep(delay)

        next_row = [0] * width
        for i in range(width):
            left = row[i - 1]
            center = row[i]
            right = row[(i + 1) % width]
            next_row[i] = apply_rule_110(left, center, right)

        row = next_row


if __name__ == "__main__":
    run_turing_universe(width=120, steps=100, delay=0.04)
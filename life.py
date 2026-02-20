import pygame
import random

# =========================================
# 0. ПАНЕЛЬ УПРАВЛЕНИЯ ВСЕЛЕННОЙ
# =========================================
# Левая кнопка мыши: Творить материю (можно просто зажать и водить мышкой, рисуя узоры).
# Правая кнопка мыши: Стирать материю (как ластик).
# Пробел (Space): Запустить или остановить время. (Лучше всего сначала поставить на паузу, нарисовать фигуру, а потом
# нажать пробел).
# Стрелка ВВЕРХ / ВНИЗ: Разгоняет или замедляет тактовую частоту симуляции (от 1 до 60 Гц).
# Клавиша R: Устроить Большой Взрыв (заполнить пространство случайным шумом, из которого сами начнут рождаться глайдеры
# и осцилляторы).
# Клавиша C: Конец света (мгновенно очистить поле).
# В этом интерфейсе особенно круто нажать R (залить всё случайным образом), нажать Пробел и наблюдать, как в течение
# пары минут первородный хаос самоупорядочивается, оставляя только стабильные "островки приводимости".


# =========================================
# 1. НАСТРОЙКИ ВСЕЛЕННОЙ И ГРАФИКИ
# =========================================
# Размеры окна и клеток
WIDTH, HEIGHT = 1000, 700
CELL_SIZE = 10  # Измените на 5 для огромной Вселенной или на 20 для крупной сетки
COLS, ROWS = WIDTH // CELL_SIZE, HEIGHT // CELL_SIZE

# Цветовая палитра "Матрица"
BG_COLOR = (10, 15, 10)  # Почти черный, слегка зеленоватый фон
GRID_COLOR = (20, 35, 20)  # Цвет сетки
ALIVE_COLOR = (0, 255, 65)  # Неоновый зеленый цвет живой клетки

# =========================================
# 2. ИНИЦИАЛИЗАЦИЯ PYGAME
# =========================================
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Клеточный Автомат: Матрица (Правила Конвея)")
clock = pygame.time.Clock()


def create_grid(randomize=False):
    """Создает двумерный массив (сетку) нулей. Если randomize=True, заполняет случайным образом."""
    if randomize:
        return [[random.choice([0, 1]) for _ in range(COLS)] for _ in range(ROWS)]
    return [[0 for _ in range(COLS)] for _ in range(ROWS)]


def draw_grid_lines():
    """Отрисовка линий сетки для удобства"""
    for x in range(0, WIDTH, CELL_SIZE):
        pygame.draw.line(screen, GRID_COLOR, (x, 0), (x, HEIGHT))
    for y in range(0, HEIGHT, CELL_SIZE):
        pygame.draw.line(screen, GRID_COLOR, (0, y), (WIDTH, y))


def draw_cells(grid):
    """Отрисовка живых клеток"""
    for row in range(ROWS):
        for col in range(COLS):
            if grid[row][col] == 1:
                # Рисуем квадрат с небольшим отступом (1 пиксель), чтобы было видно сетку
                rect = pygame.Rect(col * CELL_SIZE + 1, row * CELL_SIZE + 1, CELL_SIZE - 1, CELL_SIZE - 1)
                pygame.draw.rect(screen, ALIVE_COLOR, rect)


def count_neighbors(grid, row, col):
    """Подсчет живых соседей (с замыканием границ экрана в тор)"""
    count = 0
    for i in [-1, 0, 1]:
        for j in [-1, 0, 1]:
            if i == 0 and j == 0:
                continue
            r = (row + i) % ROWS
            c = (col + j) % COLS
            count += grid[r][c]
    return count


def update_universe(grid):
    """Вычисление следующего такта времени (Законы физики)"""
    new_grid = create_grid()
    for row in range(ROWS):
        for col in range(COLS):
            neighbors = count_neighbors(grid, row, col)

            # Правила Конвея
            if grid[row][col] == 1 and (neighbors == 2 or neighbors == 3):
                new_grid[row][col] = 1  # Выживание
            elif grid[row][col] == 0 and neighbors == 3:
                new_grid[row][col] = 1  # Рождение
            # В остальных случаях клетка умирает (в new_grid по умолчанию 0)

    return new_grid


# =========================================
# 3. ГЛАВНЫЙ ЦИКЛ ПРОГРАММЫ
# =========================================
def main():
    grid = create_grid()
    running = True  # Флаг работы приложения
    playing = False  # Флаг течения времени (пауза/пуск)
    fps = 10  # Начальная тактовая частота (кадров в секунду)

    while running:
        screen.fill(BG_COLOR)
        draw_grid_lines()
        draw_cells(grid)

        # Обновляем заголовок окна, чтобы выводить текущий статус
        status = "ИДЕТ ВЫЧИСЛЕНИЕ" if playing else "ПАУЗА (Режим редактирования)"
        pygame.display.set_caption(f"Клеточный Автомат | {status} | Частота: {fps} Гц")

        # Обработка событий (кнопки и мышь)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            # Обработка нажатий клавиш
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    playing = not playing  # Пуск / Пауза
                elif event.key == pygame.K_c:
                    grid = create_grid()  # Очистить Вселенную
                    playing = False
                elif event.key == pygame.K_r:
                    grid = create_grid(randomize=True)  # Случайный "Большой Взрыв"
                elif event.key == pygame.K_UP:
                    fps = min(180, fps + 5)  # Ускорить время (макс 180 Гц)
                elif event.key == pygame.K_DOWN:
                    fps = max(5, fps - 5)  # Замедлить время (мин 5 Гц)

            # Обработка мыши (Рисование материи)
            # Работает даже во время паузы!
            if pygame.mouse.get_pressed()[0]:  # Левая кнопка мыши
                pos = pygame.mouse.get_pos()
                c, r = pos[0] // CELL_SIZE, pos[1] // CELL_SIZE
                if 0 <= r < ROWS and 0 <= c < COLS:
                    grid[r][c] = 1  # Создать клетку

            elif pygame.mouse.get_pressed()[2]:  # Правая кнопка мыши
                pos = pygame.mouse.get_pos()
                c, r = pos[0] // CELL_SIZE, pos[1] // CELL_SIZE
                if 0 <= r < ROWS and 0 <= c < COLS:
                    grid[r][c] = 0  # Уничтожить клетку

        # Если время запущено - вычисляем следующий шаг
        if playing:
            grid = update_universe(grid)

        pygame.display.flip()

        # Если на паузе, крутим цикл на 60 FPS для плавности мыши.
        # Если время идет, ограничиваем частоту выбранным FPS.
        clock.tick(fps if playing else 60)

    pygame.quit()


if __name__ == "__main__":
    main()
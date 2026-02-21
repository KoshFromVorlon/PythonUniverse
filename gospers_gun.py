import pygame
import numpy as np
from scipy.signal import convolve2d

# ==========================================
# 1. НАСТРОЙКИ СИМУЛЯЦИИ И ОКНА
# ==========================================
CELL_SIZE = 12
WIDTH, HEIGHT = 1600, 900
COLS, ROWS = WIDTH // CELL_SIZE, HEIGHT // CELL_SIZE

BG_COLOR = (10, 15, 20)
CELL_COLOR = (0, 255, 150)  # Цвет живой клетки (информационного бита)

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Машина Тьюринга: Ружье Госпера (Пробел - Пауза, ESC - Выход)")
clock = pygame.time.Clock()

# Создаем пустую Вселенную (Двумерный массив нулей)
grid = np.zeros((ROWS, COLS), dtype=int)

# ==========================================
# 2. ЧЕРТЕЖ "ЖЕЛЕЗА" (Ружье Госпера)
# ==========================================
# 'O' - живая клетка, '.' - мертвая клетка
gun_pattern = [
    "........................O...........",
    "......................O.O...........",
    "............OO......OO............OO",
    "...........O...O....OO............OO",
    "OO........O.....O...OO..............",
    "OO........O...O.OO....O.O...........",
    "..........O.....O.......O...........",
    "...........O...O....................",
    "............OO......................"
]

# Впаиваем наш "процессор" в левый верхний угол сетки
start_r, start_c = 5, 5
for r, row in enumerate(gun_pattern):
    for c, val in enumerate(row):
        if val == 'O':
            grid[start_r + r, start_c + c] = 1

# ==========================================
# 3. МАТЕМАТИЧЕСКИЙ ДВИЖОК
# ==========================================
# Ядро свертки (Матрица Мура). Единицы вокруг нуля означают:
# "Собери информацию от всех 8 соседей, но не учитывай саму клетку"
kernel = np.array([[1, 1, 1],
                   [1, 0, 1],
                   [1, 1, 1]])

running = True
paused = False

print("Симуляция запущена. Матричные вычисления активны.")

while running:
    screen.fill(BG_COLOR)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            elif event.key == pygame.K_SPACE:
                paused = not paused

    if not paused:
        # МАГИЯ SCIPY: Одной строкой кода мы вычисляем количество
        # соседей для ВСЕХ десятков тысяч клеток на экране одновременно!
        # boundary='wrap' означает, что наша Вселенная свернута в тор (как в Pac-Man)
        neighbors = convolve2d(grid, kernel, mode='same', boundary='wrap')

        # ПРАВИЛА КОНВЕЯ (Булева логика над матрицами):
        # 1. (neighbors == 3) -> Мертвая клетка оживает, если ровно 3 соседа.
        # 2. ((grid == 1) & (neighbors == 2)) -> Живая клетка выживает, если 2 соседа.
        # Знак '|' (OR) объединяет эти два условия. Все остальное становится нулями.
        grid = ((neighbors == 3) | ((grid == 1) & (neighbors == 2))).astype(int)

    # ==========================================
    # РЕНДЕРИНГ
    # ==========================================
    # Находим координаты всех единиц в матрице
    y_coords, x_coords = np.where(grid == 1)

    # Рисуем все живые клетки
    for y, x in zip(y_coords, x_coords):
        # Рисуем квадратик чуть меньше размера ячейки, чтобы была видна сетка (CELL_SIZE - 1)
        pygame.draw.rect(screen, CELL_COLOR, (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE - 1, CELL_SIZE - 1))

    if paused:
        font = pygame.font.SysFont("Arial", 36, bold=True)
        text = font.render("ПАУЗА (Нажмите ПРОБЕЛ)", True, (255, 200, 50))
        screen.blit(text, (WIDTH // 2 - text.get_width() // 2, 50))

    pygame.display.flip()

    # Ставим ограничение в 30 кадров, иначе процессор отрендерит это
    # так быстро, что вы не успеете разглядеть, как летят "биты"
    clock.tick(30)

pygame.quit()

import pygame
import numpy as np
from scipy.signal import convolve2d

# ==========================================
# 1. НАСТРОЙКИ СИМУЛЯЦИИ
# ==========================================
CELL_SIZE = 12
BG_COLOR = (10, 15, 20)
CELL_COLOR = (0, 255, 150)
EATER_COLOR = (255, 50, 50)  # Подсветим защитника красным для наглядности

pygame.init()

screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
WIDTH, HEIGHT = screen.get_size()

pygame.display.set_caption("Машина Тьюринга: Защищенное Ружье Госпера")
clock = pygame.time.Clock()

COLS, ROWS = WIDTH // CELL_SIZE, HEIGHT // CELL_SIZE
grid = np.zeros((ROWS, COLS), dtype=int)

# ==========================================
# 2. ЧЕРТЕЖИ "ЖЕЛЕЗА"
# ==========================================

# --- Ружье Госпера (Генератор) ---
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

# --- Пожиратель-1 (Защита) ---
# Стабильная фигура, которая "съедает" глайдеры и восстанавливается.
eater_pattern = [
    "OO..",
    "O.O.",
    "..O.",
    "..OO"
]

# Размещаем Ружье (немного отступив от края)
gun_r, gun_c = 30, 30
for r, row in enumerate(gun_pattern):
    for c, val in enumerate(row):
        if val == 'O':
            grid[gun_r + r, gun_c + c] = 1

# Размещаем Пожирателя.
# Нам нужно поставить его "позади" ружья, на пути возвращающихся глайдеров.
# Ставим его выше и левее ружья. Используем % ROWS/COLS для безопасного размещения,
# даже если координаты уйдут в минус (они корректно обернутся).
eater_r = (gun_r - 15) % ROWS
eater_c = (gun_c - 15) % COLS

eater_coords = set()  # Запомним координаты едока для подкраски

for r, row in enumerate(eater_pattern):
    for c, val in enumerate(row):
        if val == 'O':
            # Вычисляем точные координаты с учетом зацикливания мира
            final_r = (eater_r + r) % ROWS
            final_c = (eater_c + c) % COLS
            grid[final_r, final_c] = 1
            eater_coords.add((final_r, final_c))

# ==========================================
# 3. МАТЕМАТИЧЕСКИЙ ДВИЖОК
# ==========================================
kernel = np.array([[1, 1, 1],
                   [1, 0, 1],
                   [1, 1, 1]])

running = True
paused = False
tick_rate = 60

font = pygame.font.SysFont("Arial", 28, bold=True)

while running:
    screen.fill(BG_COLOR)

    # ==========================================
    # ОБРАБОТКА УПРАВЛЕНИЯ
    # ==========================================
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            elif event.key == pygame.K_SPACE:
                paused = not paused
            elif event.key == pygame.K_UP:
                tick_rate = min(500, tick_rate + 10)  # Увеличил предел скорости
            elif event.key == pygame.K_DOWN:
                tick_rate = max(5, tick_rate - 10)

    # ==========================================
    # ФИЗИКА
    # ==========================================
    if not paused:
        # boundary='wrap' - Замкнутый мир (Тор)
        neighbors = convolve2d(grid, kernel, mode='same', boundary='wrap')
        grid = ((neighbors == 3) | ((grid == 1) & (neighbors == 2))).astype(int)

    # ==========================================
    # РЕНДЕРИНГ
    # ==========================================
    y_coords, x_coords = np.where(grid == 1)

    for y, x in zip(y_coords, x_coords):
        # Если клетка является частью изначального Пожирателя - рисуем красным
        # (Это приблизительная визуализация, т.к. едок деформируется в процессе)
        current_color = CELL_COLOR
        # Простая проверка: если клетка в зоне высадки едока
        r_dist = (y - eater_r + ROWS) % ROWS
        c_dist = (x - eater_c + COLS) % COLS
        if 0 <= r_dist < 4 and 0 <= c_dist < 4:
            current_color = EATER_COLOR

        pygame.draw.rect(screen, current_color, (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE - 1, CELL_SIZE - 1))

    # Интерфейс
    ui_text = f"Частота: {tick_rate} Гц | Ружье (Зеленое) + Защита (Красная) | ПРОБЕЛ: Пауза | ESC: Выход"
    text_surface = font.render(ui_text, True, (255, 255, 255))
    text_bg = pygame.Surface((text_surface.get_width() + 20, text_surface.get_height() + 10))
    text_bg.set_alpha(150)
    text_bg.fill((0, 0, 0))
    screen.blit(text_bg, (10, 10))
    screen.blit(text_surface, (20, 15))

    if paused:
        pause_text = font.render("ПАУЗА", True, (255, 50, 80))
        screen.blit(pause_text, (WIDTH // 2 - pause_text.get_width() // 2, HEIGHT // 2))

    pygame.display.flip()
    clock.tick(tick_rate)

pygame.quit()

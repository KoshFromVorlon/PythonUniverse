import pygame
import numpy as np
from scipy.signal import convolve2d

# ==========================================
# 1. НАСТРОЙКИ СИМУЛЯЦИИ И ЦВЕТОВ
# ==========================================
CELL_SIZE = 8  # Идеальный размер для 2K монитора
BG_COLOR = (8, 10, 15)

# Цвета наших 4-х квантовых пушек
COLORS = {
    1: (255, 50, 80),  # Красный (Левый Верх)
    2: (50, 255, 100),  # Зеленый (Правый Верх)
    3: (50, 150, 255),  # Синий (Правый Низ)
    4: (255, 200, 50)  # Желтый (Левый Низ)
}

pygame.init()
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
WIDTH, HEIGHT = screen.get_size()
pygame.display.set_caption("Машина Тьюринга: Независимая Юстировка")
clock = pygame.time.Clock()

COLS, ROWS = WIDTH // CELL_SIZE, HEIGHT // CELL_SIZE
grid = np.zeros((ROWS, COLS), dtype=int)

# ==========================================
# 2. ЧЕРТЕЖИ: ЧЕТЫРЕ РУЖЬЯ
# ==========================================
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

gun_TL = gun_pattern
gun_TR = [row[::-1] for row in gun_pattern]
gun_BR = [row[::-1] for row in reversed(gun_pattern)]
gun_BL = [row for row in reversed(gun_pattern)]

gun_h = len(gun_pattern)
gun_w = len(gun_pattern[0])

cr, cc = ROWS // 2, COLS // 2

# ПАРАМЕТРЫ НЕЗАВИСИМОЙ ЮСТИРОВКИ
align_13 = 0  # Сдвиг Синего ружья (Прицеливание 1-3)
align_24 = 0  # Сдвиг Желтого ружья (Прицеливание 2-4)
phase_shift = 4  # Сдвиг фазы для Зеленого и Желтого


def place_gun(pattern, start_r, start_c, color_id):
    for r, row in enumerate(pattern):
        for c, val in enumerate(row):
            if val == 'O':
                rr, cc_idx = start_r + r, start_c + c
                if 0 <= rr < ROWS and 0 <= cc_idx < COLS:
                    grid[rr, cc_idx] = color_id


def reset_world():
    """Мгновенно перестраивает Вселенную при настройке"""
    global grid
    grid.fill(0)

    D = min(cr - gun_h, cc - gun_w) - 10

    # 1. Красный (Левый Верх) - ЖЕСТКО ЗАФИКСИРОВАН
    r1, c1 = cr - D - gun_h, cc - D - gun_w

    # 3. Синий (Правый Низ) - ДВИГАЕТСЯ ПО ГОРИЗОНТАЛИ (align_13)
    # Это позволяет лучу "пройтись" поперек красного луча для точного прицела
    r3, c3 = cr + D, cc + D + align_13

    # 2. Зеленый (Правый Верх) - Сдвинут фазой (назад и вправо)
    r2, c2 = cr - D - gun_h - phase_shift, cc + D + phase_shift

    # 4. Желтый (Левый Низ) - Сдвинут фазой + ДВИГАЕТСЯ ПО ГОРИЗОНТАЛИ (align_24)
    r4, c4 = cr + D + phase_shift, cc - D - gun_w - phase_shift + align_24

    place_gun(gun_TL, r1, c1, 1)  # Красный
    place_gun(gun_TR, r2, c2, 2)  # Зеленый
    place_gun(gun_BR, r3, c3, 3)  # Синий
    place_gun(gun_BL, r4, c4, 4)  # Желтый


# Инициализируем мир
reset_world()

# ==========================================
# 3. МАТЕМАТИЧЕСКИЙ ДВИЖОК
# ==========================================
kernel = np.array([[1, 1, 1],
                   [1, 0, 1],
                   [1, 1, 1]])

running = True
paused = False
tick_rate = 120
font = pygame.font.SysFont("Arial", 22, bold=True)

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

            # Управление скоростью
            elif event.key == pygame.K_UP:
                tick_rate = min(400, tick_rate + 20)
            elif event.key == pygame.K_DOWN:
                tick_rate = max(5, tick_rate - 10)

            # Юстировка ПАРЫ 1-3 (Красный-Синий)
            elif event.key == pygame.K_RIGHT:
                align_13 += 1
                reset_world()
            elif event.key == pygame.K_LEFT:
                align_13 -= 1
                reset_world()

            # Юстировка ПАРЫ 2-4 (Зеленый-Желтый)
            elif event.key == pygame.K_d:
                align_24 += 1
                reset_world()
            elif event.key == pygame.K_a:
                align_24 -= 1
                reset_world()

            # Задержка фазы
            elif event.key == pygame.K_w:
                phase_shift += 1
                reset_world()
            elif event.key == pygame.K_s:
                phase_shift -= 1
                reset_world()

    # ==========================================
    # ФИЗИКА КОНВЕЯ (Мультиколор)
    # ==========================================
    if not paused:
        grid_b = (grid > 0).astype(int)
        neighbors = convolve2d(grid_b, kernel, mode='same', boundary='fill', fillvalue=0)

        survive = (grid_b == 1) & ((neighbors == 2) | (neighbors == 3))
        born = (grid_b == 0) & (neighbors == 3)

        new_grid = np.zeros_like(grid)
        new_grid[survive] = grid[survive]

        if np.any(born):
            c1_n = convolve2d((grid == 1).astype(int), kernel, mode='same', boundary='fill', fillvalue=0)
            c2_n = convolve2d((grid == 2).astype(int), kernel, mode='same', boundary='fill', fillvalue=0)
            c3_n = convolve2d((grid == 3).astype(int), kernel, mode='same', boundary='fill', fillvalue=0)
            c4_n = convolve2d((grid == 4).astype(int), kernel, mode='same', boundary='fill', fillvalue=0)

            color_stack = np.stack([c1_n, c2_n, c3_n, c4_n])
            dominant_color = np.argmax(color_stack, axis=0) + 1
            new_grid[born] = dominant_color[born]

        grid = new_grid

    # ==========================================
    # РЕНДЕРИНГ И ИНТЕРФЕЙС
    # ==========================================
    for color_id, color_rgb in COLORS.items():
        y_coords, x_coords = np.where(grid == color_id)
        for y, x in zip(y_coords, x_coords):
            pygame.draw.rect(screen, color_rgb, (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE - 1, CELL_SIZE - 1))

    # Телеметрия с инструкциями
    ui_texts = [
        f"1. Фокус КРАСНЫЙ-СИНИЙ: {align_13} [ВЛЕВО / ВПРАВО]",
        f"2. Фокус ЗЕЛЕНЫЙ-ЖЕЛТЫЙ: {align_24} [ A / D ]",
        f"3. Задержка фазы: {phase_shift} [ W / S ]",
        f"Частота: {tick_rate} Гц [ВВЕРХ/ВНИЗ] | ПРОБЕЛ: Пауза | ESC: Выход"
    ]

    panel_height = len(ui_texts) * 28 + 15
    pygame.draw.rect(screen, (0, 0, 0, 200), (10, 10, 520, panel_height))

    for i, text in enumerate(ui_texts):
        # Цветовая подсветка строк для интуитивности
        if i == 0:
            color = (255, 100, 100)
        elif i == 1:
            color = (100, 255, 100)
        elif i == 2:
            color = (255, 200, 50)
        else:
            color = (255, 255, 255)

        text_surface = font.render(text, True, color)
        screen.blit(text_surface, (20, 15 + i * 28))

    if paused:
        pause_text = font.render("ПАУЗА", True, (255, 50, 80))
        screen.blit(pause_text, (WIDTH // 2 - pause_text.get_width() // 2, HEIGHT // 2))

    pygame.display.flip()
    clock.tick(tick_rate)

pygame.quit()

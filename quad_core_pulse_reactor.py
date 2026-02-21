import pygame
import numpy as np
from scipy.signal import convolve2d

# ==========================================
# 1. НАСТРОЙКИ СИМУЛЯЦИИ И ЦВЕТОВ
# ==========================================
CELL_SIZE = 10  # На 2K мониторе это даст огромную, красивую сетку
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
pygame.display.set_caption("Машина Тьюринга: Идеальная Аннигиляция")
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

# ==========================================
# ИДЕАЛЬНАЯ ГЕОМЕТРИЯ (Независимо от разрешения!)
# ==========================================
cr, cc = ROWS // 2, COLS // 2  # Точный математический центр экрана

# Вычисляем максимальный отступ от центра, чтобы ружья поместились на экране
D = min(cr - gun_h, cc - gun_w) - 10

# Сдвиг фазы (Чтобы пары 1-3 и 2-4 не столкнулись в центре одновременно)
# Сдвиг на 4 клетки дает идеальную задержку в 16 тактов.
shift = 4
D2 = D + shift

# Расставляем ружья ИДЕАЛЬНО симметрично относительно центра (cr, cc)
r1, c1 = cr - D - gun_h, cc - D - gun_w  # 1. Красный (Левый Верх)
r3, c3 = cr + D, cc + D  # 3. Синий (Правый Низ)

r2, c2 = cr - D2 - gun_h, cc + D2  # 2. Зеленый (Правый Верх)
r4, c4 = cr + D2, cc - D2 - gun_w  # 4. Желтый (Левый Низ)


def place_gun(pattern, start_r, start_c, color_id):
    for r, row in enumerate(pattern):
        for c, val in enumerate(row):
            if val == 'O':
                grid[start_r + r, start_c + c] = color_id


place_gun(gun_TL, r1, c1, 1)  # Красный
place_gun(gun_TR, r2, c2, 2)  # Зеленый
place_gun(gun_BR, r3, c3, 3)  # Синий
place_gun(gun_BL, r4, c4, 4)  # Желтый

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

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            elif event.key == pygame.K_SPACE:
                paused = not paused
            elif event.key == pygame.K_UP:
                tick_rate = min(300, tick_rate + 10)
            elif event.key == pygame.K_DOWN:
                tick_rate = max(5, tick_rate - 10)

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
    # РЕНДЕРИНГ
    # ==========================================
    for color_id, color_rgb in COLORS.items():
        y_coords, x_coords = np.where(grid == color_id)
        for y, x in zip(y_coords, x_coords):
            pygame.draw.rect(screen, color_rgb, (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE - 1, CELL_SIZE - 1))

    # Телеметрия с разрешением экрана
    ui_text = f"Частота: {tick_rate} Гц | Смещение фазы: АКТИВНО | Экран: {WIDTH}x{HEIGHT} | ESC: Выход"
    text_surface = font.render(ui_text, True, (255, 255, 255))
    text_bg = pygame.Surface((text_surface.get_width() + 20, text_surface.get_height() + 10))
    text_bg.set_alpha(150)
    screen.blit(text_bg, (10, 10))
    screen.blit(text_surface, (20, 15))

    if paused:
        pause_text = font.render("ПАУЗА", True, (255, 50, 80))
        screen.blit(pause_text, (WIDTH // 2 - pause_text.get_width() // 2, HEIGHT // 2))

    pygame.display.flip()
    clock.tick(tick_rate)

pygame.quit()
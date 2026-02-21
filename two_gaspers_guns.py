import pygame
import numpy as np
from scipy.signal import convolve2d

# ==========================================
# 1. НАСТРОЙКИ СИМУЛЯЦИИ И ОКНА
# ==========================================
CELL_SIZE = 12
BG_COLOR = (10, 15, 20)
CELL_COLOR = (0, 255, 150)  # Неоново-зеленый

pygame.init()

# Включаем полноэкранный режим
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
WIDTH, HEIGHT = screen.get_size()

pygame.display.set_caption("Машина Тьюринга: Встречная Аннигиляция")
clock = pygame.time.Clock()

COLS, ROWS = WIDTH // CELL_SIZE, HEIGHT // CELL_SIZE
grid = np.zeros((ROWS, COLS), dtype=int)

# ==========================================
# 2. ЧЕРТЕЖИ: ДВА РУЖЬЯ (СИММЕТРИЯ 180 ГРАДУСОВ)
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

# Ружье 1 (Оригинал, стреляет вправо-вниз)
gun1 = gun_pattern

# Ружье 2 (Отражено по горизонтали и вертикали, стреляет влево-вверх)
gun2 = [row[::-1] for row in reversed(gun_pattern)]

# Вычисляем идеальное расстояние по диагонали, чтобы они смотрели точно друг на друга
margin = 10
gun_h = len(gun1)
gun_w = len(gun1[0])

# Максимальная диагональ, которая влезет в ваш экран
dist = min(ROWS - 2 * margin - gun_h, COLS - 2 * margin - gun_w)

r1, c1 = margin, margin
r2, c2 = margin + dist, margin + dist

# Впаиваем Ружье 1 (Верхний левый угол)
for r, row in enumerate(gun1):
    for c, val in enumerate(row):
        if val == 'O':
            grid[r1 + r, c1 + c] = 1

# Впаиваем Ружье 2 (Нижний правый угол)
for r, row in enumerate(gun2):
    for c, val in enumerate(row):
        if val == 'O':
            grid[r2 + r, c2 + c] = 1

# ==========================================
# 3. МАТЕМАТИЧЕСКИЙ ДВИЖОК
# ==========================================
kernel = np.array([[1, 1, 1],
                   [1, 0, 1],
                   [1, 1, 1]])

running = True
paused = False
tick_rate = 60  # Стартовая частота
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

            # Управление частотой (Ограничиваем от 5 до 250 Гц)
            elif event.key == pygame.K_UP:
                tick_rate = min(250, tick_rate + 5)
            elif event.key == pygame.K_DOWN:
                tick_rate = max(5, tick_rate - 5)

    # ==========================================
    # ФИЗИКА КОНВЕЯ
    # ==========================================
    if not paused:
        # Замкнутый мир (Тор)
        neighbors = convolve2d(grid, kernel, mode='same', boundary='wrap')
        grid = ((neighbors == 3) | ((grid == 1) & (neighbors == 2))).astype(int)

    # ==========================================
    # РЕНДЕРИНГ
    # ==========================================
    y_coords, x_coords = np.where(grid == 1)

    for y, x in zip(y_coords, x_coords):
        pygame.draw.rect(screen, CELL_COLOR, (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE - 1, CELL_SIZE - 1))

    # Телеметрия
    ui_text = f"Частота: {tick_rate} Гц (Стрелки ВВЕРХ/ВНИЗ) | ПРОБЕЛ: Пауза | ESC: Выход"
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
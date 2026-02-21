import pygame
import numpy as np
from scipy.signal import convolve2d

# ==========================================
# 1. НАСТРОЙКИ СИМУЛЯЦИИ
# ==========================================
CELL_SIZE = 12
BG_COLOR = (10, 15, 20)
CELL_COLOR = (0, 255, 150)  # Неоново-зеленый цвет живой клетки

pygame.init()

# Включаем полноэкранный режим и автоматически определяем разрешение
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
WIDTH, HEIGHT = screen.get_size()

pygame.display.set_caption("Машина Тьюринга: Ружье Госпера (Замкнутая Вселенная)")
clock = pygame.time.Clock()

# Вычисляем количество ячеек так, чтобы они заполнили весь экран
COLS, ROWS = WIDTH // CELL_SIZE, HEIGHT // CELL_SIZE
grid = np.zeros((ROWS, COLS), dtype=int)

# ==========================================
# 2. ЧЕРТЕЖ "ЖЕЛЕЗА" (Ружье Госпера)
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

# Впаиваем процессор немного отступив от левого верхнего края
start_r, start_c = 10, 10
for r, row in enumerate(gun_pattern):
    for c, val in enumerate(row):
        if val == 'O':
            grid[start_r + r, start_c + c] = 1

# ==========================================
# 3. МАТЕМАТИЧЕСКИЙ ДВИЖОК
# ==========================================
kernel = np.array([[1, 1, 1],
                   [1, 0, 1],
                   [1, 1, 1]])

running = True
paused = False
tick_rate = 60  # Стартовая частота симуляции (Гц)

# Шрифт для интерфейса
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
    # ФИЗИКА КОНВЕЯ (С матричными вычислениями)
    # ==========================================
    if not paused:
        # ВОЗВРАЩЕНО: boundary='wrap' сворачивает экран в тор (бублик).
        # Глайдеры, улетевшие за правый край, вернутся слева!
        neighbors = convolve2d(grid, kernel, mode='same', boundary='wrap')

        # Логика Жизни (векторные вычисления)
        grid = ((neighbors == 3) | ((grid == 1) & (neighbors == 2))).astype(int)

    # ==========================================
    # РЕНДЕРИНГ
    # ==========================================
    # Находим все единицы (живые клетки)
    y_coords, x_coords = np.where(grid == 1)

    # Отрисовываем их квадратами
    for y, x in zip(y_coords, x_coords):
        pygame.draw.rect(screen, CELL_COLOR, (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE - 1, CELL_SIZE - 1))

    # Отрисовка интерфейса (Телеметрия)
    ui_text = f"Частота: {tick_rate} Гц (Стрелки ВВЕРХ/ВНИЗ) | ПРОБЕЛ: Пауза | ESC: Выход"
    text_surface = font.render(ui_text, True, (255, 255, 255))

    # Делаем полупрозрачную подложку для текста, чтобы он читался поверх глайдеров
    text_bg = pygame.Surface((text_surface.get_width() + 20, text_surface.get_height() + 10))
    text_bg.set_alpha(150)
    text_bg.fill((0, 0, 0))

    screen.blit(text_bg, (10, 10))
    screen.blit(text_surface, (20, 15))

    if paused:
        pause_text = font.render("ПАУЗА", True, (255, 50, 80))
        screen.blit(pause_text, (WIDTH // 2 - pause_text.get_width() // 2, HEIGHT // 2))

    pygame.display.flip()

    # Применяем заданную пользователем частоту
    clock.tick(tick_rate)

pygame.quit()

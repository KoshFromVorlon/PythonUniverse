import pygame
import math

# Настройки окна
WIDTH, HEIGHT = 800, 800
BG_COLOR = (10, 10, 20)  # Цвет глубокого космоса
GRID_COLOR = (50, 150, 255)  # Цвет линий пространства-времени

# Настройки симуляции
GRID_SPACING = 40  # Расстояние между узлами сетки
GRAVITY_STRENGTH = 0.5  # Сила притяжения центральной массы
TIME_STEP = 1  # Скорость симуляции

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Вольфрамовская Гравитация: Искривление Графа")
clock = pygame.time.Clock()

# 1. Создаем "Плоское пространство" (начальный граф)
# Это просто список точек с координатами [x, y]
points = []
cols = WIDTH // GRID_SPACING + 1
rows = HEIGHT // GRID_SPACING + 1
for i in range(cols):
    for j in range(rows):
        points.append([i * GRID_SPACING, j * GRID_SPACING])

# Центр экрана - туда мы поместим "черную дыру"
center_x, center_y = WIDTH // 2, HEIGHT // 2

running = True
while running:
    screen.fill(BG_COLOR)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # 2. Применяем "Правило обновления" (Физику)
    # Каждый узел графа "хочет" притянуться к центру массы.
    # Чем ближе узел к центру, тем сильнее искажение.
    for p in points:
        dx = center_x - p[0]
        dy = center_y - p[1]
        distance_sq = dx * dx + dy * dy + 1  # +1 чтобы избежать деления на ноль
        distance = math.sqrt(distance_sq)

        # Сила притяжения обратно пропорциональна расстоянию (как у Ньютона)
        # Это упрощенная модель, но она передает суть искажения сетки.
        if distance > 20:  # Не стягиваем совсем в сингулярность
            move_x = (dx / distance) * (GRAVITY_STRENGTH * 1000 / distance_sq)
            move_y = (dy / distance) * (GRAVITY_STRENGTH * 1000 / distance_sq)
            p[0] += move_x * TIME_STEP
            p[1] += move_y * TIME_STEP

    # 3. Отрисовка искривленного пространства
    # Мы рисуем линии между соседними точками, чтобы видеть геометрию сетки.
    for i in range(cols):
        for j in range(rows):
            idx = i * rows + j
            current_point = points[idx]

            # Рисуем горизонтальную связь (если есть сосед справа)
            if i < cols - 1:
                right_neighbor = points[(i + 1) * rows + j]
                pygame.draw.line(screen, GRID_COLOR, current_point, right_neighbor, 1)

            # Рисуем вертикальную связь (если есть сосед снизу)
            if j < rows - 1:
                bottom_neighbor = points[i * rows + (j + 1)]
                pygame.draw.line(screen, GRID_COLOR, current_point, bottom_neighbor, 1)

            # Рисуем сам узел (опционально)
            # pygame.draw.circle(screen, GRID_COLOR, (int(current_point[0]), int(current_point[1])), 2)

    # Рисуем "Черную дыру" в центре для наглядности
    pygame.draw.circle(screen, (0, 0, 0), (center_x, center_y), 15)
    pygame.draw.circle(screen, (255, 50, 50), (center_x, center_y), 15, 2)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()

import pygame
import math

# ==========================================
# 1. НАСТРОЙКИ СИМУЛЯЦИИ И ОКНА
# ==========================================
WIDTH, HEIGHT = 1920, 1080
BG_COLOR = (10, 15, 20)  # Глубокий космос
GRID_COLOR = (0, 255, 150)  # Неоновая сетка
SURFACE_COLOR = (5, 8, 12, 190)  # Полупрозрачное пространство
MASS_COLOR = (255, 50, 80)  # Цвет Черной дыры

# Настройки сетки и физики
COLS, ROWS = 50, 50
SPACING = 30  # Расстояние между узлами
BASE_GRAVITY = 15000  # Стартовая гравитация (слабая воронка)
MASS_PER_NODE = 800  # Сколько массы добавляет один "съеденный" узел
Z_SCALE = 0.015  # Масштаб глубины (чтобы воронка не пробила экран)

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("3D Гиперграф: Поглощение Пространства (Пауза - Пробел, Камера - Мышь)")
clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 36, bold=True)

CX = (COLS - 1) * SPACING / 2.0
CY = (ROWS - 1) * SPACING / 2.0

# Структура узла: [x, y, z, anchor_x, anchor_y, is_consumed]
grid = []
for i in range(COLS):
    row_pts = []
    for j in range(ROWS):
        x = i * SPACING
        y = j * SPACING
        # 6-й элемент (False) означает, что узел еще "жив" и не съеден
        row_pts.append([x, y, 0.0, x, y, False])
    grid.append(row_pts)


def project_3d_to_2d(x, y, z, angle_z, tilt):
    """ Проекция 3D в 2D с учетом наклона и вращения камеры """
    X = x - CX
    Z = y - CY
    Y = z

    # Вращение по оси Z (вокруг воронки)
    X_rot = X * math.cos(angle_z) - Z * math.sin(angle_z)
    Z_rot = X * math.sin(angle_z) + Z * math.cos(angle_z)

    # Наклон камеры
    Y_tilt = Y * math.cos(tilt) + Z_rot * math.sin(tilt)
    Z_tilt = -Y * math.sin(tilt) + Z_rot * math.cos(tilt)

    distance = 1500
    fov = 1200
    Z_final = Z_tilt + distance
    factor = fov / Z_final if Z_final > 0 else 0.1

    screen_x = X_rot * factor + WIDTH / 2
    screen_y = -Y_tilt * factor + HEIGHT / 2 - 150

    return screen_x, screen_y, Z_final


# Переменные управления
camera_angle = 0.0
camera_tilt = math.radians(45)
is_paused = False
is_dragging = False
last_mouse_pos = (0, 0)

current_gravity = BASE_GRAVITY
nodes_captured = 0

running = True
while running:
    screen.fill(BG_COLOR)

    # ==========================================
    # ОБРАБОТКА УПРАВЛЕНИЯ
    # ==========================================
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # Нажатие пробела для паузы
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                is_paused = not is_paused

        # Управление мышью (Вращение камеры)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Левая кнопка
                is_dragging = True
                last_mouse_pos = event.pos
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                is_dragging = False
        elif event.type == pygame.MOUSEMOTION:
            if is_dragging:
                dx = event.pos[0] - last_mouse_pos[0]
                dy = event.pos[1] - last_mouse_pos[1]
                camera_angle -= dx * 0.005
                camera_tilt += dy * 0.005
                # Ограничиваем наклон, чтобы не переворачивать мир вверх ногами
                camera_tilt = max(0.1, min(math.pi / 2 - 0.1, camera_tilt))
                last_mouse_pos = event.pos

    # Медленное авто-вращение, если не на паузе и не держим мышь
    if not is_paused and not is_dragging:
        camera_angle += 0.00075  # Скорость вращения уменьшена вдвое!

    # ==========================================
    # ФИЗИКА (Только если нет паузы)
    # ==========================================
    if not is_paused:
        # 1. Считаем массу (зависит ТОЛЬКО от съеденных узлов)
        target_gravity = BASE_GRAVITY + (nodes_captured * MASS_PER_NODE)
        current_gravity += (target_gravity - current_gravity) * 0.02  # Плавный рост

        # Горизонт событий (радиус поглощения) немного растет вместе с массой
        event_horizon = 15 + (current_gravity / 50000)

        # 2. Обновляем узлы
        for i in range(COLS):
            for j in range(ROWS):
                p = grid[i][j]
                if p[5]:  # Если узел уже поглощен - пропускаем
                    continue

                # Расстояние от базовой точки узла до центра
                dx = CX - p[3]
                dy = CY - p[4]
                dist_orig = math.hypot(dx, dy)
                if dist_orig < 1: dist_orig = 1

                # Сила притяжения. Если она достаточно сильная, узел начинает скользить в дыру
                pull_force = current_gravity / (dist_orig * dist_orig)
                if pull_force > 0.05:
                    # Максимальная скорость падения - 4 пикселя за кадр (плавно!)
                    slip = min(pull_force * 0.1, 4.0)
                    p[3] += (dx / dist_orig) * slip
                    p[4] += (dy / dist_orig) * slip

                # Пересчитываем дистанцию после сдвига
                dx = CX - p[3]
                dy = CY - p[4]
                dist_orig = math.hypot(dx, dy)
                if dist_orig < 1: dist_orig = 1

                # Проверка: Попал ли узел за Горизонт событий?
                if dist_orig < event_horizon:
                    p[5] = True  # Уничтожаем узел!
                    nodes_captured += 1
                    continue

                # Высчитываем глубину (Z)
                p[2] = - (current_gravity / (dist_orig + 20)) * Z_SCALE

                # Высчитываем натяжение сетки (X, Y)
                stretch = current_gravity * 0.03 / (dist_orig + 10)
                stretch = min(stretch, dist_orig * 0.9)
                p[0] = p[3] + (dx / dist_orig) * stretch
                p[1] = p[4] + (dy / dist_orig) * stretch

    # ==========================================
    # РЕНДЕРИНГ
    # ==========================================
    polygons = []

    # Собираем квадраты
    for i in range(COLS - 1):
        for j in range(ROWS - 1):
            p1 = grid[i][j]
            p2 = grid[i + 1][j]
            p3 = grid[i + 1][j + 1]
            p4 = grid[i][j + 1]

            # ВАЖНО: Если хотя бы один угол квадрата съеден черной дырой -
            # мы больше не рисуем этот кусок ткани! В сетке появляется реальная дыра.
            if p1[5] or p2[5] or p3[5] or p4[5]:
                continue

            sx1, sy1, z1 = project_3d_to_2d(p1[0], p1[1], p1[2], camera_angle, camera_tilt)
            sx2, sy2, z2 = project_3d_to_2d(p2[0], p2[1], p2[2], camera_angle, camera_tilt)
            sx3, sy3, z3 = project_3d_to_2d(p3[0], p3[1], p3[2], camera_angle, camera_tilt)
            sx4, sy4, z4 = project_3d_to_2d(p4[0], p4[1], p4[2], camera_angle, camera_tilt)

            avg_z = (z1 + z2 + z3 + z4) / 4

            polygons.append({
                'pts': [(sx1, sy1), (sx2, sy2), (sx3, sy3), (sx4, sy4)],
                'z': avg_z
            })

    # Сингулярность
    z_depth = - (current_gravity / 20) * Z_SCALE - 30
    bx, by, bz = project_3d_to_2d(CX, CY, z_depth, camera_angle, camera_tilt)
    # Размер черной дыры медленно растет от 5 до 40 пикселей по мере насыщения
    bh_radius = max(5, int((current_gravity / 1500000) * 40))

    polygons.append({
        'type': 'singularity',
        'pts': (bx, by),
        'z': bz,
        'radius': bh_radius
    })

    polygons.sort(key=lambda item: item['z'], reverse=True)

    alpha_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)

    for poly in polygons:
        if 'type' in poly and poly['type'] == 'singularity':
            pygame.draw.circle(alpha_surface, MASS_COLOR, (int(poly['pts'][0]), int(poly['pts'][1])), poly['radius'])
            pygame.draw.circle(alpha_surface, (255, 255, 255), (int(poly['pts'][0]), int(poly['pts'][1])),
                               max(2, int(poly['radius'] / 3)))
        else:
            pygame.draw.polygon(alpha_surface, SURFACE_COLOR, poly['pts'])
            pygame.draw.polygon(alpha_surface, GRID_COLOR, poly['pts'], 1)

    screen.blit(alpha_surface, (0, 0))

    # Рисуем интерфейс
    pygame.display.set_caption(f"Масса: {int(current_gravity)} | Поглощено: {nodes_captured} / 2500")
    if is_paused:
        pause_text = font.render("ПАУЗА (Нажмите ПРОБЕЛ для старта)", True, (255, 200, 50))
        screen.blit(pause_text, (WIDTH // 2 - pause_text.get_width() // 2, 50))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
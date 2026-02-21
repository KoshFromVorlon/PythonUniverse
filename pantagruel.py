import pygame
import math

# ==========================================
# 1. НАСТРОЙКИ СИМУЛЯЦИИ И ОКНА
# ==========================================
WIDTH, HEIGHT = 1920, 1080
BG_COLOR = (8, 10, 15)  # Глубокий космос
GRID_COLOR = (0, 255, 180)  # Неоновая сетка
SURFACE_COLOR = (4, 6, 10, 160)
MASS_COLOR = (255, 30, 50)  # Цвет Черной дыры

# Настройки сетки
COLS, ROWS = 70, 70  # Плотная симметричная матрица
SPACING = 25
Z_SCALE = 0.015  # Масштаб глубины
BASE_GRAVITY = 10000
MASS_PER_NODE = 500
MAX_GRAVITY = 3000000

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("3D Гиперграф: Вращающаяся Черная Дыра (Плавная механика)")
clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 36, bold=True)

# Идеально симметричный центр
CX = (COLS - 1) * SPACING / 2.0
CY = (ROWS - 1) * SPACING / 2.0

grid = []
for i in range(COLS):
    row_pts = []
    for j in range(ROWS):
        orig_x = i * SPACING
        orig_y = j * SPACING

        dx = orig_x - CX
        dy = orig_y - CY
        dist = math.hypot(dx, dy)
        if dist < 0.1: dist = 0.1
        angle = math.atan2(dy, dx)

        # [Угол, Дистанция, X, Y, Z, Съеден_ли]
        row_pts.append([angle, dist, orig_x, orig_y, 0.0, False])
    grid.append(row_pts)


def project_3d_to_2d(x, y, z, angle_z, tilt):
    X = x - CX
    Z = y - CY
    Y = z

    X_rot = X * math.cos(angle_z) - Z * math.sin(angle_z)
    Z_rot = X * math.sin(angle_z) + Z * math.cos(angle_z)

    Y_tilt = Y * math.cos(tilt) + Z_rot * math.sin(tilt)
    Z_tilt = -Y * math.sin(tilt) + Z_rot * math.cos(tilt)

    distance = 1500
    fov = 1200
    Z_final = Z_tilt + distance
    factor = fov / Z_final if Z_final > 0 else 0.1

    screen_x = X_rot * factor + WIDTH / 2
    screen_y = -Y_tilt * factor + HEIGHT / 2 - 100

    return screen_x, screen_y, Z_final, factor


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

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                is_paused = not is_paused
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
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
                camera_tilt = max(0.1, min(math.pi / 2 - 0.1, camera_tilt))
                last_mouse_pos = event.pos

    if not is_paused and not is_dragging:
        # ЗАМЕДЛЕНИЕ КАМЕРЫ (было 0.001, стало 0.0003)
        camera_angle += 0.0003

    # ==========================================
    # ФИЗИКА: СОХРАНЕНИЕ МОМЕНТА ИМПУЛЬСА
    # ==========================================
    if not is_paused:
        target_gravity = BASE_GRAVITY + (nodes_captured * MASS_PER_NODE)
        target_gravity = min(target_gravity, MAX_GRAVITY)
        current_gravity += (target_gravity - current_gravity) * 0.015

        event_horizon = 10 + (current_gravity / 50000)

        for i in range(COLS):
            for j in range(ROWS):
                p = grid[i][j]

                # 1. ЗАМЕДЛЕННОЕ И СГЛАЖЕННОЕ ЗАКРУЧИВАНИЕ
                # Увеличил делитель (+80 вместо +20), чтобы соседние узлы вращались
                # более синхронно. Это убирает угловатость и "рваные" полигоны.
                spin_speed = (current_gravity * 0.000003) / (p[1] + 80)
                p[0] += spin_speed

                if not p[5]:
                    # 2. БОЛЕЕ ПЛАВНОЕ ПРИТЯЖЕНИЕ
                    pull = (current_gravity * 0.01) / (p[1] * p[1] + 150)
                    p[1] -= pull

                    if p[1] <= event_horizon:
                        p[1] = event_horizon
                        p[5] = True
                        nodes_captured += 1
                else:
                    p[1] = event_horizon

                # Возвращаем координаты на место (отступы исправлены)
                p[2] = CX + math.cos(p[0]) * p[1]
                p[3] = CY + math.sin(p[0]) * p[1]

                # Формируем глубину воронки (Z) (чуть расширил дно, чтобы сгладить пик)
                p[4] = - (current_gravity / (p[1] + 15)) * Z_SCALE

    # ==========================================
    # РЕНДЕРИНГ
    # ==========================================
    polygons = []

    for i in range(COLS - 1):
        for j in range(ROWS - 1):
            p1 = grid[i][j]
            p2 = grid[i + 1][j]
            p3 = grid[i + 1][j + 1]
            p4 = grid[i][j + 1]

            sx1, sy1, z1, _ = project_3d_to_2d(p1[2], p1[3], p1[4], camera_angle, camera_tilt)
            sx2, sy2, z2, _ = project_3d_to_2d(p2[2], p2[3], p2[4], camera_angle, camera_tilt)
            sx3, sy3, z3, _ = project_3d_to_2d(p3[2], p3[3], p3[4], camera_angle, camera_tilt)
            sx4, sy4, z4, _ = project_3d_to_2d(p4[2], p4[3], p4[4], camera_angle, camera_tilt)

            avg_z = (z1 + z2 + z3 + z4) / 4

            polygons.append({
                'pts': [(sx1, sy1), (sx2, sy2), (sx3, sy3), (sx4, sy4)],
                'z': avg_z
            })

    horizon_z = - (current_gravity / (event_horizon + 15)) * Z_SCALE
    bx, by, bz, factor = project_3d_to_2d(CX, CY, horizon_z, camera_angle, camera_tilt)

    # ХИТРОСТЬ: Делаем черную дыру на пару пикселей шире горизонта событий,
    # чтобы она визуально перекрывала собой все "острые" углы смятой сетки.
    screen_radius = max(2, int((event_horizon + 5) * factor))

    polygons.append({
        'type': 'singularity',
        'pts': (bx, by),
        'z': bz,
        'radius': screen_radius
    })

    polygons.sort(key=lambda item: item['z'], reverse=True)

    alpha_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)

    for poly in polygons:
        if 'type' in poly and poly['type'] == 'singularity':
            pygame.draw.circle(alpha_surface, MASS_COLOR, (int(poly['pts'][0]), int(poly['pts'][1])), poly['radius'])
            pygame.draw.circle(alpha_surface, (255, 255, 255), (int(poly['pts'][0]), int(poly['pts'][1])),
                               max(1, int(poly['radius'] * 0.3)))
        else:
            pygame.draw.polygon(alpha_surface, SURFACE_COLOR, poly['pts'])
            pygame.draw.polygon(alpha_surface, GRID_COLOR, poly['pts'], 1)

    screen.blit(alpha_surface, (0, 0))

    pygame.display.set_caption(
        f"Масса: {int(current_gravity)} / {MAX_GRAVITY} | Поглощено: {nodes_captured} узлов | Орбитальная механика активна")
    if is_paused:
        pause_text = font.render("ПАУЗА (Нажмите ПРОБЕЛ для старта)", True, (255, 200, 50))
        screen.blit(pause_text, (WIDTH // 2 - pause_text.get_width() // 2, 50))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
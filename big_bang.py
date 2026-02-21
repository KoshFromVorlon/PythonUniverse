import pygame
import math
import random

# ==========================================
# 1. НАСТРОЙКИ СИМУЛЯЦИИ И ОКНА
# ==========================================
BG_COLOR = (10, 15, 20)
NODE_COLOR = (255, 200, 50)
EDGE_COLOR = (0, 255, 150)

pygame.init()

# ИЗМЕНЕНИЕ: Включаем полноэкранный режим и автоматически получаем размер экрана
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
WIDTH, HEIGHT = screen.get_size()

pygame.display.set_caption("3D Эволюция Вольфрама (Пробел - Эволюция, Мышь - Вращение, ESC - Выход)")
clock = pygame.time.Clock()

# ==========================================
# 2. ИСТИННАЯ ФИЗИКА ВОЛЬФРАМА (Граф)
# ==========================================
nodes = {1: [random.uniform(-10, 10), random.uniform(-10, 10), random.uniform(-10, 10)],
         2: [random.uniform(-10, 10), random.uniform(-10, 10), random.uniform(-10, 10)]}
edges = [(1, 2)]
next_node_id = 3
universe_age = 0


def evolve_universe():
    global edges, next_node_id, universe_age
    new_edges = []

    for u, v in edges:
        c = next_node_id
        d = next_node_id + 1
        next_node_id += 2

        nodes[c] = [nodes[u][0] + random.uniform(-5, 5), nodes[u][1] + random.uniform(-5, 5),
                    nodes[u][2] + random.uniform(-5, 5)]
        nodes[d] = [nodes[v][0] + random.uniform(-5, 5), nodes[v][1] + random.uniform(-5, 5),
                    nodes[v][2] + random.uniform(-5, 5)]

        new_edges.extend([(u, c), (c, v), (u, d), (d, v)])

    edges = new_edges
    universe_age += 1


# ==========================================
# 3. 3D-ДВИЖОК И СИЛОВАЯ РАСКЛАДКА
# ==========================================
def project_3d_to_2d(x, y, z, angle_y, angle_x):
    x_rot = x * math.cos(angle_y) - z * math.sin(angle_y)
    z_rot = x * math.sin(angle_y) + z * math.cos(angle_y)

    y_rot = y * math.cos(angle_x) - z_rot * math.sin(angle_x)
    z_final = y * math.sin(angle_x) + z_rot * math.cos(angle_x)

    # Слегка отодвинул камеру, чтобы на большом экране всё смотрелось гармонично
    distance = 800
    fov = 800
    z_adj = z_final + distance
    factor = fov / z_adj if z_adj > 0 else 0.1

    screen_x = x_rot * factor + WIDTH / 2
    screen_y = y_rot * factor + HEIGHT / 2

    return screen_x, screen_y, z_final


camera_angle_y = 0.0
camera_angle_x = 0.0
is_dragging = False
last_mouse_pos = (0, 0)

running = True
while running:
    screen.fill(BG_COLOR)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            # ИЗМЕНЕНИЕ: Добавлен выход по клавише ESCAPE
            if event.key == pygame.K_ESCAPE:
                running = False
            elif event.key == pygame.K_SPACE:
                # Ограничитель, чтобы процессор не сгорел на 6-7 шаге
                if universe_age < 6:
                    evolve_universe()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            is_dragging = True
            last_mouse_pos = event.pos
        elif event.type == pygame.MOUSEBUTTONUP:
            is_dragging = False
        elif event.type == pygame.MOUSEMOTION:
            if is_dragging:
                dx = event.pos[0] - last_mouse_pos[0]
                dy = event.pos[1] - last_mouse_pos[1]
                camera_angle_y -= dx * 0.01
                camera_angle_x -= dy * 0.01
                last_mouse_pos = event.pos

    if not is_dragging:
        camera_angle_y += 0.003  # Плавное вращение

    # ==========================================
    # РАСЧЕТ СИЛ (Отталкивание и Притяжение)
    # ==========================================
    node_ids = list(nodes.keys())
    for i in range(len(node_ids)):
        for j in range(i + 1, len(node_ids)):
            n1, n2 = node_ids[i], node_ids[j]
            p1, p2 = nodes[n1], nodes[n2]

            dx = p1[0] - p2[0]
            dy = p1[1] - p2[1]
            dz = p1[2] - p2[2]
            dist_sq = dx * dx + dy * dy + dz * dz + 1
            dist = math.sqrt(dist_sq)

            if dist < 400:
                force = 600 / dist_sq
                p1[0] += (dx / dist) * force
                p1[1] += (dy / dist) * force
                p1[2] += (dz / dist) * force
                p2[0] -= (dx / dist) * force
                p2[1] -= (dy / dist) * force
                p2[2] -= (dz / dist) * force

    for u, v in edges:
        p1, p2 = nodes[u], nodes[v]
        dx = p2[0] - p1[0]
        dy = p2[1] - p1[1]
        dz = p2[2] - p1[2]
        dist = math.sqrt(dx * dx + dy * dy + dz * dz + 1)

        target_dist = 60
        force = (dist - target_dist) * 0.05

        p1[0] += (dx / dist) * force
        p1[1] += (dy / dist) * force
        p1[2] += (dz / dist) * force
        p2[0] -= (dx / dist) * force
        p2[1] -= (dy / dist) * force
        p2[2] -= (dz / dist) * force

    cx = sum(p[0] for p in nodes.values()) / len(nodes)
    cy = sum(p[1] for p in nodes.values()) / len(nodes)
    cz = sum(p[2] for p in nodes.values()) / len(nodes)
    for p in nodes.values():
        p[0] -= cx * 0.05
        p[1] -= cy * 0.05
        p[2] -= cz * 0.05

    # ==========================================
    # РЕНДЕРИНГ
    # ==========================================
    for u, v in edges:
        p1 = nodes[u]
        p2 = nodes[v]
        sx1, sy1, z1 = project_3d_to_2d(p1[0], p1[1], p1[2], camera_angle_y, camera_angle_x)
        sx2, sy2, z2 = project_3d_to_2d(p2[0], p2[1], p2[2], camera_angle_y, camera_angle_x)
        pygame.draw.line(screen, EDGE_COLOR, (sx1, sy1), (sx2, sy2), 1)

    for p in nodes.values():
        sx, sy, z = project_3d_to_2d(p[0], p[1], p[2], camera_angle_y, camera_angle_x)
        radius = max(2, int(1800 / (z + 800)))
        pygame.draw.circle(screen, NODE_COLOR, (int(sx), int(sy)), radius)

    font = pygame.font.SysFont("Arial", 28)

    # Текст-подсказка выведен в левый верхний угол
    info_text = font.render(f"Такт времени (Пробел): {universe_age} | Узлов: {len(nodes)} | ESC для выхода", True,
                            (255, 255, 255))
    screen.blit(info_text, (30, 30))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
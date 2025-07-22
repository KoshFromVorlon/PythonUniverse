import pygame
import math
import random
import sys

WIDTH, HEIGHT = 1000, 800
CENTER = WIDTH // 2, HEIGHT // 2
FPS = 60

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

# Цвета
WHITE = (255, 255, 255)
BLUE = (100, 150, 255)
YELLOW = (255, 255, 100)
RED = (255, 100, 100)
GREEN = (100, 255, 100)
PURPLE = (200, 100, 255)
GRAY = (180, 180, 180)


# Класс Электрона
class Electron:
    def __init__(self, orbit_radius, speed, color=BLUE):
        self.orbit_radius = orbit_radius
        self.angle = random.uniform(0, 2 * math.pi)
        self.speed = speed
        self.color = color
        self.energy_level = orbit_radius
        self.spin = random.choice([-1, 1])  # Упрощённый спин

    def update(self, center, rotation):
        self.angle += self.speed
        x = center[0] + self.orbit_radius * math.cos(self.angle + rotation)
        y = center[1] + self.orbit_radius * math.sin(self.angle + rotation)
        return int(x), int(y)

    def absorb_photon(self):
        if self.orbit_radius < 200:
            self.orbit_radius += 30
            self.color = PURPLE

    def emit_photon(self):
        if self.orbit_radius > 100:
            self.orbit_radius -= 30
            self.color = BLUE


# Класс Фотона
class Photon:
    def __init__(self):
        self.x = random.randint(0, WIDTH)
        self.y = HEIGHT + random.randint(20, 100)
        self.speed = random.uniform(4, 8)
        self.color = YELLOW

    def update(self):
        self.y -= self.speed
        return self.x, self.y


# Свободный электрон
class FreeElectron:
    def __init__(self):
        self.x = random.randint(0, WIDTH)
        self.y = random.randint(0, HEIGHT)
        self.color = RED

    def move_toward(self, target):
        dx, dy = target[0] - self.x, target[1] - self.y
        dist = math.hypot(dx, dy)
        if dist > 1:
            self.x += dx / dist * 2
            self.y += dy / dist * 2


# Инициализация
electrons = [Electron(100, 0.02), Electron(130, -0.017)]
photons = []
free_electrons = [FreeElectron() for _ in range(3)]
rotation = 0  # Поворот решётки

# Главный цикл
while True:
    screen.fill((10, 10, 30))
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    # Поворот сцены
    rotation += 0.002

    # Ядро
    pygame.draw.circle(screen, WHITE, CENTER, 10)

    # Орбиты
    for r in [100, 130, 160, 190]:
        pygame.draw.circle(screen, GRAY, CENTER, r, 1)

    # Фотоны
    if random.random() < 0.03:
        photons.append(Photon())
    for photon in photons[:]:
        x, y = photon.update()
        pygame.draw.circle(screen, photon.color, (int(x), int(y)), 3)
        # Столкновение с электронами
        for e in electrons:
            ex, ey = e.update(CENTER, rotation)
            if abs(x - ex) < 10 and abs(y - ey) < 10:
                e.absorb_photon()
                photons.remove(photon)
                break
        if y < 0:
            photons.remove(photon)

    # Электроны
    for e in electrons:
        pos = e.update(CENTER, rotation)
        pygame.draw.circle(screen, e.color, pos, 6)

    # Спонтанная эмиссия
    if random.random() < 0.005:
        random.choice(electrons).emit_photon()

    # Свободные электроны
    for fe in free_electrons:
        fe.move_toward(CENTER)
        pygame.draw.circle(screen, fe.color, (int(fe.x), int(fe.y)), 4)

    pygame.display.flip()
    clock.tick(FPS)

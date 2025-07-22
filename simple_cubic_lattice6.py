import pygame
import random
import math
import sys

# Настройки
WIDTH, HEIGHT = 900, 700
FPS = 60

GRID_SIZE = 10
ATOM_SPACING = 60
ATOM_RADIUS = 8
ELECTRON_RADIUS = 3
ORBIT_RADII = [20, 30]
PHOTON_RADIUS = 4
PHOTON_SPEED = 4
PHOTON_SPAWN_RATE = 5  # фотоны в секунду
INTERACTION_RADIUS = 15

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Кристаллическая решетка с электронами и фотонами")
clock = pygame.time.Clock()

# Проекция 3D (упрощённая, сверху вниз)
def project(pos3d):
    # Игнорируем z, просто сдвигаем x,y центрируем на экран
    x = pos3d[0] + WIDTH // 2 - (GRID_SIZE * ATOM_SPACING) // 2
    y = pos3d[1] + HEIGHT // 2 - (GRID_SIZE * ATOM_SPACING) // 2
    return int(x), int(y)

class Electron:
    def __init__(self, atom_pos, orbit_radius):
        self.atom_pos = atom_pos
        self.orbit_radius = orbit_radius
        self.angle = random.uniform(0, 2*math.pi)
        self.speed = random.uniform(0.02, 0.05)
        self.color = (100, 100, 255)

    def update(self):
        self.angle += self.speed
        if self.angle > 2*math.pi:
            self.angle -= 2*math.pi

    def get_pos(self):
        x = self.atom_pos[0] + self.orbit_radius * math.cos(self.angle)
        y = self.atom_pos[1] + self.orbit_radius * math.sin(self.angle)
        return (x, y)

    def excite(self):
        # Переход на "высшую" орбиту или смена цвета
        self.orbit_radius += 10
        self.color = (255, 150, 0)
        if self.orbit_radius > 40:
            self.orbit_radius = ORBIT_RADII[0]
            self.color = (100, 100, 255)

class Atom:
    def __init__(self, x, y):
        self.pos = (x, y)
        self.electrons = [Electron(self.pos, r) for r in ORBIT_RADII]

    def update(self):
        for e in self.electrons:
            e.update()

    def draw(self, surf):
        px, py = project(self.pos + (0,))
        pygame.draw.circle(surf, (255, 255, 0), (px, py), ATOM_RADIUS)  # ядро
        for e in self.electrons:
            ex, ey = e.get_pos()
            ex, ey = project((ex, ey, 0))
            pygame.draw.circle(surf, e.color, (ex, ey), ELECTRON_RADIUS)
            pygame.draw.circle(surf, (200,200,200), (px, py), int(e.orbit_radius), 1)  # орбита

class Photon:
    def __init__(self):
        # Случайная точка на периметре (4 стороны окна)
        side = random.choice(['top', 'bottom', 'left', 'right'])
        if side == 'top':
            self.pos = [random.uniform(0, WIDTH), -10]
            self.dir = [random.uniform(-0.5, 0.5), 1]
        elif side == 'bottom':
            self.pos = [random.uniform(0, WIDTH), HEIGHT + 10]
            self.dir = [random.uniform(-0.5, 0.5), -1]
        elif side == 'left':
            self.pos = [-10, random.uniform(0, HEIGHT)]
            self.dir = [1, random.uniform(-0.5, 0.5)]
        else:
            self.pos = [WIDTH + 10, random.uniform(0, HEIGHT)]
            self.dir = [-1, random.uniform(-0.5, 0.5)]

        length = math.hypot(*self.dir)
        self.dir = [self.dir[0]/length, self.dir[1]/length]
        self.color = (255, 255, 100)

    def update(self):
        self.pos[0] += self.dir[0] * PHOTON_SPEED
        self.pos[1] += self.dir[1] * PHOTON_SPEED

    def draw(self, surf):
        pygame.draw.circle(surf, self.color, (int(self.pos[0]), int(self.pos[1])), PHOTON_RADIUS)

    def is_offscreen(self):
        return (self.pos[0] < -20 or self.pos[0] > WIDTH + 20 or
                self.pos[1] < -20 or self.pos[1] > HEIGHT + 20)

# Создаем решетку атомов
atoms = []
for i in range(GRID_SIZE):
    for j in range(GRID_SIZE):
        x = i * ATOM_SPACING
        y = j * ATOM_SPACING
        atoms.append(Atom(x, y))

photons = []

spawn_timer = 0

running = True
while running:
    dt = clock.tick(FPS) / 1000  # секунды на кадр
    spawn_timer += dt

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Спавним фотоны с заданной частотой
    while spawn_timer > 1/PHOTON_SPAWN_RATE:
        photons.append(Photon())
        spawn_timer -= 1/PHOTON_SPAWN_RATE

    # Обновление
    for atom in atoms:
        atom.update()

    for photon in photons[:]:
        photon.update()
        if photon.is_offscreen():
            photons.remove(photon)
        else:
            # Проверяем столкновения с электронами
            for atom in atoms:
                px, py = project(atom.pos + (0,))
                for electron in atom.electrons:
                    ex, ey = electron.get_pos()
                    ex, ey = project((ex, ey, 0))
                    dist = math.hypot(photon.pos[0]-ex, photon.pos[1]-ey)
                    if dist < INTERACTION_RADIUS:
                        electron.excite()
                        if photon in photons:
                            photons.remove(photon)
                        break

    # Рендеринг
    screen.fill((10, 10, 30))
    for atom in atoms:
        atom.draw(screen)
    for photon in photons:
        photon.draw(screen)

    pygame.display.flip()

pygame.quit()
sys.exit()

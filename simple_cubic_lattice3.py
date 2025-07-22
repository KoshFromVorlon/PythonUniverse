import pygame
import math
import random

WIDTH, HEIGHT = 1000, 800
BLACK = (0, 0, 0)
BLUE = (100, 100, 255)
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)
FPS = 60

GRID_SIZE = 10
SPACING = 100  # Расстояние между атомами в решётке
CAMERA_Z = -1500  # Положение наблюдателя по z

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()


def project(x, y, z):
    """Проекция 3D → 2D"""
    factor = 800 / (z - CAMERA_Z + 800)
    px = int(WIDTH // 2 + x * factor)
    py = int(HEIGHT // 2 + y * factor)
    return px, py


class Electron:
    def __init__(self, orbit_radius, speed, color, orbit_plane='xy'):
        self.orbit_radius = orbit_radius
        self.angle = random.uniform(0, 2 * math.pi)
        self.speed = speed
        self.color = color
        self.spin = random.choice([-1, 1])
        self.plane = orbit_plane

    def update(self):
        self.angle += self.speed
        if self.angle > 2 * math.pi:
            self.angle -= 2 * math.pi

    def get_relative_pos(self):
        r = self.orbit_radius
        a = self.angle
        if self.plane == 'xy':
            return r * math.cos(a), r * math.sin(a), 0
        elif self.plane == 'yz':
            return 0, r * math.cos(a), r * math.sin(a)
        else:  # xz
            return r * math.cos(a), 0, r * math.sin(a)


class Atom:
    def __init__(self, base_pos):
        self.base_pos = base_pos
        self.electrons = []
        orbit_planes = ['xy', 'yz', 'xz']
        for orbit_radius in [20, 35, 50]:
            for _ in range(random.randint(1, 3)):
                plane = random.choice(orbit_planes)
                self.electrons.append(Electron(
                    orbit_radius=orbit_radius,
                    speed=random.uniform(0.01, 0.03),
                    color=BLUE,
                    orbit_plane=plane
                ))

    def update(self):
        for e in self.electrons:
            e.update()

    def draw(self, surface):
        x0, y0, z0 = self.base_pos
        # Ядро атома
        px, py = project(x0, y0, z0)
        pygame.draw.circle(surface, YELLOW, (px, py), 4)

        # Электроны
        for e in self.electrons:
            dx, dy, dz = e.get_relative_pos()
            ex, ey = project(x0 + dx, y0 + dy, z0 + dz)
            pygame.draw.circle(surface, e.color, (ex, ey), 2)
            spin_offset = 4 * e.spin
            pygame.draw.line(surface, WHITE, (ex, ey), (ex, ey + spin_offset), 1)


# Создание решётки атомов
atoms = []
for i in range(GRID_SIZE):
    for j in range(GRID_SIZE):
        for k in range(GRID_SIZE):
            x = (i - GRID_SIZE // 2) * SPACING
            y = (j - GRID_SIZE // 2) * SPACING
            z = (k - GRID_SIZE // 2) * SPACING
            atoms.append(Atom((x, y, z)))

# Главный цикл
running = True
while running:
    screen.fill(BLACK)

    for atom in atoms:
        atom.update()
        atom.draw(screen)

    pygame.display.flip()
    clock.tick(FPS)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

pygame.quit()

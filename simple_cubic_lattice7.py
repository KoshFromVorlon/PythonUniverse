import pygame
import random
import math
import sys

# Настройки экрана
WIDTH, HEIGHT = 900, 700
FPS = 60

GRID_SIZE = 10
ATOM_SPACING = 60
ATOM_RADIUS = 8
ELECTRON_RADIUS = 3
ORBIT_RADII = [20, 30]
PHOTON_RADIUS = 4
PHOTON_SPEED = 4
PHOTON_SPAWN_RATE = 5  # фотоны в секунду, внешние
INTERACTION_RADIUS = 15

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Кристаллическая решетка с электронами и фотонами")
clock = pygame.time.Clock()

def project(pos3d):
    # Простая 2D проекция (игнорируем z, центрируем решетку)
    x = pos3d[0] + WIDTH // 2 - (GRID_SIZE * ATOM_SPACING) // 2
    y = pos3d[1] + HEIGHT // 2 - (GRID_SIZE * ATOM_SPACING) // 2
    return int(x), int(y)

class Electron:
    def __init__(self, atom_pos, orbit_radius):
        self.atom_pos = atom_pos
        self.base_orbit = orbit_radius
        self.orbit_radius = orbit_radius
        self.angle = random.uniform(0, 2*math.pi)
        self.speed = random.uniform(0.02, 0.05)
        self.color = (100, 100, 255)
        self.excited = False
        self.excited_time = 0
        self.excited_duration = random.uniform(0.1, 100)  # Рандомное время возбуждения

    def update(self, dt):
        self.angle += self.speed
        if self.angle > 2*math.pi:
            self.angle -= 2*math.pi
        if self.excited:
            self.excited_time += dt
            if self.excited_time >= self.excited_duration:
                self.relax()

    def get_pos(self):
        x = self.atom_pos[0] + self.orbit_radius * math.cos(self.angle)
        y = self.atom_pos[1] + self.orbit_radius * math.sin(self.angle)
        return (x, y)

    def excite(self):
        if not self.excited:
            self.orbit_radius += 10
            self.color = (255, 150, 0)
            self.excited = True
            self.excited_time = 0
            self.excited_duration = random.uniform(0.1, 100)  # Случайное время возбуждения при каждом возбуждении

    def relax(self):
        self.orbit_radius = self.base_orbit
        self.color = (100, 100, 255)
        self.excited = False
        self.excited_time = 0
        # Испускание фотона при возвращении
        spawn_photon_at(self.get_pos())

class Atom:
    def __init__(self, x, y):
        self.pos = (x, y)
        self.electrons = [Electron(self.pos, r) for r in ORBIT_RADII]

    def update(self, dt):
        for e in self.electrons:
            e.update(dt)

    def draw(self, surf):
        px, py = project(self.pos + (0,))
        pygame.draw.circle(surf, (255, 255, 0), (px, py), ATOM_RADIUS)  # ядро
        for e in self.electrons:
            ex, ey = e.get_pos()
            ex, ey = project((ex, ey, 0))
            pygame.draw.circle(surf, e.color, (ex, ey), ELECTRON_RADIUS)
            pygame.draw.circle(surf, (200,200,200), (px, py), int(e.orbit_radius), 1)  # орбита

photons = []

def spawn_photon_at(pos):
    x, y = pos
    angle = random.uniform(0, 2*math.pi)
    dx = math.cos(angle)
    dy = math.sin(angle)
    photon = {
        'pos': [x, y],
        'dir': [dx, dy]
    }
    photons.append(photon)

def spawn_external_photon():
    side = random.choice(['top', 'bottom', 'left', 'right'])
    if side == 'top':
        pos = [random.uniform(0, WIDTH), -10]
        dir = [random.uniform(-0.5, 0.5), 1]
    elif side == 'bottom':
        pos = [random.uniform(0, WIDTH), HEIGHT + 10]
        dir = [random.uniform(-0.5, 0.5), -1]
    elif side == 'left':
        pos = [-10, random.uniform(0, HEIGHT)]
        dir = [1, random.uniform(-0.5, 0.5)]
    else:
        pos = [WIDTH + 10, random.uniform(0, HEIGHT)]
        dir = [-1, random.uniform(-0.5, 0.5)]

    length = math.hypot(*dir)
    dir = [dir[0]/length, dir[1]/length]
    photon = {
        'pos': pos,
        'dir': dir
    }
    photons.append(photon)

def update_photons(dt):
    to_remove = []
    for i, p in enumerate(photons):
        p['pos'][0] += p['dir'][0] * PHOTON_SPEED
        p['pos'][1] += p['dir'][1] * PHOTON_SPEED
        x, y = p['pos']
        if x < -20 or x > WIDTH + 20 or y < -20 or y > HEIGHT + 20:
            to_remove.append(i)
    for i in reversed(to_remove):
        photons.pop(i)

def draw_photons(surf):
    for p in photons:
        pygame.draw.circle(surf, (255,255,100), (int(p['pos'][0]), int(p['pos'][1])), PHOTON_RADIUS)

def main():
    atoms = []
    for i in range(GRID_SIZE):
        for j in range(GRID_SIZE):
            x = i * ATOM_SPACING
            y = j * ATOM_SPACING
            atoms.append(Atom(x, y))

    spawn_timer = 0

    running = True
    while running:
        dt = clock.tick(FPS) / 1000
        spawn_timer += dt

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Спавн внешних фотонов с заданной частотой
        while spawn_timer > 1/PHOTON_SPAWN_RATE:
            spawn_external_photon()
            spawn_timer -= 1/PHOTON_SPAWN_RATE

        # Обновление атомов и электронов
        for atom in atoms:
            atom.update(dt)

        # Обновление фотонов
        update_photons(dt)

        # Проверка взаимодействия фотонов с электронами
        for photon in photons[:]:
            px, py = photon['pos']
            interacted = False
            for atom in atoms:
                ax, ay = project(atom.pos + (0,))
                for electron in atom.electrons:
                    ex, ey = electron.get_pos()
                    ex, ey = project((ex, ey, 0))
                    dist = math.hypot(px - ex, py - ey)
                    if dist < INTERACTION_RADIUS:
                        electron.excite()
                        if photon in photons:
                            photons.remove(photon)
                        interacted = True
                        break
                if interacted:
                    break

        # Отрисовка
        screen.fill((10, 10, 30))
        for atom in atoms:
            atom.draw(screen)
        draw_photons(screen)

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()

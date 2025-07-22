import pygame
import math
import random

WIDTH, HEIGHT = 800, 600
CENTER = (WIDTH // 2, HEIGHT // 2)
BLACK = (0, 0, 0)
BLUE = (100, 100, 255)
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)
FPS = 60

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

class Electron:
    def __init__(self, orbit_radius, speed, color):
        self.orbit_radius = orbit_radius
        self.angle = random.uniform(0, 2 * math.pi)
        self.speed = speed
        self.color = color
        self.spin = random.choice([-1, 1])  # имитация спина

    def update(self):
        self.angle += self.speed
        if self.angle > 2 * math.pi:
            self.angle -= 2 * math.pi

    def get_pos(self):
        x = CENTER[0] + math.cos(self.angle) * self.orbit_radius
        y = CENTER[1] + math.sin(self.angle) * self.orbit_radius
        return int(x), int(y)

    def draw(self):
        pos = self.get_pos()
        pygame.draw.circle(screen, self.color, pos, 5)
        # отрисовка спина
        spin_offset = 8 * self.spin
        pygame.draw.line(screen, WHITE, pos, (pos[0], pos[1] + spin_offset), 2)

class Atom:
    def __init__(self):
        self.electrons = []
        for orbit_radius in [60, 100, 150]:  # три орбитальных уровня
            for _ in range(random.randint(1, 4)):
                self.electrons.append(Electron(
                    orbit_radius,
                    speed=random.uniform(0.01, 0.03),
                    color=BLUE
                ))

    def update(self):
        for e in self.electrons:
            e.update()

    def draw(self):
        pygame.draw.circle(screen, YELLOW, CENTER, 15)  # ядро
        for radius in [60, 100, 150]:
            pygame.draw.circle(screen, WHITE, CENTER, radius, 1)  # орбиты
        for e in self.electrons:
            e.draw()

    def interact(self):
        # простое взаимодействие: если электроны сблизились, меняют цвет
        for i, e1 in enumerate(self.electrons):
            for e2 in self.electrons[i+1:]:
                if e1.orbit_radius != e2.orbit_radius:  # взаимодействуют только разные орбиты
                    x1, y1 = e1.get_pos()
                    x2, y2 = e2.get_pos()
                    dist = math.hypot(x2 - x1, y2 - y1)
                    if dist < 15:
                        e1.color = random.choice([BLUE, WHITE])
                        e2.color = random.choice([BLUE, WHITE])
                        # можно также поменять спины
                        e1.spin *= -1
                        e2.spin *= -1

atom = Atom()

running = True
while running:
    screen.fill(BLACK)
    atom.update()
    atom.interact()
    atom.draw()
    pygame.display.flip()
    clock.tick(FPS)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

pygame.quit()

import pygame
import random
import math

# Параметры окна
WIDTH, HEIGHT = 800, 600
FPS = 60
NUM_PARTICLES = 50

# Инициализация Pygame
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Симуляция частиц")
clock = pygame.time.Clock()

class Particle:
    def __init__(self):
        self.radius = random.randint(3, 8)
        self.x = random.uniform(self.radius, WIDTH - self.radius)
        self.y = random.uniform(self.radius, HEIGHT - self.radius)
        self.vx = random.uniform(-2, 2)
        self.vy = random.uniform(-2, 2)
        self.color = (random.randint(100, 255), random.randint(100, 255), random.randint(100, 255))

    def move(self):
        self.x += self.vx
        self.y += self.vy

        # Отскок от стен
        if self.x <= self.radius or self.x >= WIDTH - self.radius:
            self.vx *= -1
        if self.y <= self.radius or self.y >= HEIGHT - self.radius:
            self.vy *= -1

    def draw(self, surface):
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.radius)

# Создание частиц
particles = [Particle() for _ in range(NUM_PARTICLES)]

# Главный цикл
running = True
while running:
    clock.tick(FPS)
    screen.fill((10, 10, 30))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    for p in particles:
        p.move()
        p.draw(screen)

    pygame.display.flip()

pygame.quit()

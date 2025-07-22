from vpython import *
import random
import math

scene = canvas(title='Кристаллическая решетка с электронами и фотонами',
               background=color.black, width=1000, height=700)
scene.camera.pos = vector(30, 30, 30)
scene.camera.axis = vector(-30, -30, -30)

# Функция создания атома с ядром и электронами
def create_atom(position):
    nucleus = sphere(pos=position, radius=0.3, color=color.red)
    electron_orbits = []
    electrons = []
    radii = [0.7, 1.0]  # две орбиты
    for r in radii:
        orbit_ring = ring(pos=position, axis=vector(0,1,0), radius=r, thickness=0.01, color=color.white)
        electron = sphere(pos=position + vector(r, 0, 0), radius=0.1, color=color.cyan, make_trail=False)
        electron_orbits.append(orbit_ring)
        electrons.append([electron, r, random.uniform(0, 2*math.pi)])  # угол сохраняем для обновления
    return electrons

grid_size = 10
spacing = 3
all_electrons = []

# Создаем кубическую решетку атомов
for x in range(grid_size):
    for y in range(grid_size):
        for z in range(grid_size):
            pos = vector(x * spacing, y * spacing, z * spacing)
            electrons = create_atom(pos)
            all_electrons.extend(electrons)

# Класс фотона
class Photon:
    def __init__(self):
        # Запускаем фотон с случайной точки на сфере радиуса 100
        theta = random.uniform(0, math.pi)
        phi = random.uniform(0, 2 * math.pi)
        r = 100
        self.pos = vector(r * math.sin(theta) * math.cos(phi),
                          r * math.sin(theta) * math.sin(phi),
                          r * math.cos(theta))
        # Направляем к центру (0,0,0)
        self.velocity = norm(-self.pos) * 1.5
        self.body = sphere(pos=self.pos, radius=0.15, color=color.yellow, make_trail=False)

    def move(self):
        self.pos += self.velocity
        self.body.pos = self.pos

photons = [Photon() for _ in range(80)]

# Основной цикл анимации
while True:
    rate(60)

    # Обновляем позиции электронов на орбитах
    for i, (e, r, angle) in enumerate(all_electrons):
        angle += 0.05
        all_electrons[i][2] = angle  # обновляем угол
        center = e.pos - vector(r, 0, 0)  # центр орбиты
        # Новая позиция электрона по кругу в плоскости XY
        e.pos = center + vector(r * math.cos(angle), 0, r * math.sin(angle))

    # Двигаем фотоны
    for photon in photons:
        photon.move()

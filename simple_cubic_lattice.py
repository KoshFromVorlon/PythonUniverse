import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

# Параметры
N = 10  # решётка 10x10x10
lattice_spacing = 1.0
interaction_distance = 0.5

# Классы
class Electron:
    def __init__(self, orbit_radius=0.2):
        angle = np.random.uniform(0, 2*np.pi)
        self.position = np.array([
            orbit_radius * np.cos(angle),
            orbit_radius * np.sin(angle),
            0
        ])

class Atom:
    def __init__(self, position, n_electrons=1):
        self.position = np.array(position)
        self.electrons = [Electron() for _ in range(n_electrons)]

    def get_electron_world_positions(self):
        return [self.position + e.position for e in self.electrons]

class Photon:
    def __init__(self, position, direction, speed=1.0):
        self.position = np.array(position, dtype=np.float64)
        self.direction = np.array(direction, dtype=np.float64)
        self.direction /= np.linalg.norm(self.direction)
        self.speed = speed

    def move(self, dt):
        self.position += self.direction * self.speed * dt

def spawn_random_photon(bounds):
    side = np.random.choice(['x', 'y', 'z'])
    axis = {'x': 0, 'y': 1, 'z': 2}[side]
    position = np.random.uniform(0, bounds, size=3)
    position[axis] = -2  # за пределами решётки
    direction = np.random.normal(0, 1, size=3)
    direction[axis] = 1  # направлен внутрь решётки
    return Photon(position, direction)

# Генерация решётки
x = np.arange(N) * lattice_spacing
y = np.arange(N) * lattice_spacing
z = np.arange(N) * lattice_spacing
xx, yy, zz = np.meshgrid(x, y, z, indexing='ij')
atoms = np.stack([xx, yy, zz], axis=-1).reshape(-1, 3)

# Создаём атомы
atom_objects = [Atom(pos) for pos in atoms]

# Фотоны
photons = [spawn_random_photon(bounds=N * lattice_spacing) for _ in range(5)]

# Обновление фотонов
for photon in photons:
    photon.move(dt=0.1)

# Визуализация
fig = plt.figure(figsize=(10, 10))
ax = fig.add_subplot(111, projection='3d')
ax.set_title('Кристаллическая решётка с электронами и фотонами')

# Атомы
atom_coords = np.array([atom.position for atom in atom_objects])
ax.scatter(atom_coords[:, 0], atom_coords[:, 1], atom_coords[:, 2], c='cyan', s=5, label='Атомы')

# Электроны
for atom in atom_objects:
    for ep in atom.get_electron_world_positions():
        ax.scatter(*ep, c='blue', s=2)

# Фотоны
for photon in photons:
    ax.scatter(*photon.position, c='yellow', s=30, marker='*', label='Фотон')

# Настройки
ax.set_xlim(0, N)
ax.set_ylim(0, N)
ax.set_zlim(0, N)
ax.set_xlabel("X")
ax.set_ylabel("Y")
ax.set_zlabel("Z")
plt.legend(loc='upper left')
plt.show()

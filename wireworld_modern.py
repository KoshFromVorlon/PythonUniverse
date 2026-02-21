import sys
import numpy as np
from scipy.signal import convolve2d
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QPushButton, QComboBox, QLabel)
from PyQt6.QtGui import QPainter, QColor, QImage, QPixmap
from PyQt6.QtCore import Qt, QTimer

# ==========================================
# 1. КОНСТАНТЫ И СОСТОЯНИЯ (Из старого config.py)
# ==========================================
EMPTY = 0
WIRE = 1
HEAD = 2
TAIL = 3

COLORS = {
    EMPTY: (34, 34, 34),  # Темный фон (#222)
    WIRE: (170, 85, 0),  # Медный провод (#A50)
    HEAD: (255, 255, 255),  # Белая голова электрона (#FFF)
    TAIL: (0, 0, 170)  # Синий хвост электрона (#00A)
}

CELL_SIZE = 15
COLS, ROWS = 60, 40


# ==========================================
# 2. МАТЕМАТИЧЕСКИЙ ДВИЖОК (Из старого monde.py)
# ==========================================
class WireworldEngine:
    def __init__(self, cols, rows):
        self.cols = cols
        self.rows = rows
        self.grid = np.zeros((rows, cols), dtype=int)
        # Ядро Мура для подсчета соседей
        self.kernel = np.array([[1, 1, 1],
                                [1, 0, 1],
                                [1, 1, 1]])

    def step(self):
        # 1. Находим все головы электронов
        heads = (self.grid == HEAD).astype(int)

        # 2. Считаем количество голов вокруг каждой клетки
        head_counts = convolve2d(heads, self.kernel, mode='same', boundary='fill', fillvalue=0)

        # 3. Правила Wireworld:
        new_grid = self.grid.copy()

        # Голова -> Хвост
        new_grid[self.grid == HEAD] = TAIL
        # Хвост -> Провод
        new_grid[self.grid == TAIL] = WIRE
        # Провод -> Голова (если рядом 1 или 2 головы)
        wire_becomes_head = (self.grid == WIRE) & ((head_counts == 1) | (head_counts == 2))
        new_grid[wire_becomes_head] = HEAD

        self.grid = new_grid


# ==========================================
# 3. ГРАФИЧЕСКИЙ КАНВАС (Из старого ui_cell_array.py)
# ==========================================
class GridCanvas(QWidget):
    def __init__(self, engine):
        super().__init__()
        self.engine = engine
        self.setFixedSize(engine.cols * CELL_SIZE, engine.rows * CELL_SIZE)
        self.current_tool = WIRE
        self.is_drawing = False

    def paintEvent(self, event):
        painter = QPainter(self)
        # Создаем изображение из numpy массива
        h, w = self.engine.grid.shape
        img = QImage(w, h, QImage.Format.Format_RGB32)

        for y in range(h):
            for x in range(w):
                state = self.engine.grid[y, x]
                r, g, b = COLORS[state]
                img.setPixelColor(x, y, QColor(r, g, b))

        # Масштабируем до размеров окна без сглаживания (чтобы пиксели были четкими)
        pixmap = QPixmap.fromImage(img).scaled(
            self.width(), self.height(),
            Qt.AspectRatioMode.IgnoreAspectRatio,
            Qt.TransformationMode.FastTransformation
        )
        painter.drawPixmap(0, 0, pixmap)

        # Рисуем сетку
        painter.setPen(QColor(60, 60, 60))
        for x in range(0, self.width(), CELL_SIZE):
            painter.drawLine(x, 0, x, self.height())
        for y in range(0, self.height(), CELL_SIZE):
            painter.drawLine(0, y, self.width(), y)

    def mousePressEvent(self, event):
        self.is_drawing = True
        self.apply_tool(event.position().x(), event.position().y())

    def mouseMoveEvent(self, event):
        if self.is_drawing:
            self.apply_tool(event.position().x(), event.position().y())

    def mouseReleaseEvent(self, event):
        self.is_drawing = False

    def apply_tool(self, x, y):
        col = int(x // CELL_SIZE)
        row = int(y // CELL_SIZE)
        if 0 <= col < self.engine.cols and 0 <= row < self.engine.rows:
            self.engine.grid[row, col] = self.current_tool
            self.update()


# ==========================================
# 4. ГЛАВНОЕ ОКНО И ИНТЕРФЕЙС (Из старого ui_main_window.py)
# ==========================================
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Wireworld Simulator (PyQt6)")

        self.engine = WireworldEngine(COLS, ROWS)
        self.canvas = GridCanvas(self.engine)

        self.timer = QTimer()
        self.timer.timeout.connect(self.next_step)

        self.init_ui()

    def init_ui(self):
        main_widget = QWidget()
        layout = QVBoxLayout()

        # Панель инструментов
        toolbar = QHBoxLayout()

        self.btn_play = QPushButton("Play")
        self.btn_play.clicked.connect(self.toggle_play)

        self.btn_step = QPushButton("Step")
        self.btn_step.clicked.connect(self.next_step)

        self.btn_clear = QPushButton("Clear")
        self.btn_clear.clicked.connect(self.clear_grid)

        self.tool_selector = QComboBox()
        self.tool_selector.addItems(["Draw Wire", "Draw Electron Head", "Draw Electron Tail", "Eraser"])
        self.tool_selector.currentIndexChanged.connect(self.change_tool)

        toolbar.addWidget(self.btn_play)
        toolbar.addWidget(self.btn_step)
        toolbar.addWidget(self.btn_clear)
        toolbar.addWidget(QLabel("Tool:"))
        toolbar.addWidget(self.tool_selector)
        toolbar.addStretch()

        layout.addLayout(toolbar)
        layout.addWidget(self.canvas)
        main_widget.setLayout(layout)
        self.setCentralWidget(main_widget)

    def toggle_play(self):
        if self.timer.isActive():
            self.timer.stop()
            self.btn_play.setText("Play")
        else:
            self.timer.start(100)  # 10 кадров в секунду (100 мс)
            self.btn_play.setText("Pause")

    def next_step(self):
        self.engine.step()
        self.canvas.update()

    def clear_grid(self):
        self.engine.grid.fill(EMPTY)
        self.canvas.update()

    def change_tool(self, index):
        tools = {0: WIRE, 1: HEAD, 2: TAIL, 3: EMPTY}
        self.canvas.current_tool = tools.get(index, WIRE)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

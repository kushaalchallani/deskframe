import sys

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QWidget
from PySide6.QtGui import QPainter

class DeskFrame(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("DeskFrame")

        # Window appearance
        self.setWindowFlags(
            Qt.FramelessWindowHint |
            Qt.WindowStaysOnTopHint
        )

        self.setAttribute(Qt.WA_TranslucentBackground)

        # Widget size
        self.resize(300, 200)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        painter.setBrush(Qt.black)
        painter.setPen(Qt.NoPen)

        painter.drawRoundedRect(self.rect(), 15, 15)


def main():
    app = QApplication(sys.argv)

    window = DeskFrame()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
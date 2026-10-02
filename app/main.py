import sys

from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QApplication, QLabel, QWidget


class DeskFrame(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("DeskFrame")

        self.setWindowFlags(
            Qt.FramelessWindowHint |
            Qt.WindowStaysOnTopHint
        )

        self.setAttribute(Qt.WA_TranslucentBackground)

        self.resize(300, 200)

        # Create an image label
        self.image_label = QLabel(self)

        # Load the image
        pixmap = QPixmap("assets/test.png")

        # Scale the image to fit the widget
        pixmap = pixmap.scaled(
            self.size(),
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )

        self.image_label.setPixmap(pixmap)

        # Center the image
        self.image_label.setAlignment(Qt.AlignCenter)

        # Make the label fill the widget
        self.image_label.resize(self.size())


def main():
    app = QApplication(sys.argv)

    window = DeskFrame()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
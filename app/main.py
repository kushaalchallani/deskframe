import sys
from pathlib import Path

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QPixmap, QImageReader
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

        self.resize(350, 250)

        self.image_label = QLabel(self)
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.resize(self.size())

        self.photo_folder = Path("assets/photos")

        self.photos = [
            path for path in self.photo_folder.iterdir()
            if path.suffix.lower() in [".jpg", ".jpeg", ".png", ".webp"]
        ]

        self.current_index = 0

        self.show_photo()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.next_photo)
        self.timer.start(5000)

    def show_photo(self):
        if not self.photos:
            return

        photo_path = self.photos[self.current_index]

        reader = QImageReader(str(photo_path))
        reader.setAutoTransform(True)

        image = reader.read()

        if image.isNull():
            return

        pixmap = QPixmap.fromImage(image)

        pixmap = pixmap.scaled(
            self.size(),
            Qt.KeepAspectRatioByExpanding,
            Qt.SmoothTransformation
        )

        self.image_label.setPixmap(pixmap)

    def next_photo(self):
        if not self.photos:
            return

        self.current_index += 1

        if self.current_index >= len(self.photos):
            self.current_index = 0

        self.show_photo()


def main():
    app = QApplication(sys.argv)

    window = DeskFrame()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
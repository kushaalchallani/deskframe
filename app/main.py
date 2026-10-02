import sys
from pathlib import Path
from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import QApplication, QLabel, QWidget
from image_utils import load_smart_crop


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

        pixmap = load_smart_crop(
            photo_path,
            (self.width(), self.height())
        )

        self.image_label.setPixmap(pixmap)

    def next_photo(self):
        if not self.photos:
            return

        self.current_index += 1

        if self.current_index >= len(self.photos):
            self.current_index = 0

        self.show_photo()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()


    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.LeftButton:
            self.move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()


    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            event.accept()


def main():
    app = QApplication(sys.argv)

    window = DeskFrame()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
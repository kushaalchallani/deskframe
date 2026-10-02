import cv2
import numpy as np
from pathlib import Path
from PySide6.QtGui import QImage, QImageReader, QPixmap
from ultralytics import YOLO


MODEL_PATH = (
    Path(__file__).resolve().parent.parent
    / "assets"
    / "models"
    / "face_detection_yunet_2026may.onnx"
)

FACE_DETECTOR = cv2.FaceDetectorYN.create(
    str(MODEL_PATH),
    "",
    (320, 320),
    0.7,
    0.3,
    5000
)

PERSON_DETECTOR = YOLO("yolo11n.pt")

PIXMAP_CACHE = {}


def qimage_to_cv(image):
    image = image.convertToFormat(QImage.Format_RGB888)

    width = image.width()
    height = image.height()
    bytes_per_line = image.bytesPerLine()

    array = np.frombuffer(
        image.constBits(),
        dtype=np.uint8
    ).reshape(height, bytes_per_line)

    array = array[:, :width * 3]
    array = array.reshape(height, width, 3)

    return cv2.cvtColor(
        array,
        cv2.COLOR_RGB2BGR
    ).copy()


def cv_to_pixmap(image):
    rgb = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2RGB
    )

    height, width = rgb.shape[:2]

    qimage = QImage(
        rgb.data,
        width,
        height,
        width * 3,
        QImage.Format_RGB888
    ).copy()

    return QPixmap.fromImage(qimage)


def center_crop(image, target_ratio):
    height, width = image.shape[:2]
    image_ratio = width / height

    if image_ratio > target_ratio:
        crop_height = height
        crop_width = int(height * target_ratio)
    else:
        crop_width = width
        crop_height = int(width / target_ratio)

    left = (width - crop_width) // 2
    top = (height - crop_height) // 2

    return image[
        top:top + crop_height,
        left:left + crop_width
    ]


def build_subject_regions(faces, people):
    regions = []

    for face in faces:
        fx, fy, fw, fh = map(int, face[:4])

        left = fx - int(fw * 0.8)
        right = fx + fw + int(fw * 0.8)
        top = fy - int(fh * 0.5)
        bottom = fy + int(fh * 2.8)

        face_center_x = fx + fw / 2
        face_center_y = fy + fh / 2

        for person in people:
            px, py, pw, ph = map(int, person)

            if (
                px <= face_center_x <= px + pw
                and py <= face_center_y <= py + ph
            ):
                left = max(left, px)
                right = min(right, px + pw)
                top = max(top, py)
                bottom = min(
                    bottom,
                    fy + int(fh * 3.0)
                )
                break

        regions.append((left, top, right, bottom))

    return regions


def smart_crop(image, faces, people, target_size):
    target_width, target_height = target_size
    target_ratio = target_width / target_height

    if faces is None or len(faces) == 0:
        cropped = center_crop(
            image,
            target_ratio
        )

        return cv2.resize(
            cropped,
            target_size,
            interpolation=cv2.INTER_AREA
        )

    regions = build_subject_regions(
        faces,
        people
    )

    left = min(region[0] for region in regions)
    top = min(region[1] for region in regions)
    right = max(region[2] for region in regions)
    bottom = max(region[3] for region in regions)

    subject_width = right - left
    subject_height = bottom - top

    center_x = (left + right) / 2
    center_y = (top + bottom) / 2

    padding_x = subject_width * 0.08
    padding_y = subject_height * 0.08

    crop_width = subject_width + padding_x * 2
    crop_height = subject_height + padding_y * 2

    if crop_width / crop_height > target_ratio:
        crop_height = crop_width / target_ratio
    else:
        crop_width = crop_height * target_ratio

    image_height, image_width = image.shape[:2]

    crop_width = min(crop_width, image_width)
    crop_height = min(crop_height, image_height)

    if crop_width / crop_height > target_ratio:
        crop_height = crop_width / target_ratio
    else:
        crop_width = crop_height * target_ratio

    crop_width = int(crop_width)
    crop_height = int(crop_height)

    crop_left = int(center_x - crop_width / 2)
    crop_top = int(center_y - crop_height / 2)

    crop_left = max(
        0,
        min(crop_left, image_width - crop_width)
    )

    crop_top = max(
        0,
        min(crop_top, image_height - crop_height)
    )

    cropped = image[
        crop_top:crop_top + crop_height,
        crop_left:crop_left + crop_width
    ]

    return cv2.resize(
        cropped,
        target_size,
        interpolation=cv2.INTER_AREA
    )


def detect_faces(image):
    height, width = image.shape[:2]

    FACE_DETECTOR.setInputSize(
        (width, height)
    )

    _, faces = FACE_DETECTOR.detect(image)

    return faces


def detect_people(image):
    results = PERSON_DETECTOR(
        image,
        classes=[0],
        imgsz=640,
        verbose=False
    )

    return [
        box.astype(int).tolist()
        for box in results[0].boxes.xyxy.cpu().numpy()
    ]


def load_smart_crop(image_path, target_size):
    cache_key = (
        str(image_path),
        target_size
    )

    if cache_key in PIXMAP_CACHE:
        return PIXMAP_CACHE[cache_key]

    reader = QImageReader(str(image_path))
    reader.setAutoTransform(True)

    image = reader.read()

    if image.isNull():
        return QPixmap()

    cv_image = qimage_to_cv(image)

    faces = detect_faces(cv_image)
    people = detect_people(cv_image)

    result = smart_crop(
        cv_image,
        faces,
        people,
        target_size
    )

    pixmap = cv_to_pixmap(result)

    PIXMAP_CACHE[cache_key] = pixmap

    return pixmap
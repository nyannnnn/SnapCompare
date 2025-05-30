from utils.encode import encode_pil
import cv2
import numpy as np
from PIL import Image
import io
import base64
import random

# Function to generate a random color for each class ID
def get_color_for_class(cls_id):
    random.seed(cls_id)
    return tuple(int(x) for x in np.random.choice(range(100, 256), size=3))  # brighter colors

# Function to render YOLO bounding boxes on an image
def render_yolo_bbox(image: np.ndarray, result) -> str:
    overlay = image.copy()
    for box in result.boxes:
        x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
        cls = int(box.cls[0])
        conf = float(box.conf[0])

        label = f"{result.names[cls]} {conf:.2f}"
        color = get_color_for_class(cls)

        # Draw a thin rectangle
        cv2.rectangle(overlay, (x1, y1), (x2, y2), color, 2)
        font_scale = 0.4
        thickness = 1
        (label_width, label_height), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, font_scale, thickness)

        cv2.rectangle(
            overlay,
            (x1, y1 - label_height - 6),
            (x1 + label_width + 6, y1),
            color,
            -1
        )

        cv2.putText(
            overlay,
            label,
            (x1 + 3, y1 - 3),
            cv2.FONT_HERSHEY_SIMPLEX,
            font_scale,
            (255, 255, 255),
            thickness,
            cv2.LINE_AA
        )


    # Convert to PIL and encode
    pil_img = Image.fromarray(cv2.cvtColor(overlay, cv2.COLOR_BGR2RGB))
    return encode_pil(pil_img)

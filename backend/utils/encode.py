import base64
import io
from PIL import Image

def encode_pil(pil_img: Image.Image):
    buffer = io.BytesIO()
    pil_img.save(buffer, format="PNG")
    return base64.b64encode(buffer.getvalue()).decode("utf-8")
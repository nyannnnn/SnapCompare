import numpy as np
import cv2
from PIL import Image
from utils.encode import encode_pil

class DiffGenerator:
    @staticmethod
    def overlay(original_img: Image.Image, diff_array: np.ndarray, threshold=0.75):
        mask = diff_array < threshold
        # convert original image to numpy array
        original_np = np.array(original_img.resize(diff_array.shape[::-1]))
        # Create an overlay where differences are highlighted
        overlay = original_np.copy()
        overlay[mask] = [255, 0, 0]  # Highlight differences in red
        blended = cv2.addWeighted(original_np, 0.8, overlay, 0.2, 0)
        return encode_pil(Image.fromarray(blended))
    
    @staticmethod
    def heatmap(diff_array: np.ndarray):
        scaled = (diff_array * 255).astype(np.uint8)
        color = cv2.applyColorMap(scaled, cv2.COLORMAP_JET)
        rgb = cv2.cvtColor(color, cv2.COLOR_BGR2RGB)
        return encode_pil(Image.fromarray(rgb))
    
    @staticmethod
    def grayscale(diff_array: np.ndarray):
        gray = (diff_array * 255).astype(np.uint8)
        return encode_pil(Image.fromarray(gray))
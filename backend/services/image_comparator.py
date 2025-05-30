from PIL import Image
import numpy as np
from skimage.metrics import structural_similarity as ssim
import torch
import io

class ImageComparator:
    def __init__(self, img1_bytes: bytes, img2_bytes: bytes):
        self.img1_rgb = Image.open(io.BytesIO(img1_bytes)).convert('RGB').resize((256, 256))
        self.img2_rgb = Image.open(io.BytesIO(img2_bytes)).convert('RGB').resize((256, 256))
    
    def compute_ssim(self) -> float:
        img1_gray = self.img1_rgb.convert('L')
        img2_gray = self.img2_rgb.convert('L')
        img1_array = np.array(img1_gray)
        img2_array = np.array(img2_gray)

        # Calculate SSIM
        score, diff = ssim(img1_array, img2_array, full=True)
        return float(score), diff

    def compute_CLIP_similarity(self, model, processor):
        inputs = processor(images=[self.img1_rgb, self.img2_rgb], return_tensors="pt", padding=True)

        with torch.no_grad():
            image_features = model.get_image_features(**inputs)

        # Normalize the features
        image_features = torch.nn.functional.normalize(image_features, dim=1)
        # Calculate cosine similarity
        cos_sim = torch.nn.functional.cosine_similarity(image_features[0:1], image_features[1:2]).item()
        return (cos_sim + 1)/2
    
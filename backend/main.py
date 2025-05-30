from fastapi import FastAPI, File, UploadFile
from PIL import Image
import base64
from skimage.metrics import structural_similarity as ssim
from transformers import CLIPProcessor, CLIPModel
import torch
import cv2
import numpy as np
import io

clip_model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
clip_processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")


app = FastAPI()
from fastapi.middleware.cors import CORSMiddleware

#allowing CORS for the React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # React frontend origin
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

#test endpoint to check if the server is running
@app.get("/ping")
def ping():
    return {"message": "pong"}

# Generate a grayscale diff image from the SSIM diff map
def generate_grayscale_diff(diff_array: np.ndarray):
    gray = (diff_array * 255).astype(np.uint8)
    return encode_pil(Image.fromarray(gray))

# Helper to convert SSIM diff map to colored image
def generate_colored_diff(diff_array):
    scaled = (diff_array * 255).astype(np.uint8)
    color = cv2.applyColorMap(scaled, cv2.COLORMAP_JET)
    rgb = cv2.cvtColor(color, cv2.COLOR_BGR2RGB)
    return encode_pil(Image.fromarray(rgb))

# Generate an overlayed diff image
def generate_overlayed_diff(original_img: Image.Image, diff_array: np.ndarray, threshold=0.75):
    diff_array = np.array(diff_array)
    mask = diff_array < threshold
    # convert original image to numpy array
    original_np = np.array(original_img.resize((diff_array.shape[1], diff_array.shape[0])))
    # Create an overlay where differences are highlighted
    overlay = original_np.copy()
    overlay[mask] = [255, 0, 0]  # Highlight differences in red
    blended = cv2.addWeighted(original_np, 0.8, overlay, 0.2, 0)
    return encode_pil(Image.fromarray(blended))

# Encode PIL image to base64
def encode_pil(pil_img: Image.Image):
    buffer = io.BytesIO()
    pil_img.save(buffer, format="PNG")
    return base64.b64encode(buffer.getvalue()).decode("utf-8")

# Determine the reason for the difference
def detect_difference_reason(score, cos_sim):
    if score > 0.9 and cos_sim > 0.9:
        return "Images are nearly identical"
    elif score < 0.6 and cos_sim > 0.9:
        return "Slight visual changes (e.g., lighting, compression)"
    elif score > 0.9 and cos_sim < 0.6:
        return "Semantically different (e.g., object changed)"
    elif score < 0.6 and cos_sim < 0.6:
        return "Major visual and semantic differences"
    else:
        return "Minor differences"

@app.post("/compare")
async def compare_images(
    file1: UploadFile = File(...), file2: UploadFile = File(...)
):
    try:
    # Read the file bytes
        img1_bytes = await file1.read()
        img2_bytes = await file2.read()
        # Convert bytes to PIL Image
        img1_rgb = Image.open(io.BytesIO(img1_bytes)).convert("RGB")
        img2_rgb = Image.open(io.BytesIO(img2_bytes)).convert("RGB")

        img1_gray = img1_rgb.convert("L").resize((256, 256))
        img2_gray = img2_rgb.convert("L").resize((256, 256))

        img1_array = np.array(img1_gray)
        img2_array = np.array(img2_gray)

        # Calculate SSIM
        score, diff = ssim(img1_array, img2_array, full=True)
            
        inputs = clip_processor(images=[img1_rgb, img2_rgb], return_tensors="pt", padding=True)

        with torch.no_grad():
            image_features = clip_model.get_image_features(**inputs)

        # Normalize the features
        image_features = torch.nn.functional.normalize(image_features, dim=-1)
        # Calculate cosine similarity
        cos_sim = torch.nn.functional.cosine_similarity(image_features[0:1], image_features[1:2]).item()

        ssim_score = float(score)
        cos_sim = (cos_sim + 1) / 2  # Normalize cosine similarity to [0, 1]

        hybrid_score = round(0.5 * ssim_score + 0.5 * cos_sim, 4)
        reason_label = detect_difference_reason(ssim_score, cos_sim)
        # Return the SSIM score
        return {"similarity": round(score, 4),
                "ai_similarity": round(cos_sim, 4),
                "hybrid_similarity": hybrid_score,
                "diff_overlay": generate_overlayed_diff(img1_rgb, diff),
                "diff_heatmap": generate_colored_diff(diff),
                "diff_grayscale": generate_grayscale_diff(diff),
                "difference_reason": reason_label
                }
    except Exception as e:
        return {"error": str(e)}
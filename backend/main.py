from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from services.image_comparator import ImageComparator
from services.diff_generator import DiffGenerator
from services.similarity_utils import compute_hybrid_score, detect_difference_reason
from utils.encode import encode_pil
from transformers import CLIPProcessor, CLIPModel
import io

clip_model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
clip_processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")


app = FastAPI()
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

@app.post("/compare")
async def compare_images(file1: UploadFile = File(...), file2: UploadFile = File(...)):
    try:
        # Read the file bytes
        img1_bytes = await file1.read()
        img2_bytes = await file2.read()
        # Convert bytes to PIL Image
        comparator = ImageComparator(img1_bytes, img2_bytes)
        ssim_score, diff = comparator.compute_ssim()
        clip_score = comparator.compute_CLIP_similarity(clip_model, clip_processor)
        hybrid_score = compute_hybrid_score(ssim_score, clip_score)
        reason = detect_difference_reason(ssim_score, clip_score)

        overlay = DiffGenerator.overlay(comparator.img1_rgb, diff)
        heatmap = DiffGenerator.heatmap(diff)
        grayscale = DiffGenerator.grayscale(diff)
        # Return the SSIM score
        return {
            "similarity": round(ssim_score, 4),
            "ai_similarity": round(clip_score, 4),
            "hybrid_similarity": round(hybrid_score, 4),
            "diff_overlay": overlay,
            "diff_heatmap": heatmap,
            "diff_grayscale": grayscale,
            "difference_reason": reason
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"error": str(e)}
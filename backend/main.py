from fastapi import FastAPI, File, UploadFile, Query
from fastapi.middleware.cors import CORSMiddleware
from services.image_comparator import ImageComparator
from services.diff_generator import DiffGenerator
from services.similarity_utils import compute_hybrid_score, compute_object_score, detect_difference_reason
from utils.yolo import render_yolo_bbox
from utils.encode import encode_pil
from transformers import CLIPProcessor, CLIPModel
from ultralytics import YOLO
from PIL import Image
import numpy as np
import io
import cv2

clip_model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32") # Load CLIP model
clip_processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
yolo_model = YOLO("yolov8n.pt")  # Load YOLOv8 model


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
async def compare_images(file1: UploadFile = File(...), file2: UploadFile = File(...), threshold: float = Query(0.85)):
    try:
        # Read the file bytes
        img1_bytes = await file1.read()
        img2_bytes = await file2.read()
        # Convert bytes to PIL Image
        comparator = ImageComparator(img1_bytes, img2_bytes)
        ssim_score, diff = comparator.compute_ssim()
        clip_score = comparator.compute_CLIP_similarity(clip_model, clip_processor)
        reason = detect_difference_reason(ssim_score, clip_score, threshold=threshold)
        #provide YOLO results
        yolo_results1 = yolo_model(comparator.img1_rgb)
        yolo_results2 = yolo_model(comparator.img2_rgb)
        #provide object outlings for the images
        img_np1 = np.array(comparator.img1_rgb.resize((256, 256)))[:, :, ::-1]  # Convert PIL → BGR
        img_np2 = np.array(comparator.img2_rgb.resize((256, 256)))[:, :, ::-1]

        bbox_img1 = render_yolo_bbox(img_np1, yolo_results1[0])
        bbox_img2 = render_yolo_bbox(img_np2, yolo_results2[0])

        # computer object score
        object_score = compute_object_score(yolo_results1[0], yolo_results2[0])

        # Compute hybrid score
        hybrid_score = compute_hybrid_score(ssim_score, clip_score, object_score)

        overlay = DiffGenerator.overlay(comparator.img1_rgb, diff, threshold=threshold)
        heatmap = DiffGenerator.heatmap(diff)
        grayscale = DiffGenerator.grayscale(diff)
        # Return the SSIM score
        return {
            "similarity": round(ssim_score, 4),
            "ai_similarity": round(clip_score, 4),
            "object_similarity": round(object_score, 4),
            "hybrid_similarity": round(hybrid_score, 4),
            "diff_overlay": overlay,
            "diff_heatmap": heatmap,
            "diff_grayscale": grayscale,
            "difference_reason": reason,
            "bbox_img1": bbox_img1,
            "bbox_img2": bbox_img2,
            "reasoning_report": {
                "ssim_score": round(ssim_score, 4),
                "clip_score": round(clip_score, 4),
                "objects_img1": len(yolo_results1[0].boxes),
                "objects_img2": len(yolo_results2[0].boxes),
                "object_difference": abs(len(yolo_results1[0].boxes) - len(yolo_results2[0].boxes))
            }
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"error": str(e)}
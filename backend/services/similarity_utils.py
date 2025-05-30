def detect_difference_reason(score, cos_sim, threshold: float =0.8):
    if score > threshold and cos_sim > 0.9:
        return "Images are nearly identical"
    elif score < threshold and cos_sim > 0.9:
        return "Minor visual differences (e.g., lighting, crop)"
    elif score > threshold and cos_sim < 0.6:
        return "Object content changed (semantically different)"
    elif score < threshold and cos_sim < 0.6:
        return "Major visual and content differences"
    else:
        return "Some differences detected"
    
def compute_hybrid_score(ssim_score: float, clip_score: float, weight_ssim: float = 0.5):
    weight_clip = 1.0 - weight_ssim
    return weight_ssim * ssim_score + weight_clip * clip_score
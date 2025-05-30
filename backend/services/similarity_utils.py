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
    
def compute_hybrid_score(ssim_score: float, clip_score: float, weight_ssim: float = 0.5):
    weight_clip = 1.0 - weight_ssim
    return weight_ssim * ssim_score + weight_clip * clip_score
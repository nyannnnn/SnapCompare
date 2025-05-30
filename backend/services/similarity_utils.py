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
    
def compute_hybrid_score(ssim_score, clip_score, object_score, weights=(0.3, 0.5, 0.2)):
    ssim_w, clip_w, object_w = weights
    return (
        ssim_w * ssim_score +
        clip_w * clip_score +
        object_w * object_score
    )

def compute_object_score(yolo1, yolo2):
    from collections import Counter

    # Get class IDs from each image
    classes1 = [int(c) for c in yolo1.boxes.cls.cpu().numpy()]
    classes2 = [int(c) for c in yolo2.boxes.cls.cpu().numpy()]

    counter1 = Counter(classes1)
    counter2 = Counter(classes2)

    # All unique classes across both images
    all_classes = set(counter1.keys()).union(set(counter2.keys()))

    # Total similarity over shared classes
    total_score = 0
    for cls in all_classes:
        count1 = counter1.get(cls, 0)
        count2 = counter2.get(cls, 0)
        max_count = max(count1, count2)
        if max_count > 0:
            total_score += 1 - abs(count1 - count2) / max_count

    return total_score / len(all_classes) if all_classes else 1.0

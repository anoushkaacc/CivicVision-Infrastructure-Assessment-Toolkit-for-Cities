"""Civic intelligence engine — computes all metrics, scores, and recommendations."""

import math


def _bbox_area(bbox):
    """Compute pixel area of a bounding box (x1, y1, x2, y2)."""
    x1, y1, x2, y2 = bbox
    return max(0, x2 - x1) * max(0, y2 - y1)


def _image_area(img):
    """Return total pixel area of a (H, W, C) or (H, W) image."""
    h, w = img.shape[:2]
    return h * w


def compute_damage_metrics(road_detections, image):
    """Compute road-damage metrics from a list of road detections.

    Returns dict with:
        longitudinal_crack_count, transverse_crack_count,
        alligator_crack_count, pothole_count,
        total_damage_count, total_damage_bbox_area,
        average_damage_bbox_area, largest_damage_bbox_area,
        damage_area_percentage
    """
    counts = {
        "longitudinal_crack": 0,
        "transverse_crack": 0,
        "alligator_crack": 0,
        "pothole": 0,
    }

    areas = []
    for det in road_detections:
        key = det["class_key"]
        if key in counts:
            counts[key] += 1
        areas.append(_bbox_area(det["bbox"]))

    total_damage_count = sum(counts.values())
    total_damage_bbox_area = sum(areas)
    average_damage_bbox_area = (total_damage_bbox_area / total_damage_count) if total_damage_count > 0 else 0.0
    largest_damage_bbox_area = max(areas) if areas else 0.0
    img_area = _image_area(image)
    damage_area_percentage = (total_damage_bbox_area / img_area * 100) if img_area > 0 else 0.0

    return {
        "longitudinal_crack_count": counts["longitudinal_crack"],
        "transverse_crack_count": counts["transverse_crack"],
        "alligator_crack_count": counts["alligator_crack"],
        "pothole_count": counts["pothole"],
        "total_damage_count": total_damage_count,
        "total_damage_bbox_area": total_damage_bbox_area,
        "average_damage_bbox_area": average_damage_bbox_area,
        "largest_damage_bbox_area": largest_damage_bbox_area,
        "damage_area_percentage": damage_area_percentage,
    }


def compute_traffic_metrics(traffic_detections):
    """Compute traffic metrics from a list of traffic detections.

    Returns dict with:
        car_count, motorcycle_count, bus_count, truck_count, bicycle_count,
        total_vehicle_count, traffic_level
    """
    counts = {
        "car": 0,
        "motorcycle": 0,
        "bus": 0,
        "truck": 0,
        "bicycle": 0,
    }

    for det in traffic_detections:
        key = det["class_key"]
        if key in counts:
            counts[key] += 1

    total_vehicle_count = sum(counts.values())

    if total_vehicle_count <= 5:
        traffic_level = "Low"
    elif total_vehicle_count <= 15:
        traffic_level = "Medium"
    else:
        traffic_level = "High"

    return {
        "car_count": counts["car"],
        "motorcycle_count": counts["motorcycle"],
        "bus_count": counts["bus"],
        "truck_count": counts["truck"],
        "bicycle_count": counts["bicycle"],
        "total_vehicle_count": total_vehicle_count,
        "traffic_level": traffic_level,
    }


def compute_severity(damage_area_percentage):
    """Determine damage severity from damage area percentage."""
    if damage_area_percentage <= 1.0:
        return "Excellent"
    elif damage_area_percentage <= 3.0:
        return "Minor"
    elif damage_area_percentage <= 6.0:
        return "Moderate"
    elif damage_area_percentage <= 10.0:
        return "Severe"
    else:
        return "Critical"


def compute_traffic_score(total_vehicle_count):
    """Compute traffic score (0–100) from total vehicle count."""
    if total_vehicle_count <= 5:
        return 100
    elif total_vehicle_count <= 15:
        return 70
    else:
        return 40


def compute_road_damage_score(damage_metrics):
    """Compute road damage score starting at 100 with deductions."""
    score = 100
    score -= damage_metrics["longitudinal_crack_count"] * 5
    score -= damage_metrics["transverse_crack_count"] * 7
    score -= damage_metrics["alligator_crack_count"] * 10
    score -= damage_metrics["pothole_count"] * 15
    return max(0, min(100, score))


def compute_infrastructure_score(road_damage_score, traffic_score):
    """Compute combined infrastructure health score (0–100 integer)."""
    return round(0.70 * road_damage_score + 0.30 * traffic_score)


def compute_infrastructure_category(infrastructure_score):
    """Map infrastructure score to category label."""
    if 90 <= infrastructure_score <= 100:
        return "Excellent"
    elif 75 <= infrastructure_score <= 89:
        return "Good"
    elif 60 <= infrastructure_score <= 74:
        return "Fair"
    elif 40 <= infrastructure_score <= 59:
        return "Poor"
    else:
        return "Critical"


def compute_maintenance_priority(infrastructure_score):
    """Determine maintenance priority from infrastructure score."""
    if 90 <= infrastructure_score <= 100:
        return "None"
    elif 75 <= infrastructure_score <= 89:
        return "Low"
    elif 60 <= infrastructure_score <= 74:
        return "Medium"
    elif 40 <= infrastructure_score <= 59:
        return "High"
    else:
        return "Immediate"


def compute_recommendations(damage_metrics, traffic_level):
    """Generate maintenance recommendations list."""
    recs = []
    if damage_metrics["pothole_count"] > 0:
        recs.append("Repair potholes.")
    if damage_metrics["alligator_crack_count"] > 0:
        recs.append("Surface reconstruction recommended.")
    if damage_metrics["longitudinal_crack_count"] > 3:
        recs.append("Seal longitudinal cracks.")
    if damage_metrics["transverse_crack_count"] > 3:
        recs.append("Seal transverse cracks.")
    if traffic_level == "High":
        recs.append("Prioritize maintenance due to heavy traffic.")
    return recs


def process_image(road_detections, traffic_detections, image):
    """Run the full civic intelligence pipeline for one image.

    Returns a complete results dict for JSON output.
    """
    h, w = image.shape[:2]

    dm = compute_damage_metrics(road_detections, image)
    tm = compute_traffic_metrics(traffic_detections)

    severity = compute_severity(dm["damage_area_percentage"])
    traffic_score = compute_traffic_score(tm["total_vehicle_count"])
    road_damage_score = compute_road_damage_score(dm)
    infrastructure_score = compute_infrastructure_score(road_damage_score, traffic_score)
    infrastructure_category = compute_infrastructure_category(infrastructure_score)
    maintenance_priority = compute_maintenance_priority(infrastructure_score)
    recommendations = compute_recommendations(dm, tm["traffic_level"])

    result = {
        "image_width": w,
        "image_height": h,
        **dm,
        **tm,
        "road_damage_score": road_damage_score,
        "traffic_score": traffic_score,
        "infrastructure_score": infrastructure_score,
        "infrastructure_category": infrastructure_category,
        "severity": severity,
        "maintenance_priority": maintenance_priority,
        "recommendations": recommendations,
    }
    return result

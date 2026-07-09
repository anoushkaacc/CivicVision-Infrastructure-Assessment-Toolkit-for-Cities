"""Road damage detector wrapping the pretrained YOLOv8_Small_RDD model.

This module performs inference only. It loads the pretrained road damage
YOLO model and exposes a simple `detect` API that returns normalized
detection dictionaries used by the rest of the CivicVision pipeline.
"""

from ultralytics import YOLO

# Maps the road damage model's native class names to the internal
# civic-metric keys used throughout CivicVision.
CLASS_NAME_MAP = {
    "Longitudinal Crack": "longitudinal_crack",
    "Transverse Crack": "transverse_crack",
    "Alligator Crack": "alligator_crack",
    "Potholes": "pothole",
    "Pothole": "pothole",
}


class RoadDamageDetector:
    """Wraps the pretrained YOLOv8_Small_RDD model for road damage detection."""

    def __init__(self, model_path="YOLOv8_Small_RDD.pt", conf_threshold=0.25):
        self.model = YOLO(model_path)
        self.conf_threshold = conf_threshold

    def detect(self, image):
        """Run inference on a single image (numpy array, BGR).

        Returns a list of detections, each a dict with:
            class_key: normalized key (longitudinal_crack, transverse_crack,
                       alligator_crack, pothole)
            class_name: original model class name
            confidence: detection confidence (float)
            bbox: (x1, y1, x2, y2) in pixel coordinates
        """
        results = self.model.predict(source=image, conf=self.conf_threshold, verbose=False)
        detections = []
        if not results:
            return detections

        result = results[0]
        boxes = result.boxes
        if boxes is None or len(boxes) == 0:
            return detections

        names = result.names

        for box in boxes:
            cls_id = int(box.cls[0].item())
            confidence = float(box.conf[0].item())
            x1, y1, x2, y2 = box.xyxy[0].tolist()

            class_name = names.get(cls_id, str(cls_id)) if isinstance(names, dict) else names[cls_id]
            class_key = CLASS_NAME_MAP.get(class_name)
            if class_key is None:
                # Unknown class from this model; skip it.
                continue

            detections.append(
                {
                    "class_key": class_key,
                    "class_name": class_name,
                    "confidence": confidence,
                    "bbox": (x1, y1, x2, y2),
                }
            )

        return detections

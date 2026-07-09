"""Traffic detector wrapping the pretrained yolo11n model.

Filters detections to only the relevant COCO vehicle classes:
car, motorcycle, bus, truck, bicycle.
"""

from ultralytics import YOLO

# COCO class IDs for the five vehicle types we care about.
TRAFFIC_CLASS_IDS = {
    2: "car",
    3: "motorcycle",
    5: "bus",
    7: "truck",
    1: "bicycle",
}


class TrafficDetector:
    """Wraps the pretrained yolo11n model for vehicle detection."""

    def __init__(self, model_path="yolo11n.pt", conf_threshold=0.25):
        self.model = YOLO(model_path)
        self.conf_threshold = conf_threshold

    def detect(self, image):
        """Run inference on a single image (numpy array, BGR).

        Returns a list of detections, each a dict with:
            class_key: vehicle type key (car, motorcycle, bus, truck, bicycle)
            class_name: COCO class name
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

        for box in boxes:
            cls_id = int(box.cls[0].item())
            if cls_id not in TRAFFIC_CLASS_IDS:
                continue

            confidence = float(box.conf[0].item())
            x1, y1, x2, y2 = box.xyxy[0].tolist()
            class_key = TRAFFIC_CLASS_IDS[cls_id]

            detections.append(
                {
                    "class_key": class_key,
                    "class_name": class_key,
                    "confidence": confidence,
                    "bbox": (x1, y1, x2, y2),
                }
            )

        return detections

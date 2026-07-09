"""Visualization utilities — annotated images and dataset charts."""

import os
import cv2
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


# Colour palette for road damage classes
DAMAGE_COLORS = {
    "longitudinal_crack": (0, 0, 255),    # Red
    "transverse_crack": (255, 0, 0),      # Blue
    "alligator_crack": (0, 255, 255),     # Yellow
    "pothole": (0, 0, 0),                 # Black
}

# Colour palette for traffic classes
TRAFFIC_COLORS = {
    "car": (0, 255, 0),                   # Green
    "motorcycle": (255, 0, 255),          # Magenta
    "bus": (255, 255, 0),                 # Cyan
    "truck": (128, 0, 128),              # Purple
    "bicycle": (255, 128, 0),            # Orange
}


def draw_detections(image, road_detections, traffic_detections):
    """Draw bounding boxes and labels for all detections on the image."""
    img = image.copy()

    for det in road_detections:
        x1, y1, x2, y2 = [int(v) for v in det["bbox"]]
        color = DAMAGE_COLORS.get(det["class_key"], (255, 255, 255))
        cv2.rectangle(img, (x1, y1), (x2, y2), color, 2)
        label = f"{det['class_key']} {det['confidence']:.2f}"
        cv2.putText(img, label, (x1, max(y1 - 5, 20)),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1, cv2.LINE_AA)

    for det in traffic_detections:
        x1, y1, x2, y2 = [int(v) for v in det["bbox"]]
        color = TRAFFIC_COLORS.get(det["class_key"], (255, 255, 255))
        cv2.rectangle(img, (x1, y1), (x2, y2), color, 2)
        label = f"{det['class_key']} {det['confidence']:.2f}"
        cv2.putText(img, label, (x1, max(y1 - 5, 20)),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1, cv2.LINE_AA)

    return img


def draw_overlay(image, infrastructure_score, severity, traffic_level):
    """Draw a top-left overlay with infrastructure score, severity, and traffic level."""
    img = image.copy()
    h, w = img.shape[:2]

    overlay_text = [
        f"Score: {infrastructure_score}",
        f"Severity: {severity}",
        f"Traffic: {traffic_level}",
    ]

    # Semi-transparent background rectangle
    rect_x1, rect_y1 = 10, 10
    rect_x2, rect_y2 = 280, 90
    cv2.rectangle(img, (rect_x1, rect_y1), (rect_x2, rect_y2), (0, 0, 0), -1)
    overlay = img[rect_y1:rect_y2, rect_x1:rect_x2]
    alpha = 0.6
    img[rect_y1:rect_y2, rect_x1:rect_x2] = cv2.addWeighted(
        overlay, alpha, np.zeros_like(overlay), 1 - alpha, 0
    )

    for i, text in enumerate(overlay_text):
        y_pos = rect_y1 + 20 + i * 25
        cv2.putText(img, text, (rect_x1 + 10, y_pos),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1, cv2.LINE_AA)

    return img


def save_annotated_image(image, road_detections, traffic_detections,
                         infrastructure_score, severity, traffic_level, output_path):
    """Draw detections + overlay and save to disk."""
    img = draw_detections(image, road_detections, traffic_detections)
    img = draw_overlay(img, infrastructure_score, severity, traffic_level)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    cv2.imwrite(output_path, img)


def _save_plot(fig, output_path):
    """Save a matplotlib figure to disk."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    fig.savefig(output_path, bbox_inches="tight", dpi=150)
    plt.close(fig)


def plot_damage_bar_chart(damage_totals, output_path):
    """Bar chart of total damage counts by class."""
    categories = ["Longitudinal\nCrack", "Transverse\nCrack", "Alligator\nCrack", "Pothole"]
    keys = ["longitudinal_crack", "transverse_crack", "alligator_crack", "pothole"]
    values = [damage_totals.get(k, 0) for k in keys]
    colors = ["#ff0000", "#0000ff", "#00ffff", "#000000"]

    fig, ax = plt.subplots(figsize=(8, 5))
    bars = ax.bar(categories, values, color=colors, edgecolor="gray")
    for bar, v in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.5,
                str(v), ha="center", va="bottom", fontsize=11)
    ax.set_ylabel("Count")
    ax.set_title("Road Damage Class Distribution")
    ax.grid(axis="y", alpha=0.3)
    _save_plot(fig, output_path)


def plot_vehicle_bar_chart(vehicle_totals, output_path):
    """Bar chart of total vehicle counts by class."""
    categories = ["Car", "Motorcycle", "Bus", "Truck", "Bicycle"]
    keys = ["car", "motorcycle", "bus", "truck", "bicycle"]
    values = [vehicle_totals.get(k, 0) for k in keys]
    colors = ["#00ff00", "#ff00ff", "#00ffff", "#800080", "#ff8000"]

    fig, ax = plt.subplots(figsize=(8, 5))
    bars = ax.bar(categories, values, color=colors, edgecolor="gray")
    for bar, v in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.5,
                str(v), ha="center", va="bottom", fontsize=11)
    ax.set_ylabel("Count")
    ax.set_title("Vehicle Class Distribution")
    ax.grid(axis="y", alpha=0.3)
    _save_plot(fig, output_path)


def plot_infrastructure_histogram(scores, output_path):
    """Histogram of infrastructure scores across the dataset."""
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.hist(scores, bins=20, color="#4c72b0", edgecolor="white", alpha=0.8)
    ax.set_xlabel("Infrastructure Score")
    ax.set_ylabel("Number of Images")
    ax.set_title("Infrastructure Score Distribution")
    ax.grid(axis="y", alpha=0.3)
    _save_plot(fig, output_path)


def plot_severity_pie_chart(severity_counts, output_path):
    """Pie chart of severity distribution."""
    labels = list(severity_counts.keys())
    sizes = list(severity_counts.values())
    colors_pie = ["#2ecc71", "#f1c40f", "#e67e22", "#e74c3c", "#8e44ad"]

    fig, ax = plt.subplots(figsize=(7, 7))
    wedges, texts, autotexts = ax.pie(
        sizes, labels=labels, autopct="%1.1f%%",
        colors=colors_pie[:len(labels)], startangle=90,
        textprops={"fontsize": 11}
    )
    for at in autotexts:
        at.set_fontsize(10)
    ax.set_title("Severity Distribution", fontsize=14)
    _save_plot(fig, output_path)

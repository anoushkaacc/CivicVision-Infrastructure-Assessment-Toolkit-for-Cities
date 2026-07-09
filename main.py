#!/usr/bin/env python3
"""CivicVision v1 — AI-powered civic infrastructure assessment system.

Usage:
    python main.py <image_or_folder>

Processes road images with two pretrained YOLO models (road damage + traffic),
computes civic intelligence metrics, and generates annotated images, per-image
JSON reports, dataset summary JSON, charts, and a standalone HTML report.
"""

import sys
import json
import argparse
from pathlib import Path

import cv2

from modules.road_detector import RoadDamageDetector
from modules.traffic_detector import TrafficDetector
from modules.civic_engine import process_image
from modules.visualization import (
    save_annotated_image,
    plot_damage_bar_chart,
    plot_vehicle_bar_chart,
    plot_infrastructure_histogram,
    plot_severity_pie_chart,
)
from modules.report_generator import generate_summary_json, generate_html_report


SUPPORTED_EXTENSIONS = {".jpg", ".jpeg", ".png"}


def collect_images(path):
    """Return list of image paths from a single file or a directory."""
    path = Path(path)
    if path.is_file():
        if path.suffix.lower() in SUPPORTED_EXTENSIONS:
            return [path]
        else:
            print(f"Warning: unsupported file format: {path}")
            return []
    elif path.is_dir():
        images = sorted(
            p for p in path.iterdir()
            if p.is_file() and p.suffix.lower() in SUPPORTED_EXTENSIONS
        )
        return images
    else:
        print(f"Error: {path} is not a valid file or directory.")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="CivicVision v1 — AI-powered civic infrastructure assessment."
    )
    parser.add_argument(
        "input",
        type=str,
        help="Path to a single image or a folder containing road images.",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="outputs",
        help="Output directory (default: outputs)",
    )
    args = parser.parse_args()

    output_dir = Path(args.output)
    annotated_dir = output_dir / "annotated"
    json_dir = output_dir / "json"
    plots_dir = output_dir / "plots"

    annotated_dir.mkdir(parents=True, exist_ok=True)
    json_dir.mkdir(parents=True, exist_ok=True)
    plots_dir.mkdir(parents=True, exist_ok=True)

    print("Loading models...")
    road_detector = RoadDamageDetector(model_path="YOLOv8_Small_RDD.pt")
    traffic_detector = TrafficDetector(model_path="yolo11n.pt")
    print("Models loaded.\n")

    image_paths = collect_images(args.input)
    if not image_paths:
        print("No supported images found.")
        sys.exit(0)

    print(f"Processing {len(image_paths)} image(s)...\n")
    results = []

    for img_path in image_paths:
        stem = img_path.stem
        ext = img_path.suffix
        print(f"  {img_path.name} ...", end=" ", flush=True)

        image_bgr = cv2.imread(str(img_path))
        if image_bgr is None:
            print("FAILED (could not read)")
            continue
        image_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)

        road_dets = road_detector.detect(image_rgb)
        traffic_dets = traffic_detector.detect(image_rgb)

        metrics = process_image(road_dets, traffic_dets, image_bgr)
        metrics["filename"] = img_path.name

        json_path = json_dir / f"{stem}.json"
        with open(json_path, "w") as f:
            json.dump(metrics, f, indent=2)

        annotated_path = annotated_dir / f"{stem}{ext}"
        save_annotated_image(
            image_bgr,
            road_dets,
            traffic_dets,
            metrics["infrastructure_score"],
            metrics["severity"],
            metrics["traffic_level"],
            str(annotated_path),
        )

        results.append(metrics)
        print("done")

    print(f"\nAll images processed. Generating reports...")

    summary_data = generate_summary_json(results, str(output_dir / "summary.json"))
    if len(results) > 0:
        summary, damage_totals, vehicle_totals, category_counts = summary_data
    else:
        print("No results to report.")
        sys.exit(0)

    plot_damage_bar_chart(damage_totals, str(plots_dir / "damage_bar_chart.png"))
    plot_vehicle_bar_chart(vehicle_totals, str(plots_dir / "vehicle_bar_chart.png"))

    scores = [r["infrastructure_score"] for r in results]
    plot_infrastructure_histogram(scores, str(plots_dir / "infrastructure_histogram.png"))

    severity_counts = {}
    for r in results:
        sev = r["severity"]
        severity_counts[sev] = severity_counts.get(sev, 0) + 1
    plot_severity_pie_chart(severity_counts, str(plots_dir / "severity_pie_chart.png"))

    chart_paths = {
        "Damages": str(plots_dir / "damage_bar_chart.png"),
        "Vehicles": str(plots_dir / "vehicle_bar_chart.png"),
        "Scores": str(plots_dir / "infrastructure_histogram.png"),
        "Severity": str(plots_dir / "severity_pie_chart.png"),
    }

    generate_html_report(
        results,
        summary,
        damage_totals,
        vehicle_totals,
        category_counts,
        chart_paths,
        str(annotated_dir),
        str(json_dir),
        str(output_dir / "report.html"),
    )

    print(f"Report generated: {output_dir / 'report.html'}")
    print(f"Summary JSON: {output_dir / 'summary.json'}")
    print("Done.")


if __name__ == "__main__":
    main()

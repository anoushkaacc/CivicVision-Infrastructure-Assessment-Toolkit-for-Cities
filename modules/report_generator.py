"""Generates the standalone HTML report and summary JSON for the dataset."""

import os
import json
import base64
from pathlib import Path


def _img_to_b64(path):
    """Read an image file and return a base64 data URI."""
    with open(path, "rb") as f:
        data = f.read()
    ext = Path(path).suffix.lower().lstrip(".")
    if ext in ("jpg", "jpeg"):
        mime = "image/jpeg"
    elif ext == "png":
        mime = "image/png"
    else:
        mime = "image/png"
    return f"data:{mime};base64,{base64.b64encode(data).decode()}"


def generate_summary_json(results, output_path):
    """Generate summary.json from the list of per-image results."""
    n = len(results)
    if n == 0:
        summary = {"total_images": 0}
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "w") as f:
            json.dump(summary, f, indent=2)
        return summary

    scores = [r["infrastructure_score"] for r in results]
    damage_scores = [r["road_damage_score"] for r in results]
    traffic_scores = [r["traffic_score"] for r in results]

    damage_totals = {
        "pothole": sum(r["pothole_count"] for r in results),
        "longitudinal_crack": sum(r["longitudinal_crack_count"] for r in results),
        "transverse_crack": sum(r["transverse_crack_count"] for r in results),
        "alligator_crack": sum(r["alligator_crack_count"] for r in results),
    }

    vehicle_totals = {
        "car": sum(r["car_count"] for r in results),
        "motorcycle": sum(r["motorcycle_count"] for r in results),
        "bus": sum(r["bus_count"] for r in results),
        "truck": sum(r["truck_count"] for r in results),
        "bicycle": sum(r["bicycle_count"] for r in results),
    }

    category_counts = {"Excellent": 0, "Good": 0, "Fair": 0, "Poor": 0, "Critical": 0}
    for r in results:
        cat = r.get("infrastructure_category", "Critical")
        if cat in category_counts:
            category_counts[cat] += 1

    avg_damage_area_pct = sum(r["damage_area_percentage"] for r in results) / n
    avg_vehicle_count = sum(r["total_vehicle_count"] for r in results) / n

    summary = {
        "total_images": n,
        "average_infrastructure_score": round(sum(scores) / n, 2),
        "average_damage_score": round(sum(damage_scores) / n, 2),
        "average_traffic_score": round(sum(traffic_scores) / n, 2),
        "total_potholes": damage_totals["pothole"],
        "total_longitudinal_cracks": damage_totals["longitudinal_crack"],
        "total_transverse_cracks": damage_totals["transverse_crack"],
        "total_alligator_cracks": damage_totals["alligator_crack"],
        "total_cars": vehicle_totals["car"],
        "total_motorcycles": vehicle_totals["motorcycle"],
        "total_buses": vehicle_totals["bus"],
        "total_trucks": vehicle_totals["truck"],
        "total_bicycles": vehicle_totals["bicycle"],
        "distribution": category_counts,
        "average_damage_area_percentage": round(avg_damage_area_pct, 2),
        "average_vehicle_count": round(avg_vehicle_count, 2),
    }

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(summary, f, indent=2)
    return summary, damage_totals, vehicle_totals, category_counts


def generate_html_report(results, summary, damage_totals, vehicle_totals,
                         category_counts, chart_paths, annotated_dir, json_dir, output_path):
    """Generate a standalone self-contained HTML report."""
    n = summary["total_images"]

    # Build rows for the images table
    table_rows = ""
    for r in results:
        fn = r.get("filename", "unknown")
        # Find annotated thumbnail
        annotated_path = os.path.join(annotated_dir, fn)
        if not os.path.exists(annotated_path):
            base_stem = Path(fn).stem
            for ext in [".jpg", ".jpeg", ".png"]:
                test = os.path.join(annotated_dir, base_stem + ext)
                if os.path.exists(test):
                    annotated_path = test
                    break

        thumb_html = ""
        if os.path.exists(annotated_path):
            uri = _img_to_b64(annotated_path)
            thumb_html = f'<img src="{uri}" alt="{fn}" style="max-width:200px;max-height:150px;border:1px solid #ccc;">'
        else:
            thumb_html = f'<span style="color:#999;">No annotation</span>'

        recs = r.get("recommendations", [])
        recs_html = "<br>".join(recs) if recs else "—"

        table_rows += f"""<tr>
            <td>{fn}</td>
            <td>{thumb_html}</td>
            <td>{r["longitudinal_crack_count"]}</td>
            <td>{r["transverse_crack_count"]}</td>
            <td>{r["alligator_crack_count"]}</td>
            <td>{r["pothole_count"]}</td>
            <td>{r["car_count"]}</td>
            <td>{r["motorcycle_count"]}</td>
            <td>{r["bus_count"]}</td>
            <td>{r["truck_count"]}</td>
            <td>{r["bicycle_count"]}</td>
            <td>{r["infrastructure_score"]}</td>
            <td>{r["severity"]}</td>
            <td>{r["maintenance_priority"]}</td>
            <td>{recs_html}</td>
        </tr>"""

    # Embed charts
    chart_sections = ""
    for label, cp in chart_paths.items():
        if os.path.exists(cp):
            uri = _img_to_b64(cp)
            chart_sections += f'<div style="margin:20px 0;"><h3>{label}</h3><img src="{uri}" style="max-width:700px;border:1px solid #ddd;"></div>'

    # Distribution as text
    dist_html = "".join(
        f"<li>{k}: {v}</li>" for k, v in category_counts.items()
    )

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>CivicVision — Infrastructure Assessment Report</title>
<style>
    body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
    h1, h2, h3 {{ color: #333; }}
    .container {{ max-width: 1200px; margin: auto; background: #fff; padding: 20px; border-radius: 8px; box-shadow: 0 0 10px rgba(0,0,0,0.1); }}
    .summary {{ display: flex; flex-wrap: wrap; gap: 15px; margin: 20px 0; }}
    .card {{ background: #fafafa; border: 1px solid #ddd; border-radius: 6px; padding: 15px; flex: 1 1 200px; }}
    .card h3 {{ margin: 0 0 8px; font-size: 14px; color: #666; }}
    .card .value {{ font-size: 24px; font-weight: bold; color: #222; }}
    table {{ width: 100%; border-collapse: collapse; margin: 20px 0; font-size: 13px; }}
    th, td {{ border: 1px solid #ddd; padding: 8px; text-align: center; }}
    th {{ background: #4c72b0; color: #fff; }}
    tr:nth-child(even) {{ background: #f9f9f9; }}
    .charts {{ display: flex; flex-wrap: wrap; gap: 20px; justify-content: center; }}
    ul.dist {{ list-style: none; padding: 0; }}
    ul.dist li {{ padding: 4px 0; }}
</style>
</head>
<body>
<div class="container">
    <h1>CivicVision — Infrastructure Assessment Report</h1>
    <p>Generated by CivicVision v1 — AI-powered civic infrastructure assessment.</p>

    <h2>Dataset Summary</h2>
    <div class="summary">
        <div class="card"><h3>Total Images</h3><div class="value">{n}</div></div>
        <div class="card"><h3>Avg Infrastructure Score</h3><div class="value">{summary["average_infrastructure_score"]}</div></div>
        <div class="card"><h3>Avg Damage Score</h3><div class="value">{summary["average_damage_score"]}</div></div>
        <div class="card"><h3>Avg Traffic Score</h3><div class="value">{summary["average_traffic_score"]}</div></div>
        <div class="card"><h3>Avg Damage Area %</h3><div class="value">{summary["average_damage_area_percentage"]}</div></div>
        <div class="card"><h3>Avg Vehicle Count</h3><div class="value">{summary["average_vehicle_count"]}</div></div>
    </div>

    <h2>Aggregate Metrics</h2>
    <div class="summary">
        <div class="card"><h3>Total Potholes</h3><div class="value">{damage_totals["pothole"]}</div></div>
        <div class="card"><h3>Total Longitudinal Cracks</h3><div class="value">{damage_totals["longitudinal_crack"]}</div></div>
        <div class="card"><h3>Total Transverse Cracks</h3><div class="value">{damage_totals["transverse_crack"]}</div></div>
        <div class="card"><h3>Total Alligator Cracks</h3><div class="value">{damage_totals["alligator_crack"]}</div></div>
        <div class="card"><h3>Total Cars</h3><div class="value">{vehicle_totals["car"]}</div></div>
        <div class="card"><h3>Total Motorcycles</h3><div class="value">{vehicle_totals["motorcycle"]}</div></div>
        <div class="card"><h3>Total Buses</h3><div class="value">{vehicle_totals["bus"]}</div></div>
        <div class="card"><h3>Total Trucks</h3><div class="value">{vehicle_totals["truck"]}</div></div>
        <div class="card"><h3>Total Bicycles</h3><div class="value">{vehicle_totals["bicycle"]}</div></div>
    </div>

    <h2>Infrastructure Distribution</h2>
    <ul class="dist">{dist_html}</ul>

    <h2>Charts</h2>
    <div class="charts">{chart_sections}</div>

    <h2>Per-Image Results</h2>
    <div style="overflow-x:auto;">
    <table>
        <thead>
            <tr>
                <th>Filename</th>
                <th>Annotated</th>
                <th>Longitudinal</th>
                <th>Transverse</th>
                <th>Alligator</th>
                <th>Pothole</th>
                <th>Car</th>
                <th>Mcycle</th>
                <th>Bus</th>
                <th>Truck</th>
                <th>Bicycle</th>
                <th>Score</th>
                <th>Severity</th>
                <th>Priority</th>
                <th>Recommendations</th>
            </tr>
        </thead>
        <tbody>
            {table_rows}
        </tbody>
    </table>
    </div>

    <p style="text-align:center;color:#999;margin-top:30px;">CivicVision v1 Report</p>
</div>
</body>
</html>"""

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)

    return output_path

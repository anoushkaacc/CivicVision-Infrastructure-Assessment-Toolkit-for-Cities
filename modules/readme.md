# CivicVision 

**CivicVision** is an AI-powered civic infrastructure assessment system that analyzes road images to detect road damage and traffic conditions in real-time. It uses state-of-the-art deep learning models to evaluate road health, generate comprehensive reports, and provide data-driven maintenance recommendations.

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Quick Start](#quick-start)
- [Installation](#installation)
- [Usage](#usage)
- [Output Structure](#output-structure)
- [Scoring System](#scoring-system)
- [Metrics & Algorithms](#metrics--algorithms)
- [Example Output](#example-output)
- [Models Used](#models-used)
- [Architecture](#architecture)
- [Project Structure](#project-structure)
- [Requirements](#requirements)
- [License](#license)

## Overview

CivicVision automates the assessment of road infrastructure by:

1. **Detecting Road Damage**: Identifies and classifies four types of road deterioration (cracks, potholes)
2. **Monitoring Traffic**: Detects and counts vehicles to assess traffic congestion levels
3. **Computing Health Metrics**: Generates quantitative infrastructure health scores (0-100)
4. **Generating Reports**: Creates annotated images, JSON data, visualizations, and interactive HTML reports
5. **Providing Recommendations**: Suggests maintenance actions based on detected damage and traffic patterns

This system is ideal for:
- Urban planning and infrastructure management
- Predictive maintenance scheduling
- Civil engineering assessments
- Traffic pattern analysis
- Civic data collection and reporting

## Features

### Road Damage Detection
- Detects **4 damage types**:
  - Longitudinal Cracks
  - Transverse Cracks
  - Alligator Cracks
  - Potholes
- Computes damage metrics including area coverage percentage
- Generates damage severity ratings

### Traffic Analysis
- Detects **5 vehicle types**:
  - Cars
  - Motorcycles
  - Buses
  - Trucks
  - Bicycles
- Classifies traffic levels: Low / Medium / High
- Tracks aggregate traffic statistics

### Comprehensive Metrics
- **Infrastructure Score**: Combined health metric (0-100)
- **Road Damage Score**: Deduction-based damage assessment (0-100)
- **Traffic Score**: Vehicle density evaluation (0-100)
- **Damage Area Percentage**: Proportion of road surface affected
- **Severity Rating**: Qualitative assessment (Excellent → Critical)
- **Maintenance Priority**: Actionable priority levels (None → Immediate)

### Multiple Output Formats
- **Annotated Images**: Original images with bounding boxes and overlay metrics
- **Per-Image JSON**: Detailed detection data and metrics for each image
- **Summary JSON**: Aggregate statistics across all processed images
- **Dataset Charts**: Bar charts, histograms, and pie charts
- **Interactive HTML Report**: Self-contained, standalone report with embedded images and charts

### Visualization
- Color-coded bounding boxes for each damage type
- Overlay display of infrastructure score, severity, and traffic level
- Professional dataset visualizations
- Responsive HTML report with styled tables and charts

## Quick Start

```bash
# 1. Clone the repository
git clone https://github.com/yourusername/civicvision.git
cd civicvision

# 2. Install dependencies
pip install -r requirements.txt

# 3. Download pre-trained models
# Models should be placed in the project root:
# - YOLOv8_Small_RDD.pt (road damage model)
# - yolo11n.pt (traffic detection model)

# 4. Process images
python main.py path/to/image_or_folder

# 5. View results
# Open outputs/report.html in your browser
```

## Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager
- 2GB+ disk space (for models)
- 4GB+ RAM recommended

### Step 1: Clone Repository
```bash
git clone https://github.com/yourusername/civicvision.git
cd civicvision
```

### Step 2: Create Virtual Environment (Optional but recommended)
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Download Pre-trained Models
Download the following models and place them in the project root directory:

1. **YOLOv8_Small_RDD.pt** (Road Damage Detector)
   - Size: ~26 MB
   - [Download from source](https://github.com/RDD2020/RDD2020-Challenge)

2. **yolo11n.pt** (Traffic Detector)
   - Size: ~25 MB
   - Automatically downloads via Ultralytics on first run

```bash
# Models should be in:
civicvision/
├── YOLOv8_Small_RDD.pt
├── yolo11n.pt
└── ...
```

## Usage

### Basic Usage

#### Process a Single Image
```bash
python main.py path/to/image.jpg
```

#### Process an Image Folder
```bash
python main.py path/to/image_folder
```

#### Specify Custom Output Directory
```bash
python main.py path/to/images --output custom_outputs
```

### Command-Line Arguments

```
usage: main.py [-h] [--output OUTPUT] input

positional arguments:
  input              Path to a single image or folder containing road images

optional arguments:
  -h, --help         show this help message and exit
  --output OUTPUT    Output directory (default: outputs)
```

### Example Workflow

```bash
# Process all images in a folder
python main.py ./road_images --output ./results

# Check the results
ls -la ./results/
# outputs:
# - annotated/         (images with detections)
# - json/              (per-image reports)
# - plots/             (charts and visualizations)
# - report.html        (interactive report)
# - summary.json       (aggregate statistics)
```

## Output Structure

After processing, the following directory structure is created:

```
outputs/
├── annotated/
│   ├── image_001.jpg      (original image with bounding boxes)
│   ├── image_002.jpg
│   └── ...
├── json/
│   ├── image_001.json     (detailed metrics and detections)
│   ├── image_002.json
│   └── ...
├── plots/
│   ├── damage_bar_chart.png
│   ├── vehicle_bar_chart.png
│   ├── infrastructure_histogram.png
│   └── severity_pie_chart.png
├── report.html            (interactive HTML report)
└── summary.json           (dataset-wide aggregate stats)
```

## Scoring System

### Infrastructure Score (0-100)
Combined metric using weighted average:
```
Infrastructure Score = 0.70 × Road Damage Score + 0.30 × Traffic Score
```

**Weight Rationale:**
- Road Damage (70%): Primary factor for maintenance decisions
- Traffic (30%): Secondary factor affecting urgency

### Road Damage Score (0-100)
Deduction-based scoring starting from 100:
```
Score = 100
       - (Longitudinal Cracks × 5)
       - (Transverse Cracks × 7)
       - (Alligator Cracks × 10)
       - (Potholes × 15)

Score Range: 0-100 (clamped)
```

### Traffic Score (0-100)
Vehicle density classification:
```
Vehicle Count ≤ 5    → Traffic Score = 100 (Low Traffic)
5 < Count ≤ 15       → Traffic Score = 70  (Medium Traffic)
Count > 15           → Traffic Score = 40  (High Traffic)
```

### Severity Rating (Qualitative)
Based on damage area percentage:
```
≤ 1.0%   → Excellent
1.0-3.0% → Minor
3.0-6.0% → Moderate
6.0-10%  → Severe
> 10%    → Critical
```

### Infrastructure Category
Based on infrastructure score:
```
90-100   → Excellent  (No maintenance needed)
75-89    → Good       (Low priority)
60-74    → Fair       (Medium priority)
40-59    → Poor       (High priority)
0-39     → Critical   (Immediate action required)
```

### Maintenance Priority
Action-level classification:
```
Infrastructure Score 90-100  → Priority: None
Infrastructure Score 75-89   → Priority: Low
Infrastructure Score 60-74   → Priority: Medium
Infrastructure Score 40-59   → Priority: High
Infrastructure Score 0-39    → Priority: Immediate
```

## Metrics & Algorithms

### Damage Metrics

For each detected damage type:

| Metric | Description | Calculation |
|--------|-------------|-------------|
| **Count** | Number of detected instances | Sum of bounding boxes per class |
| **Total Area** | Sum of bounding box areas (pixels) | Σ (x2-x1) × (y2-y1) |
| **Average Area** | Mean size of detected damage | Total Area / Count |
| **Largest Area** | Biggest single damage instance | Max(areas) |
| **Damage %** | Percentage of road covered | (Total Area / Image Area) × 100 |

### Traffic Metrics

| Metric | Description |
|--------|-------------|
| **Vehicle Counts** | Individual count per vehicle type |
| **Total Vehicle Count** | Sum of all detected vehicles |
| **Traffic Level** | Classification: Low / Medium / High |

### Quality Metrics

| Metric | Description |
|--------|-------------|
| **Image Dimensions** | Width and height in pixels |
| **Detection Confidence** | Model confidence score (0.0-1.0) per detection |

## Example Output

### Per-Image JSON Report (`India_000004.json`)

```json
{
  "image_width": 720,
  "image_height": 720,
  "longitudinal_crack_count": 0,
  "transverse_crack_count": 0,
  "alligator_crack_count": 0,
  "pothole_count": 0,
  "total_damage_count": 0,
  "total_damage_bbox_area": 0,
  "average_damage_bbox_area": 0.0,
  "largest_damage_bbox_area": 0.0,
  "damage_area_percentage": 0.0,
  "car_count": 0,
  "motorcycle_count": 0,
  "bus_count": 0,
  "truck_count": 0,
  "bicycle_count": 0,
  "total_vehicle_count": 0,
  "traffic_level": "Low",
  "road_damage_score": 100,
  "traffic_score": 100,
  "infrastructure_score": 100,
  "infrastructure_category": "Excellent",
  "severity": "Excellent",
  "maintenance_priority": "None",
  "recommendations": [],
  "filename": "India_000004.jpg"
}
```

### Dataset Summary JSON (`summary.json`)

```json
{
  "total_images": 1,
  "average_infrastructure_score": 91.0,
  "average_damage_score": 100.0,
  "average_traffic_score": 70.0,
  "total_potholes": 0,
  "total_longitudinal_cracks": 0,
  "total_transverse_cracks": 0,
  "total_alligator_cracks": 0,
  "total_cars": 4,
  "total_motorcycles": 0,
  "total_buses": 0,
  "total_trucks": 2,
  "total_bicycles": 0,
  "distribution": {
    "Excellent": 1,
    "Good": 0,
    "Fair": 0,
    "Poor": 0,
    "Critical": 0
  },
  "average_damage_area_percentage": 0.0,
  "average_vehicle_count": 6.0
}
```

### HTML Report Features

The generated `report.html` includes:

- **Dashboard Overview**
  - Total images processed
  - Average infrastructure score
  - Average damage and traffic scores
  - Key metrics cards

- **Aggregate Statistics**
  - Total damage counts by type
  - Total vehicle counts by type
  - Infrastructure category distribution

- **Visualizations**
  - Damage bar charts
  - Vehicle detection bar charts
  - Infrastructure health histogram
  - Severity distribution pie chart

- **Per-Image Table**
  - Thumbnail of annotated image
  - Individual damage counts
  - Individual vehicle counts
  - Infrastructure score
  - Maintenance priority
  - AI-generated recommendations

- **Responsive Design**
  - Mobile-friendly layout
  - Embedded images (no external dependencies)
  - Professional styling

## Models Used

### 1. YOLOv8_Small_RDD (Road Damage Detection)
- **Purpose**: Detect and classify road damage
- **Architecture**: YOLOv8 Small variant
- **Training Data**: RDD2020 Challenge dataset
- **Output Classes**:
  - Longitudinal Crack
  - Transverse Crack
  - Alligator Crack
  - Potholes
- **Size**: ~26 MB
- **Confidence Threshold**: 0.25 (adjustable)

### 2. YOLOv11n (Traffic Detection)
- **Purpose**: Detect and classify vehicles
- **Architecture**: YOLOv11 Nano variant
- **Training Data**: COCO dataset
- **Output Classes** (filtered):
  - Car (COCO ID: 2)
  - Motorcycle (COCO ID: 3)
  - Bus (COCO ID: 5)
  - Truck (COCO ID: 7)
  - Bicycle (COCO ID: 1)
- **Size**: ~25 MB
- **Confidence Threshold**: 0.25 (adjustable)

## Architecture

### System Components

```
┌─────────────────────────────────────────────────────────────┐
│                      Input Images                            │
│          (Single file or folder of JPG/PNG)                  │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
         ┌───────────────────────────────┐
         │    Load Pre-trained Models     │
         │  ├─ YOLOv8_Small_RDD          │
         │  └─ YOLOv11n                  │
         └───────────────────────────────┘
                         │
                         ▼
         ┌───────────────────────────────┐
         │   For Each Image              │
         ├─ Road Damage Detection        │
         ├─ Traffic Vehicle Detection    │
         └───────────────────────────────┘
                         │
                         ▼
         ┌───────────────────────────────┐
         │   Civic Engine Processing     │
         ├─ Compute Damage Metrics       │
         ├─ Compute Traffic Metrics      │
         ├─ Calculate Scores             │
         ├─ Generate Recommendations     │
         └───────────────────────────────┘
                         │
        ┌────────────────┼────────────────┐
        ▼                ▼                ▼
    Annotated      JSON Report      Visualization
    Images         (Per-image)       Generation
        │                │                │
        └────────────────┼────────────────┘
                         ▼
         ┌───────────────────────────────┐
         │    Report Generation          │
         ├─ HTML Report                  │
         ├─ Summary JSON                 │
         ├─ Charts & Plots               │
         └───────────────────────────────┘
                         │
                         ▼
         ┌───────────────────────────────┐
         │    Output Directory           │
         ├─ outputs/annotated/           │
         ├─ outputs/json/                │
         ├─ outputs/plots/               │
         ├─ outputs/report.html          │
         └─ outputs/summary.json         │
         └───────────────────────────────┘
```

### Module Structure

```
civicvision/
├── main.py                    # Entry point, CLI argument parsing
├── modules/
│   ├── __init__.py
│   ├── road_detector.py       # Road damage detection module
│   ├── traffic_detector.py    # Traffic detection module
│   ├── civic_engine.py        # Metrics computation & scoring
│   ├── visualization.py       # Image annotation & charting
│   └── report_generator.py    # HTML & JSON report generation
├── YOLOv8_Small_RDD.pt        # Pre-trained road damage model
├── yolo11n.pt                 # Pre-trained traffic model
└── README.md
```

## Project Structure

```
civicvision/
├── main.py                         # Main entry point
├── README.md                       # This file
├── requirements.txt                # Python dependencies
├── model_names.txt                 # Model information
├── pip_list.txt                    # Full pip package list
│
├── modules/                        # Core modules
│   ├── __init__.py
│   ├── civic_engine.py            # Metric computation
│   ├── report_generator.py        # Report generation
│   ├── road_detector.py           # Road damage detection
│   ├── traffic_detector.py        # Vehicle detection
│   └── visualization.py           # Visualization utilities
│
├── YOLOv8_Small_RDD.pt            # Road damage model
├── yolo11n.pt                     # Traffic detection model
│
└── outputs/                        # Generated outputs
    ├── annotated/                 # Annotated images
    ├── json/                      # Per-image JSON reports
    ├── plots/                     # Generated charts
    ├── report.html                # Interactive HTML report
    └── summary.json               # Dataset summary
```

## Requirements

### Python Dependencies
```
ultralytics>=8.0.0
opencv-python>=4.8.0
numpy>=1.24.0
matplotlib>=3.7.0
Pillow>=10.0.0
```

### System Requirements
- **OS**: Windows, macOS, or Linux
- **Python**: 3.8+
- **RAM**: 4GB minimum (8GB+ recommended)
- **Disk Space**: 2GB+ for models
- **GPU**: Optional (CUDA 11.0+ for faster inference)

## Advanced Usage

### Adjusting Confidence Thresholds

Edit `main.py` to customize model confidence thresholds:

```python
# Lines 75-76 in main.py
road_detector = RoadDamageDetector(model_path="YOLOv8_Small_RDD.pt", conf_threshold=0.30)
traffic_detector = TrafficDetector(model_path="yolo11n.pt", conf_threshold=0.30)
```

Lower values (0.15-0.25) = More detections (higher sensitivity)
Higher values (0.35-0.50) = Fewer detections (higher specificity)

### Processing Large Datasets

For processing thousands of images efficiently:

```bash
# Process all images in a folder
python main.py /path/to/large_dataset --output /path/to/results

# Or split into batches and process separately
python main.py /path/to/dataset_batch_1 --output /path/to/results_1
python main.py /path/to/dataset_batch_2 --output /path/to/results_2
```

## Performance Notes

- **Single Image**: ~2-5 seconds (depends on image size and hardware)
- **Batch Processing (100 images)**: ~3-8 minutes
- **Report Generation**: Included in processing time
- **GPU Acceleration**: Approximately 3-5x faster than CPU

## Troubleshooting

### Models Not Found
```
Error: FileNotFoundError: YOLOv8_Small_RDD.pt
```
**Solution**: Ensure model files are in the project root directory

### Out of Memory
```
Error: CUDA out of memory
```
**Solution**: 
- Process fewer images at a time
- Run on CPU: Edit `road_detector.py` and `traffic_detector.py` to force CPU usage
- Reduce image resolution

### No Detections Found
- Check that models are loaded correctly
- Verify image format (JPG, PNG supported)
- Lower confidence thresholds (see Advanced Usage)
- Check image quality and resolution

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.



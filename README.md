# Advanced Real-Time Abandoned Object Detection Using YOLOv8s, ByteTrack, and OSNet-Based Owner Re-Identification

## Overview

This project presents an intelligent real-time abandoned object detection framework for surveillance applications. The system integrates **YOLOv8s** for object detection, **ByteTrack** for multi-object tracking, and **OSNet** for person re-identification to accurately associate baggage with its owner and detect unattended objects.

Unlike traditional approaches that rely only on spatial distance and time thresholds, this framework incorporates identity-aware owner assignment and dynamic risk assessment to improve robustness in crowded surveillance environments.

---

## Features

- Real-time person and baggage detection using YOLOv8s
- Multi-object tracking using ByteTrack
- Person re-identification using OSNet
- Identity-aware owner assignment
- Abandoned object detection using distance and time constraints
- Dynamic risk assessment
- Real-time Streamlit dashboard
- CPU-compatible implementation

---

## System Architecture

```
Input Surveillance Video
          │
          ▼
Frame Extraction (OpenCV)
          │
          ▼
YOLOv8s Object Detection
          │
          ▼
ByteTrack Multi-Object Tracking
          │
          ▼
OSNet Person Re-Identification
          │
          ▼
Identity-Aware Owner Assignment
          │
          ▼
Abandoned Object Detection
          │
          ▼
Dynamic Risk Assessment
          │
          ▼
Alert Generation & Streamlit Dashboard
```

---

## Technologies Used

| Component | Technology |
|------------|------------|
| Programming Language | Python |
| Object Detection | YOLOv8s |
| Tracking | ByteTrack |
| Person Re-Identification | OSNet |
| Computer Vision | OpenCV |
| Deep Learning | PyTorch |
| Dashboard | Streamlit |
| IDE | Visual Studio Code |

---

## Project Structure

```
Abandoned_Object_Detection/
│
├── models/
│   ├── yolov8s.pt
│   └── osnet/
│
├── tracker/
│   └── my_bytetrack.yaml
│
├── videos/
│   ├── sample.mp4
│   └── output.mp4
│
├── streamlit_app.py
├── main.py
├── owner_assignment.py
├── risk_assessment.py
├── utils.py
├── requirements.txt
└── README.md
```

---

## Installation

Clone the repository

```bash
git clone https://github.com/<your-username>/<repository-name>.git
cd <repository-name>
```

Create a virtual environment

```bash
python -m venv venv
```

Activate the environment

Windows

```bash
venv\Scripts\activate
```

Linux / macOS

```bash
source venv/bin/activate
```

Install dependencies

```bash
pip install -r requirements.txt
```

---

## Running the Project

Run the detection script

```bash
python main.py
```

Run the Streamlit dashboard

```bash
streamlit run streamlit_app.py
```

---

## Methodology

### 1. Video Acquisition

Surveillance videos are processed frame by frame using OpenCV.

### 2. Object Detection

YOLOv8s detects:

- Person
- Backpack
- Handbag
- Suitcase

### 3. Multi-Object Tracking

ByteTrack assigns unique IDs to detected objects and maintains identity across frames.

### 4. Person Re-Identification

OSNet extracts appearance features to recover identities during occlusion and re-entry.

### 5. Owner Assignment

Each baggage object is associated with its owner using:

- Spatial Distance
- Motion Consistency
- Bounding Box Overlap
- Re-ID Similarity

### 6. Abandonment Detection

The owner–bag relationship is continuously monitored using distance and elapsed time.

### 7. Dynamic Risk Assessment

Risk is gradually increased before declaring an object abandoned.

---

## Results

The proposed framework was evaluated on multiple surveillance video scenarios including:

- Single abandoned baggage
- Crowded environments
- Multiple persons and baggage
- Occlusion scenarios
- Shoulder bag scenarios

The system successfully demonstrated:

- Real-time object detection
- Multi-object tracking
- Owner association
- Abandoned object detection
- Risk visualization

---

## Current Limitations

- Identity switching during heavy occlusion
- Temporary incorrect owner assignment
- False High-Risk alerts for stationary shoulder bags
- High processing time on CPU
- Limited availability of annotated abandoned object datasets

---

## Future Work

- GPU acceleration
- Support for YOLOv11
- Improved owner assignment logic
- Enhanced person re-identification
- Multi-camera surveillance
- Evaluation on larger benchmark datasets
- Deployment on NVIDIA Jetson devices

---

## Research Contribution

The major contributions of this work include:

- Integration of YOLOv8s, ByteTrack, and OSNet into a unified surveillance framework.
- Identity-aware owner assignment using spatial and appearance information.
- Dynamic risk assessment for prioritizing suspicious unattended baggage.
- Real-time visualization using Streamlit.
- Analysis of practical challenges such as ID switching and owner association.

---

## License

This project is intended for academic and research purposes.

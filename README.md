<br />
<div align="center">
  <h1 align="center">SentryApp 3.2</h1>

  <p align="center">
    A Python-based Motion Detection & Optical Flow Dashboard
    <br />
    <br />
    <a href="https://github.com/DavidIZ-rob/SENTRYAPP_3.2/issues">Report Bug</a>
    ·
    <a href="https://github.com/DavidIZ-rob/SENTRYAPP_3.2/pulls">Request Feature</a>
  </p>
</div>

<div align="center">

![Python](https://img.shields.io/badge/Python-3.8%2B-blue?style=for-the-badge&logo=python&logoColor=white)
![OpenCV](https://img.shields.io/badge/OpenCV-4.5-green?style=for-the-badge&logo=opencv&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)

</div>

<details>
  <summary>Table of Contents</summary>
  <ol>
    <li><a href="#about-the-project">About The Project</a></li>
    <li><a href="#technical-logic">Technical Logic</a></li>
    <li><a href="#installation">Installation</a></li>
    <li><a href="#usage-guide">Usage Guide</a></li>
    <li><a href="#ai-transparency">AI Transparency</a></li>
    <li><a href="#license">License</a></li>
    <li><a href="#author">Author</a></li>
  </ol>
</details>

##  About The Project

**SentryApp 3.2** is a modular computer vision dashboard built with Python. It serves as a central interface for experimenting with different surveillance and tracking algorithms, combining motion detection, QR handling, and optical flow mapping into a single **Tkinter** GUI.

Unlike standard recording software, SentryApp analyzes pixel data in real-time to trigger events—whether that's detecting an intruder, logging a QR code, or mapping the trajectory of an object.

---

##  Technical Logic & Code Explanations

The application runs on a main event loop powered by Tkinter and OpenCV. Here is the breakdown of the specific algorithms used:

### 1. Motion Detection (Background Subtraction)
The security mode operates by comparing the current frame against a static background model.
* **Preprocessing:** We convert the frame to grayscale and apply a Gaussian Blur. This removes sensor noise (grain) that would otherwise trigger false positives.
* **Difference Calculation:** We use `cv2.absdiff` to compare the current frame against the saved background frame.
* **Thresholding:** We create a binary mask where changes smaller than 25 are ignored (black) and changes larger are highlighted (white). If the contour area > 600px, it is flagged as "Motion."

### 2. Vector Mapping (Lucas-Kanade Flow)
This mode visualizes movement direction using sparse optical flow.
* **Feature Detection:** We identify "good features" (corners) to track using Shi-Tomasi parameters (`cv2.goodFeaturesToTrack`).
* **Flow Calculation:** We use the Lucas-Kanade pyramid method (`cv2.calcOpticalFlowPyrLK`) to calculate displacement vectors.
* **Visualization:** The mean vector is plotted onto a secondary "Internal Map" canvas.

### 3. Object Tracking (KCF)
For continuous target locking, the app implements the **Kernelized Correlation Filters (KCF)** tracker. This allows the system to maintain a lock on a specific object even if it stops moving or other movement occurs in the background.

---

##  Installation

To run SentryApp, you need a standard Python 3 environment.

1. **Clone the repo**
   ```bash
   git clone [https://github.com/DavidIZ-rob/SENTRYAPP_3.2.git](https://github.com/DavidIZ-rob/SENTRYAPP_3.2.git)

2.**Install Python packages**
```bash
pip install opencv-python opencv-contrib-python numpy pillow
```
---

## Usage Guide
Run the application by executing the main script:
```bash
     python SentryAPP.py
```


### Controls

* MOTION: Switches to Motion Detection mode.
* QR SCAN: Point at a QR code to auto-launch URLs.
* VECTOR MAP: Switches to Optical Flow mode.
* SET TRACKER: Freeze frame, draw a box, and press ENTER to track.

## AI Transparency

### In accordance with development transparency, Artificial Intelligence was used for:

* Refactoring: Correcting the early motion detection scaffolding.
* Debugging: Assisting with OpenCV/Tkinter integration issues.

## Author
## ZAHALEANU IOAN DAVID

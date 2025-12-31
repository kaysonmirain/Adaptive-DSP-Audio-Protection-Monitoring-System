# Adaptive DSP Audio Protection & Monitoring System

**Project Background**
This repository contains the technical implementation of a specialized headset system designed for construction site staff. This project was developed for **Unhack 2024**, a hackathon held by the **Lassonde School of Engineering at York University**. It represents the functional software core of a proposed smart PPE (Personal Protective Equipment) solution aimed at protecting worker hearing while maintaining site-wide communication.

**Core Technical Features**
**Dynamic OSHA Dose Tracking:** The system performs real-time calculations of daily "Noise Dose" percentages based on OSHA's regulatory standards to prevent long-term hearing loss.
**Acoustic Zone Management:** It automatically adjusts audio suppression levels based on ambient noise: **Transparency Mode** for quiet environments under 70 dB, **Active Reduction** for standard site noise between 70-85 dB, and **Critical Protection** for hazardous levels exceeding 85 dB.
**Intelligent Voice Uplink:** The software monitors microphone input and automatically triggers a low-latency UDP audio stream when it detects human speech above a specific amplitude threshold.
**Safety Limiter:** A mandatory safety cap is applied to all processed audio, ensuring ear output never exceeds a 0.25 amplitude threshold to prevent digital acoustic shock.

**Technical Specifications**
**Processing Engine:** Built with Python 3.x using `numpy` and `noisereduce` for real-time digital signal processing.
**Audio Standards:** Operates at a 16,000Hz sample rate with a block size of 2048 for a balance between low latency and processing accuracy.
**Networking:** Implements UDP socket programming for high-speed voice transmission across local site networks.
**Interface:** Features a high-performance command-line interface (CLI) powered by `colorama` for real-time safety monitoring and signal visualization.

**Installation & Usage**
1. Clone this repository to your local machine.
2. Install dependencies using `pip install -r requirements.txt`.
3. Run the application with `python main.py`.
*Note: Ensure your microphone and headphones are connected before starting the session.*

**Academic Acknowledgement**
This implementation was built as part of the technical challenge for **Unhack 2024** at **York University**. The project focuses on solving real-world safety challenges in the construction industry through engineering and software innovation.

---
**Disclaimer:** This software is a technical prototype developed for a hackathon. It is not a substitute for certified hearing protection in industrial environments.

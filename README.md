🎹 MIDI-AR-VR: The Virtual Gesture Piano
A high-performance, real-time MIDI synthesizer that transforms hand gestures into musical notes using computer vision and a professional-grade data engineering architecture. This project enables a 10-finger "virtual piano" experience by mapping hand landmarks to MIDI events through a distributed message broker.

🚀 Project Overview
This application uses MediaPipe to capture hand landmarks and converts them into 10-finger bitmasks. These events are streamed via Apache Kafka (running in Docker) to a logic engine that manages musical state, modifiers (like sharps and flats), and octave control before outputting to a MIDI device.

🛠️ Current State (v0.9.0-beta)
The following core components have been implemented:

Real-Time Vision Producer: Utilizes OpenCV and MediaPipe to track 21 hand landmarks and generate 5-bit hand masks for high-speed gesture recognition.

Decoupled Kafka Pipeline: A containerized Kafka and Zookeeper environment handles the high-frequency data stream, ensuring the audio engine remains responsive even if video processing frames fluctuate.

10-Finger MIDI Logic:

7-Key Mapping: Fingers are mapped to a standard 7-note scale (C, D, E, F, G, A, B).

Thumb Modifiers: The Right Thumb acts as a "Sharp" toggle, shifting notes in real-time.

Octave Scrolling: The Right Pinky tracks vertical movement to dynamically shift the playing octave up or down.

State-Managed Consumer: A MIDI consumer that prevents note duplication by tracking active notes and triggering note_on and note_off events only when gestures change.

Unified Orchestration: A main.py entry point designed to launch both the Vision Producer and MIDI Consumer simultaneously.

📋 Prerequisites
Docker & Docker Compose: For running the Kafka/Zookeeper cluster.

Python 3.10+: Recommended environment (e.g., Anaconda).

DAW: A MIDI-enabled Digital Audio Workstation (e.g., GarageBand, Ableton Live, Logic Pro).

Virtual MIDI: macOS IAC Driver enabled.

⚙️ Installation & Setup
Clone the Repository:

Bash
git clone https://github.com/ManavvPatel/MIDI-AR-VR.git
cd MIDI-AR-VR
Start Infrastructure:

Bash
docker-compose up -d
Install Dependencies:

Bash
pip install opencv-python mediapipe mido kafka-python python-rtmidi
Run Application:

Bash
python main.py
🛣️ Roadmap & Next Improvements
Velocity Sensitivity: Detect downward finger speed to map "strike" velocity to MIDI volume.

Complex Event Processing (CEP): Integrate Apache Flink to handle gesture smoothing and complex chord detection.

Data Analytics Persistence: Create a Kafka Connect sink to dump performance data into Apache Hive for historical "finger-flow" analysis.

Web Dashboard: A real-time UI showing current bitmasks, active notes, and Kafka throughput.

Multi-Instrument Support: Use the Left Thumb as a "Mode Switch" to swap between Piano and Drum kits.

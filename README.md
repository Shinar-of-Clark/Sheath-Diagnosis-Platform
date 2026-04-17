# ⚡ Sheath Diagnosis Platform

An advanced analysis and AI-driven expert diagnostic system for cable sheath circulating currents, based on electromagnetic induction principles and cutting-edge physical phenomena.
Built with Python and Dash, the system extracts core features (RMS, DC bias, harmonic amplitudes and phases) from raw waveforms. Combined with an AI expert diagnostic matrix, it automatically identifies up to 18 types of underlying faults.

## ✨ Features

- **🔌 Multi-dimensional Signal Processing**: Supports DC bias removal, Butterworth low-pass filtering, IIR comb filtering, and Exponential Moving Average (EMA).
- **📊 Golden Cycle Synthesis**: Automatically intercepts steady-state data to synthesize a "Golden Cycle" for high-precision Fourier analysis.
- **🧠 AI Expert Fingerprint Diagnosis**: Features a built-in diagnostic matrix to accurately identify faults such as sheath open circuits, link box water ingress, and multi-point grounding.
- **🛠️ Fault Waveform Generator**: Includes a built-in script (`gen_diagnostic_data.py`) and a web-based generator to simulate various complex interference waveforms with a single click.
- **📦 Out-of-the-Box Deployment**: Provides a standalone executable file, allowing rapid deployment on a VPS without configuring a Python environment.

## 🚀 Quick Start

### Run Standalone Executable on VPS (No Environment Configuration Required)

If you have obtained the packaged standalone executable, you can run it directly on your VPS server **without installing Python or any dependencies**:

```bash
# 1. Upload the standalone executable (e.g., diagnosis_app) to your VPS server

# 2. Grant execution permissions (Linux environment)
chmod +x diagnosis_app

# 3. Start in foreground for testing (defaults to port 8051)
./diagnosis_app

# 4. Run as a background daemon for production (recommended, keeps running after SSH disconnect)
nohup ./diagnosis_app > runtime.log 2>&1 &
```
from website : `http://<your IP>:8051`



### Option 2: Run with Docker

Ensure that Docker is installed on your machine.

```bash
# Build the image (use --progress=plain to monitor the compilation of underlying C/C++ dependencies in real-time, avoiding false freezing illusions)
docker build --progress=plain -t sheath-diagnosis-app .

# Run the container (mapping to host port 8051)
docker run -d -p 8051:8000 sheath-diagnosis-app
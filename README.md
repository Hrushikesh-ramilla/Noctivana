Here’s a well-structured folder tree and documentation-style overview based on your VS Code screenshot and details:

---

# 👶 Noctivana: Real-time Infant Monitoring System

Noctivana is a real-time infant monitoring system designed for Raspberry Pi. It combines deep learning-based audio analysis and computer vision to monitor a baby's safety and comfort in real-time.

---

## 🚀 Features

- 🔊 **Cry Detection**  
  Classifies audio into: Crying, Silence, Laugh, and Noise using a CNN-BiLSTM-Attention model trained on MFCC and spectrogram features.

- 🎥 **Video Monitoring**  
  Detects:
  - Sleep vs Awake (EAR-based with MediaPipe)
  - Face Covered / Face Down
  - Body Uncovered
  - Camera Obstruction (WIP)

- 🧠 **Optimized for Edge**  
  - Lightweight TorchScript model (`cry_model_torchscript.pt`)
  - Fast webcam and mic inference
  - Modular, plug-and-play design

---

## 🗂️ Project Structure

```
NOCTIVANA/
├── 301 - Crying baby/                   # Labeled cry audio samples
├── 901 - Silence/                      # Silence audio samples
├── 902 - Noise/                        # Ambient noise samples
├── 903 - Baby laugh/                   # Laughter audio samples
├── data/                               # Preprocessed data (chunked audio)
├── features/                           # Extracted MFCC and spectrogram features
│
├── alone_again_01.wav                 # Test audio file
├── example.wav                        # Sample for cry detection
├── audio_cry_detect.py                # Real-time cry detection script
├── cry_model.pth                      # Trained PyTorch model
├── cry_model_torchscript.pt           # Optimized TorchScript model for Raspberry Pi
├── dataset.py                         # Loads features and labels for training
├── extract_features.py                # Extracts spectrogram and MFCC features
├── focal_loss.py                      # Custom Focal Loss for imbalanced training
├── model.py                           # CNN-BiLSTM-Attention cry classifier
├── train.py                           # Model training and evaluation pipeline
├── main.py                            # Unified launcher for real-time monitoring
├── preprocess_data.py                 # Preprocesses and chunks raw audio files
├── shape_predictor_68_face_landmarks.dat # Dlib shape predictor for face mesh
├── video_monitor.py                   # Webcam-based infant posture and face monitoring
│
├── *.jpg / *.png / *.avif             # Sample images for detection (awake, asleep, face covered, etc.)
├── Untitled-1.ipynb                   # Temporary/experimental notebook
├── tempCodeRunnerFile.py              # Temp file from VS Code
```

---

## 📁 Key Files Explained

| File | Description |
|------|-------------|
| `dataset.py` | Defines the `CryDataset` class to load and return (feature, label) pairs from a CSV. Converts .npy feature files into PyTorch tensors. |
| `focal_loss.py` | Implements Focal Loss to handle class imbalance by focusing on hard samples. Improves cry detection for underrepresented classes. |
| `main.py` | Launches the entire system: audio-based cry detection and video-based monitoring using multithreading. |
| `model.py` | Defines `CryClassifier`: CNN + BiLSTM + Attention to capture spatial-temporal features from audio spectrograms. |
| `train.py` | Trains the cry detection model, saves checkpoints, evaluates metrics, and plots confusion matrix. |
| `video_monitor.py` | Uses webcam to monitor infant's sleep status, facial visibility, and posture using MediaPipe + Dlib. Integrates with audio cry detection alerts. |
| `preprocess_data.py` | Converts audio files to WAV, splits into 3-second chunks, and organizes them by label. |
| `extract_features.py` | Extracts mel-spectrogram and delta features from WAV audio files. Saves as .npy files and metadata CSV for training. |

---

## ⚙️ Installation

```bash
git clone https://github.com/Hrushikesh-ramilla/Noctivana.git
cd Noctivana
pip install -r requirements.txt
```

**Hardware Required:**
- Raspberry Pi 5 (or compatible PC)
- USB Microphone
- USB Webcam

---

## 🚦 Run the System

**Cry Detection (Audio):**
```bash
python audio_cry_detect.py
```

**Video Monitoring (Camera):**
```bash
python video_monitor.py
```

**Unified Monitoring:**
```bash
python main.py
```

---

## 📊 Performance

| Task                        | Accuracy |
|-----------------------------|----------|
| Cry Detection               | 90%      |
| Sleep/Awake Detection       | 95%      |
| Face Covered/Face Down      | 98%      |
| Body Uncovered              | 85%      |
| Camera Obstructed (WIP)     | 100%     |

---

## 📬 Contact

📧 Email: ramillahrushikesh@gmail.com  
🤝 Maintainer: Hrushikesh Ramilla

---

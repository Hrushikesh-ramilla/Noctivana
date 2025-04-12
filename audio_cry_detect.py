import torch
import torchaudio
import numpy as np
import sounddevice as sd
from model import CryClassifier
import queue
import threading

crying = False
q = queue.Queue()

# Load model
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = CryClassifier().to(device)
model.load_state_dict(torch.load("cry_model.pth", map_location=device))
model.eval()

def preprocess_audio(audio, sr):
    waveform = torch.tensor(audio).float().unsqueeze(0)
    mel_spec = torchaudio.transforms.MelSpectrogram(sample_rate=sr, n_mels=128)(waveform)
    mel_spec = torchaudio.transforms.AmplitudeToDB()(mel_spec)
    mel_spec = mel_spec[:, :, :128]
    mel_spec = mel_spec.unsqueeze(0).repeat(1, 3, 1, 1)  # (1, 3, 128, 128)
    return mel_spec.to(device)

def audio_callback(indata, frames, time, status):
    if status:
        print(status)
    q.put(indata.copy())

def detect_cry():
    global crying
    samplerate = 16000
    duration = 2
    with sd.InputStream(channels=1, callback=audio_callback, samplerate=samplerate, blocksize=int(samplerate * duration)):
        while True:
            audio = q.get()
            if audio.shape[0] < samplerate * duration:
                continue
            audio = audio.flatten()
            features = preprocess_audio(audio, samplerate)
            with torch.no_grad():
                pred = model(features)
                crying = pred.item() > 0.5
# Add this at the bottom of audio_cry_detect.py

def is_crying():
    return crying


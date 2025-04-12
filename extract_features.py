import os
import numpy as np
import librosa
import pandas as pd
from tqdm import tqdm

INPUT_DIR = "data"
OUTPUT_DIR = "features"
SAMPLE_RATE = 16000
N_MELS = 128

os.makedirs(OUTPUT_DIR, exist_ok=True)
metadata = []

def extract_features(file_path):
    y, sr = librosa.load(file_path, sr=SAMPLE_RATE, mono=True)
    mel_spec = librosa.feature.melspectrogram(y=y, sr=sr, n_mels=N_MELS)
    log_mel = librosa.power_to_db(mel_spec, ref=np.max)
    delta = librosa.feature.delta(log_mel)
    delta2 = librosa.feature.delta(log_mel, order=2)
    feature_stack = np.stack([log_mel, delta, delta2], axis=0)  # shape: (3, 128, T)
    return feature_stack


def process_folder(folder, label):
    files = [f for f in os.listdir(folder) if f.endswith(".wav")]
    for f in tqdm(files, desc=f"Extracting from {folder}"):
        file_path = os.path.join(folder, f)
        features = extract_features(file_path)
        out_name = f.replace(".wav", ".npy")
        out_path = os.path.join(OUTPUT_DIR, out_name)
        np.save(out_path, features)
        metadata.append({"path": out_path, "label": label})

def main():
    process_folder(os.path.join(INPUT_DIR, "crying"), 1)
    process_folder(os.path.join(INPUT_DIR, "not_crying"), 0)
    pd.DataFrame(metadata).to_csv(os.path.join(OUTPUT_DIR, "metadata.csv"), index=False)

if __name__ == "__main__":
    main()

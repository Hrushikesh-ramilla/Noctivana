import os
from pydub import AudioSegment
import librosa
import soundfile as sf
from tqdm import tqdm

SOURCE_DIRS = {
    "301 - Crying baby": 1,
    "901 - Silence": 0,
    "902 - Noise": 0,
    "903 - Baby laugh": 0,
}
OUTPUT_DIR = "data"
SAMPLE_RATE = 16000
CHUNK_DURATION = 3  # seconds

os.makedirs(f"{OUTPUT_DIR}/crying", exist_ok=True)
os.makedirs(f"{OUTPUT_DIR}/not_crying", exist_ok=True)

def convert_to_wav(src_path):
    if src_path.endswith(".wav"):
        return src_path
    audio = AudioSegment.from_file(src_path)
    wav_path = src_path.rsplit(".", 1)[0] + ".wav"
    audio.export(wav_path, format="wav")
    return wav_path

def process_file(file_path, label, output_count):
    wav_path = convert_to_wav(file_path)
    y, sr = librosa.load(wav_path, sr=SAMPLE_RATE, mono=True)
    total_duration = librosa.get_duration(y=y, sr=sr)
    num_chunks = int(total_duration // CHUNK_DURATION)

    for i in range(num_chunks):
        start_sample = int(i * CHUNK_DURATION * sr)
        end_sample = int((i + 1) * CHUNK_DURATION * sr)
        chunk = y[start_sample:end_sample]

        class_folder = "crying" if label == 1 else "not_crying"
        chunk_path = os.path.join(OUTPUT_DIR, class_folder, f"{class_folder}_{output_count}.wav")
        sf.write(chunk_path, chunk, sr)
        output_count += 1

    return output_count

def preprocess_all():
    output_count = 0
    for folder, label in SOURCE_DIRS.items():
        folder_path = os.path.join(".", folder)
        files = [f for f in os.listdir(folder_path) if f.endswith((".ogg", ".wav"))]
        for f in tqdm(files, desc=f"Processing {folder}"):
            full_path = os.path.join(folder_path, f)
            output_count = process_file(full_path, label, output_count)

if __name__ == "__main__":
    preprocess_all()

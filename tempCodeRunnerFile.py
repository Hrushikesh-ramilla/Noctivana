import threading
from video_monitor import run_webcam_monitoring
from audio_cry_detect import detect_cry

if __name__ == "__main__":
    t1 = threading.Thread(target=run_webcam_monitoring)
    t2 = threading.Thread(target=detect_cry)

    t1.start()
    t2.start()

    t1.join()
    t2.join()

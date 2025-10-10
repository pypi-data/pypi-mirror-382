import os, urllib.request, zipfile, sounddevice as sd

MODEL_URL = "https://alphacephei.com/vosk/models/vosk-model-en-in-0.5.zip"
MODEL_DIR = os.path.join(os.path.dirname(__file__), "model")
MODEL_PATH = os.path.join(MODEL_DIR, "vosk-model-en-in-0.5")


def ensure_model():
    """Download and extract Vosk model if not already present."""
    if os.path.exists(MODEL_PATH):
        print("✅ Vosk model found.")
        return MODEL_PATH

    print("📦 Downloading Vosk model (≈120 MB)...")
    os.makedirs(MODEL_DIR, exist_ok=True)
    zip_path = os.path.join(MODEL_DIR, "vosk-model.zip")
    urllib.request.urlretrieve(MODEL_URL, zip_path)

    print("📂 Extracting model...")
    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extractall(MODEL_DIR)
    os.remove(zip_path)

    print("✅ Model ready at:", MODEL_PATH)
    return MODEL_PATH


def auto_input_device():
    """Auto-detect and set the first available microphone."""
    devices = sd.query_devices()
    for i, d in enumerate(devices):
        if d["max_input_channels"] > 0:
            print(f"🎧 Using mic: {d['name']} (device #{i})")
            sd.default.device = i
            return
    raise RuntimeError("⚠️ No input device found!")

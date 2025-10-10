import os, zipfile, requests, sounddevice as sd, tkinter as tk, threading
from tqdm import tqdm

# ----------------------------
#  MODEL DOWNLOAD SETTINGS
# ----------------------------
MODEL_URL = "https://alphacephei.com/vosk/models/vosk-model-en-in-0.5.zip"
BASE_DIR = os.path.join(os.path.expanduser("~"), "AppData", "Local", "lumivox", "models")
MODEL_FOLDER = os.path.join(BASE_DIR, "vosk-model-en-in-0.5")
ZIP_PATH = os.path.join(BASE_DIR, "vosk-model-en-in-0.5.zip")


# ----------------------------
#  AUTO MICROPHONE DETECTION
# ----------------------------
def auto_input_device():
    """Automatically select an available input (microphone) device."""
    try:
        devices = sd.query_devices()
        input_devices = [d for d in devices if d["max_input_channels"] > 0]

        if not input_devices:
            print("⚠️ No microphone input devices detected.")
            return

        sd.default.device = input_devices[0]["name"]
        print(f"[mic] 🎙️ Using: {input_devices[0]['name']}")
    except Exception as e:
        print(f"[mic] ⚠️ Could not set input device: {e}")


# ----------------------------
#  MODEL ENSURE + PROGRESS POPUP
# ----------------------------
def ensure_model():
    """Ensures the Vosk model is downloaded, extracted, and ready with progress + popup."""
    os.makedirs(BASE_DIR, exist_ok=True)

    if os.path.exists(MODEL_FOLDER):
        print("✅ Using cached model: vosk-model-en-in-0.5")
        return MODEL_FOLDER

    # ---------- Transparent Popup ----------
    popup = tk.Tk()
    popup.title("Downloading Lumivox Model")
    popup.geometry("460x160+480+280")
    popup.configure(bg="#000000")
    popup.attributes("-alpha", 0.92)
    popup.resizable(False, False)

    label = tk.Label(
        popup,
        text="🎤 Downloading Vosk Indian-English model (~1 GB)\nThis happens only once...",
        fg="white", bg="black",
        font=("Consolas", 11, "italic")
    )
    label.pack(expand=True)

    progress_var = tk.StringVar(value="0%")
    progress_label = tk.Label(popup, textvariable=progress_var, fg="#00ff88", bg="black", font=("Consolas", 10))
    progress_label.pack(pady=10)

    popup.update()

    # ---------- Background Download Thread ----------
    def download_model():
        print("⬇️ Downloading model...")
        r = requests.get(MODEL_URL, stream=True)
        total = int(r.headers.get("content-length", 0))

        with open(ZIP_PATH, "wb") as f, tqdm(
            desc="Downloading", total=total, unit="B", unit_scale=True, ncols=70
        ) as bar:
            downloaded = 0
            for chunk in r.iter_content(chunk_size=1024 * 1024):
                if chunk:
                    f.write(chunk)
                    bar.update(len(chunk))
                    downloaded += len(chunk)
                    percent = (downloaded / total) * 100
                    progress_var.set(f"{percent:.1f}%")
                    popup.update()

        print("📦 Extracting model...")
        label.config(text="📦 Extracting model, please wait...")
        popup.update()

        with zipfile.ZipFile(ZIP_PATH, "r") as zip_ref:
            zip_ref.extractall(BASE_DIR)

        os.remove(ZIP_PATH)
        label.config(text="✅ Model ready! Starting Lumivox...")
        popup.update()
        popup.after(1500, popup.destroy)

    threading.Thread(target=download_model, daemon=True).start()
    popup.mainloop()

    return MODEL_FOLDER

import os, zipfile, requests, sounddevice as sd, tkinter as tk, threading
from tqdm import tqdm

# ---------------------------------------------------
# 🌐 MODEL SETTINGS
# ---------------------------------------------------
MODEL_URL = "https://alphacephei.com/vosk/models/vosk-model-en-in-0.5.zip"
BASE_DIR = os.path.join(os.path.expanduser("~"), "AppData", "Local", "lumivox", "models")
MODEL_FOLDER = os.path.join(BASE_DIR, "vosk-model-en-in-0.5")
ZIP_PATH = os.path.join(BASE_DIR, "vosk-model-en-in-0.5.zip")


# ---------------------------------------------------
# 🎤 AUTO MICROPHONE DETECTION
# ---------------------------------------------------
def auto_input_device():
    """Automatically selects the first available microphone input device."""
    try:
        devices = sd.query_devices()
        input_devices = [d for d in devices if d["max_input_channels"] > 0]

        if not input_devices:
            print("⚠️ No microphone input devices detected.")
            return

        sd.default.device = input_devices[0]["name"]
        print(f"[mic] 🎙️ Using input device: {input_devices[0]['name']}")

    except Exception as e:
        print(f"[mic] ⚠️ Could not set microphone input: {e}")


# ---------------------------------------------------
# 📦 ENSURE MODEL DOWNLOADED (WITH POPUP + PROGRESS)
# ---------------------------------------------------
def ensure_model():
    """
    Ensures the Vosk model is downloaded and extracted with a transparent popup + safe progress updates.
    """
    os.makedirs(BASE_DIR, exist_ok=True)

    # ✅ Already downloaded
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
    progress_label = tk.Label(
        popup, textvariable=progress_var,
        fg="#00ff88", bg="black", font=("Consolas", 10)
    )
    progress_label.pack(pady=10)

    popup.update()

    # ---------- Background Download Thread ----------
    def download_model():
        try:
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

                        # ✅ GUI-safe update (avoids RuntimeError)
                        popup.after(0, lambda p=f"{percent:.1f}%": progress_var.set(p))

            print("📦 Extracting model...")
            popup.after(0, lambda: label.config(text="📦 Extracting model, please wait..."))

            with zipfile.ZipFile(ZIP_PATH, "r") as zip_ref:
                zip_ref.extractall(BASE_DIR)

            os.remove(ZIP_PATH)
            popup.after(0, lambda: label.config(text="✅ Model ready! Starting Lumivox..."))
            popup.after(1500, popup.destroy)

        except Exception as e:
            print("❌ Download failed:", e)
            popup.after(0, lambda: label.config(text=f"❌ Error: {e}"))

    threading.Thread(target=download_model, daemon=True).start()
    popup.mainloop()

    return MODEL_FOLDER

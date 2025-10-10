import os, zipfile, requests, sounddevice as sd, tkinter as tk, threading, subprocess
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
# ⚡ FAST EXTRACTION FUNCTION
# ---------------------------------------------------
def fast_extract(zip_path, extract_to, popup, label):
    """Extract the model quickly using tar if available, otherwise fallback to zip."""
    try:
        print("⚡ Fast extracting model (1–3 minutes)...")
        popup.after(0, lambda: label.config(text="⚡ Fast extracting model, please wait..."))

        # Try using Windows native extraction (tar)
        subprocess.run(
            ["tar", "-xf", zip_path, "-C", extract_to],
            check=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

        # Check if extraction succeeded, otherwise fallback to zip
        if not os.path.exists(os.path.join(extract_to, "vosk-model-en-in-0.5")):
            print("📦 Falling back to Python extraction...")
            with zipfile.ZipFile(zip_path, "r") as zip_ref:
                total_files = len(zip_ref.infolist())
                for i, member in enumerate(zip_ref.infolist(), 1):
                    zip_ref.extract(member, extract_to)
                    if i % 500 == 0:
                        percent = (i / total_files) * 100
                        popup.after(0, lambda p=f"Extracting... {percent:.1f}%": label.config(text=p))

        popup.after(0, lambda: label.config(text="✅ Model ready! Starting Lumivox..."))
        print("✅ Extraction complete.")
        os.remove(zip_path)

    except Exception as e:
        print("❌ Extraction failed:", e)
        popup.after(0, lambda: label.config(text=f"❌ Extraction error: {e}"))


# ---------------------------------------------------
# 📦 ENSURE MODEL (ONE-TIME DOWNLOAD)
# ---------------------------------------------------
def ensure_model():
    """
    Ensures the Vosk model is downloaded and extracted.
    Skips download if the folder already exists.
    """
    os.makedirs(BASE_DIR, exist_ok=True)

    # ✅ Skip download if already extracted
    if os.path.exists(MODEL_FOLDER):
        print("✅ Model already exists — skipping download.")
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

    # ---------- Download in background ----------
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
                        popup.after(0, lambda p=f"{percent:.1f}%": progress_var.set(p))

            # Extract after download
            popup.after(0, lambda: label.config(text="📦 Extracting model, please wait..."))
            fast_extract(ZIP_PATH, BASE_DIR, popup, label)

            # Close popup after short delay
            popup.after(1500, popup.destroy)

        except Exception as e:
            print("❌ Download failed:", e)
            popup.after(0, lambda: label.config(text=f"❌ Error: {e}"))

    threading.Thread(target=download_model, daemon=True).start()
    popup.mainloop()

    return MODEL_FOLDER

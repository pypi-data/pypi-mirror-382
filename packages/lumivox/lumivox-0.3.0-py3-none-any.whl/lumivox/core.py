import os, io, zipfile, requests, json, queue, sounddevice as sd, tkinter as tk, serial, time
from vosk import Model, KaldiRecognizer

# --------------------- MODEL AUTO-DOWNLOAD ---------------------
def ensure_model(path="model/vosk-model-en-in-0.5"):
    """Automatically download the large Indian-English Vosk model (~1 GB) if not found."""
    if os.path.exists(path):
        return path  # ✅ Already downloaded

    os.makedirs("model", exist_ok=True)
    url = "https://alphacephei.com/vosk/models/vosk-model-en-in-0.5.zip"
    print("📦 Downloading Vosk Indian-English model (~1 GB)... please wait (first time only).")

    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        total = int(r.headers.get("content-length", 0))
        downloaded = 0
        buffer = io.BytesIO()

        for chunk in r.iter_content(chunk_size=1024 * 1024):  # 1 MB chunks
            if chunk:
                buffer.write(chunk)
                downloaded += len(chunk)
                percent = (downloaded / total) * 100
                print(f"\r⬇️  Downloading: {percent:5.1f}%", end="")

        print("\n✅ Download complete. Extracting...")
        with zipfile.ZipFile(io.BytesIO(buffer.getvalue())) as z:
            z.extractall("model")

    print("✅ Model extracted and ready.")
    return path


# --------------------- SERIAL COMMUNICATION ---------------------
def connect_serial(port="COM4", baud=115200, timeout=1.0):
    try:
        ser = serial.Serial(port, baud, timeout=timeout)
        time.sleep(2)
        print(f"[serial] Connected to {port}")
        return ser
    except Exception as e:
        print(f"[serial] ⚠️ Could not open serial port ({e}) — GUI only.")
        return None


def send_to_esp32(esp, color, state):
    if esp:
        r = g = b = 0
        if color == "red": r = 255 if state else 0
        elif color == "green": g = 255 if state else 0
        elif color == "blue": b = 255 if state else 0
        cmd = f"SET {r},{g},{b}\n"
        esp.write(cmd.encode())
        print("[serial] Sent:", cmd.strip())


# --------------------- MODEL + MICROPHONE ---------------------
def load_model():
    path = ensure_model()
    print("🎤 Loading Vosk model...")
    return Model(path)


def start_mic(model):
    return KaldiRecognizer(model, 16000)


def listen_once(rec):
    with sd.RawInputStream(samplerate=16000, blocksize=8000, dtype='int16', channels=1) as s:
        while True:
            data = s.read(8000)[0]
            if rec.AcceptWaveform(data):
                result = json.loads(rec.Result())
                return result.get("text", "").lower()


# --------------------- COMMAND PARSER ---------------------
def parse_command(text):
    text = text.replace("read", "red").replace("reed", "red")
    text = text.replace("blew", "blue").replace("grin", "green")
    for color in ["red", "green", "blue"]:
        if f"turn on {color}" in text or f"on {color}" in text:
            return color, True
        if f"turn off {color}" in text or f"off {color}" in text:
            return color, False
    return None, None


# --------------------- GUI SYSTEM ---------------------
def start_led_gui():
    win = tk.Tk(); win.title("💡 Lumivox"); win.geometry("520x300")
    c = tk.Canvas(win, width=520, height=300, bg="black"); c.pack()
    c.create_rectangle(0, 0, 260, 300, fill="#0077ff", outline="")
    c.create_rectangle(260, 0, 520, 300, fill="#00cc66", outline="")
    leds = {x: c.create_arc(i, 110, i+80, 190, start=0, extent=180,
                            fill="#111", outline=x, width=3)
            for i, x in zip([60, 220, 380], ["red", "green", "blue"])}
    c.create_text(260, 50, text="Say: 'turn on red', 'turn off blue'", fill="white",
                  font=("Consolas", 10, "italic"))
    win.bind("<Escape>", lambda e: win.destroy())
    return {"root": win, "canvas": c, "leds": leds}


def update_led(gui, color, state):
    c = gui["canvas"]; leds = gui["leds"]
    c.itemconfig(leds[color], fill=color if state else "#111")
    gui["root"].update()


def check_exit(gui):
    return not bool(gui["root"].winfo_exists())


def cleanup(gui):
    try:
        gui["root"].destroy()
    except:
        pass

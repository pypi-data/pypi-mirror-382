import json, queue, sounddevice as sd, tkinter as tk, serial, time, numpy as np
from vosk import Model, KaldiRecognizer
from .utils import ensure_model, auto_input_device


# ---------- Serial ----------
def connect_serial(port="COM4", baudrate=115200, timeout=1):
    """Try to connect to ESP32 via serial."""
    try:
        ser = serial.Serial(port, baudrate, timeout=timeout)
        time.sleep(2)
        print(f"[serial] Connected to {port}")
        return ser
    except Exception as e:
        print(f"[serial] ⚠️ Could not open serial port ({e}) — GUI-only mode.")
        return None


def send_to_esp32(ser, color, state):
    """Send RGB command to ESP32."""
    if ser:
        try:
            r, g, b = (255, 0, 0) if color == "red" else (0, 255, 0) if color == "green" else (0, 0, 255)
            if not state:
                r = g = b = 0
            cmd = f"SET {r},{g},{b}\n"
            ser.write(cmd.encode())
            print("[serial] Sent:", cmd.strip())
        except Exception as e:
            print("[serial] Error:", e)


# ---------- GUI ----------
class LED_GUI:
    """Animated LED GUI using tkinter."""

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🎤 Lumivox - Voice Controlled LED")
        self.root.geometry("520x300")
        self.root.configure(bg="black")
        self.root.resizable(False, False)

        self.canvas = tk.Canvas(self.root, width=520, height=300, highlightthickness=0)
        self.canvas.pack()

        self.canvas.create_rectangle(0, 0, 260, 300, fill="#0077ff", outline="")
        self.canvas.create_rectangle(260, 0, 520, 300, fill="#00cc66", outline="")

        self.root.bind("<Escape>", lambda e: self.safe_exit())

        self.positions = {"red": 110, "green": 260, "blue": 410}
        self.led_shapes = {}
        self.glow = {"red": 0, "green": 0, "blue": 0}
        self.target = {"red": 0, "green": 0, "blue": 0}

        for color, x in self.positions.items():
            self.led_shapes[color] = self.draw_led(x, 110, color)

        self.status = self.canvas.create_text(
            260, 260, text="Say: 'turn on red', 'turn off blue'", fill="white",
            font=("Consolas", 11, "italic")
        )

        self.running = True
        self.animate()

    def draw_led(self, x, y, color):
        led = {}
        led["body"] = self.canvas.create_arc(x - 25, y - 25, x + 25, y + 25,
                                             start=0, extent=180, fill="#111", outline=color, width=3)
        led["leg1"] = self.canvas.create_line(x - 10, y + 25, x - 10, y + 55, fill="#888", width=3)
        led["leg2"] = self.canvas.create_line(x + 10, y + 25, x + 10, y + 55, fill="#888", width=3)
        led["rays"] = [self.canvas.create_line(x - 35, y - 30, x - 50, y - 50, fill=""),
                       self.canvas.create_line(x, y - 35, x, y - 55, fill=""),
                       self.canvas.create_line(x + 35, y - 30, x + 50, y - 50, fill="")]
        return led

    def update_led(self, color, state):
        self.target[color] = 1 if state else 0

    def animate(self):
        for color, led in self.led_shapes.items():
            current, target = self.glow[color], self.target[color]
            new = current + (target - current) * 0.1
            self.glow[color] = new
            b = int(50 + 205 * new)
            color_code = {
                "red": f"#{b:02x}0000",
                "green": f"#00{b:02x}00",
                "blue": f"#0000{b:02x}"
            }[color]
            self.canvas.itemconfig(led["body"], fill=color_code)
            ray_color = color_code if new > 0.2 else ""
            for ray in led["rays"]:
                self.canvas.itemconfig(ray, fill=ray_color)

        if self.running:
            self.root.after(80, self.animate)

    def set_status(self, text):
        self.canvas.itemconfig(self.status, text=text)

    def safe_exit(self):
        self.running = False
        self.root.destroy()
        print("🛑 ESC pressed — Exiting safely.")

    def run(self):
        self.root.mainloop()


# ---------- VOICE ----------
def load_model():
    """Ensure and load Vosk model."""
    model_path = ensure_model()
    print("🎤 Loading Vosk model...")
    return Model(model_path)


def start_mic(model):
    """
    Start microphone with automatic fallback and buffer safety.
    """
    rec = KaldiRecognizer(model, 16000)
    rec.SetWords(True)
    q = queue.Queue()

    def callback(indata, frames, time_info, status):
        try:
            if hasattr(indata, "tobytes"):
                data = indata.tobytes()
            else:
                data = np.array(indata).astype(np.int16).tobytes()
            q.put(data)
        except Exception as e:
            print(f"[mic] ⚠️ Audio callback error: {e}")

    # Try default mic first
    try:
        auto_input_device()
        stream = sd.RawInputStream(
            samplerate=16000, blocksize=8000, dtype="int16",
            channels=1, callback=callback
        )
        stream.start()
        print("[mic] 🎧 Microphone stream started.")
        return rec, q

    except Exception as e:
        print(f"[mic] ⚠️ Mic failed: {e}")
        print("[mic] 🔁 Trying next available device...")

        try:
            devices = sd.query_devices()
            for d in devices:
                if d["max_input_channels"] > 0:
                    print(f"[mic] Switching to {d['name']}")
                    sd.default.device = d["name"]
                    stream = sd.RawInputStream(
                        samplerate=16000, blocksize=8000, dtype="int16",
                        channels=1, callback=callback
                    )
                    stream.start()
                    print("[mic] ✅ Fallback mic stream started.")
                    return rec, q
            print("[mic] ❌ No available input devices found.")
        except Exception as e2:
            print(f"[mic] ❌ All microphone attempts failed: {e2}")
            return rec, None


def listen_once(mic_data):
    """Process one chunk of audio and return recognized text."""
    if mic_data is None:
        return ""
    rec, q = mic_data
    try:
        data = q.get()
        if rec.AcceptWaveform(data):
            result = json.loads(rec.Result())
            return result.get("text", "")
    except Exception as e:
        print(f"[mic] ⚠️ Listening error: {e}")
    return ""


# ---------- COMMAND PARSER ----------
def parse_command(text):
    text = text.replace("reed", "red").replace("blew", "blue").replace("grin", "green")
    for color in ["red", "green", "blue"]:
        if f"turn on {color}" in text or f"on {color}" in text:
            return color, True
        if f"turn off {color}" in text or f"off {color}" in text:
            return color, False
    return None, None


# ---------- HELPER ----------
def check_exit(gui):
    return not gui.running


def cleanup(gui):
    gui.safe_exit()

import tkinter as tk
from tkinter import filedialog
import speech_recognition as sr
import pywhatkit, json, pyttsx3
import datetime, os, threading, psutil, wikipedia, math, pyautogui, webbrowser, time, random
import screen_brightness_control as sbc
import google.generativeai as genai

# --- 1. IDENTITY & BRAIN SETUP ---
THEME_CYAN = "#00FFD1"
DANGER_RED = "#FF4C4C"
BG_BLACK = "#000000"

try:
    genai.configure(api_key="AIzaSyDPstl0vX50mqWzjADRSLm9DEMF2ENBcaY")
    model = genai.GenerativeModel('gemini-1.5-flash')
    api_ready = True
except: api_ready = False

# --- 2. BRIGHTNESS WMI FIX ---
def set_brightness_fixed(level):
    try:
        os.system(f"powershell (Get-WmiObject -Namespace root/WMI -Class WmiMonitorBrightnessMethods).WmiSetBrightness(1, {level})")
        log_msg(f"ROXY: Brightness set to {level}%")
    except:
        if level > 50: pyautogui.hotkey('fn', 'f8')
        else: pyautogui.hotkey('fn', 'f7')

# --- 3. VOICE DRIVER ---
def speak_now(text):
    log_msg(f"ROXY: {text[:60]}...")
    def task():
        try:
            local_engine = pyttsx3.init('sapi5')
            local_engine.setProperty('rate', 175)
            clean_text = str(text).encode('ascii', 'ignore').decode('ascii')
            local_engine.say(clean_text)
            local_engine.runAndWait()
            local_engine.stop()
        except: pass
    threading.Thread(target=task, daemon=True).start()

# --- 4. SMART UTILS ---
def smart_read_task(f_path):
    try:
        content = ""
        if f_path.lower().endswith('.pdf'):
            import PyPDF2
            with open(f_path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                content = " ".join([page.extract_text() for page in reader.pages[:2] if page.extract_text()])
        else:
            with open(f_path, 'r', encoding='utf-8-sig', errors='ignore') as f:
                content = f.read()
        if content.strip():
            log_msg("ROXY: Reading content now...")
            speak_now(content.replace('\n', ' ').strip()[:800])
        else: speak_now("No readable text found.")
    except: speak_now("Error reading file.")

# --- 5. UI CLASS WITH DIGITAL RAIN ---
class RoxySupreme:
    def __init__(self, root):
        self.root = root; self.root.overrideredirect(True)
        self.width, self.height = root.winfo_screenwidth(), root.winfo_screenheight()
        self.root.geometry(f"{self.width}x{self.height}+0+0"); self.root.configure(bg=BG_BLACK)
        self.canvas = tk.Canvas(root, width=self.width, height=self.height, bg=BG_BLACK, highlightthickness=0); self.canvas.pack()
        
        self.is_running = True
        self.rain_drops = []
        self.setup_ui()
        self.animate()

    def setup_ui(self):
        self.cx, self.cy = self.width // 2, self.height // 2
        
        # 1. HIGH DENSITY DIGITAL RAIN (120 drops for darker look)
        for _ in range(120):
            x = random.randint(0, self.width)
            y = random.randint(0, self.height)
            length = random.randint(60, 160)
            line = self.canvas.create_line(x, y, x, y+length, fill="#002525", width=1)
            self.rain_drops.append({'id': line, 'x': x, 'y': y, 'speed': random.randint(6, 18), 'len': length})

        # 2. SYSTEM DIAGNOSTICS (Left Aligned)
        self.canvas.create_rectangle(40, 40, 300, 180, outline=THEME_CYAN, width=1)
        self.canvas.create_text(170, 65, text="SYSTEM DIAGNOSTICS", fill=THEME_CYAN, font=("Orbitron", 10, "bold"))
        self.cpu_text = self.canvas.create_text(170, 105, text="CPU: 0%", fill=THEME_CYAN, font=("Orbitron", 9))
        self.ram_text = self.canvas.create_text(170, 145, text="RAM: 0%", fill=THEME_CYAN, font=("Orbitron", 9))

        # 3. CORE HUD
        self.outer_glow = self.canvas.create_oval(self.cx-180, self.cy-180, self.cx+180, self.cy+180, outline=THEME_CYAN, width=2)
        self.inner_glow = self.canvas.create_oval(self.cx-155, self.cy-155, self.cx+155, self.cy+155, outline=THEME_CYAN, width=5)
        self.canvas.create_text(self.cx, self.cy, text="R.O.X.Y", fill=THEME_CYAN, font=("Orbitron", 42, "bold"))
        self.status_text = self.canvas.create_text(self.cx, self.cy+210, text="[ STANDBY ]", fill=THEME_CYAN, font=("Orbitron", 12))

        # Close Button
        self.btn_close = tk.Button(self.root, text="✕", command=self.safe_exit, bg=BG_BLACK, fg=THEME_CYAN, bd=0, font=("Arial", 20))
        self.canvas.create_window(self.width-40, 40, window=self.btn_close)

    def animate(self):
        if not self.is_running: return
        try:
            for drop in self.rain_drops:
                drop['y'] += drop['speed']
                if drop['y'] > self.height: 
                    drop['y'] = -drop['len']
                    drop['x'] = random.randint(0, self.width)
                self.canvas.coords(drop['id'], drop['x'], drop['y'], drop['x'], drop['y'] + drop['len'])

            pulse = 15 * math.sin(datetime.datetime.now().microsecond / 80000)
            self.canvas.itemconfig(self.inner_glow, width=5 + abs(pulse/3))
            
            cpu = psutil.cpu_percent()
            ram = psutil.virtual_memory().percent
            self.canvas.itemconfig(self.cpu_text, text=f"CPU USAGE: {cpu}%")
            self.canvas.itemconfig(self.ram_text, text=f"RAM USAGE: {ram}%")
            
            # Smoother Rain Animation
            self.root.after(20, self.animate) 
        except: pass

    def safe_exit(self):
        self.is_running = False; self.root.destroy()

# --- 6. COMMAND ENGINE ---
def log_msg(msg):
    log_box.insert(tk.END, f"> {msg}\n"); log_box.see(tk.END)

def process_command():
    app.canvas.itemconfig(app.inner_glow, outline=DANGER_RED)
    app.canvas.itemconfig(app.status_text, text="[ LISTENING... ]", fill=DANGER_RED)
    r = sr.Recognizer()
    r.energy_threshold = 400 
    r.dynamic_energy_threshold = True
    with sr.Microphone() as source:
        try:
            r.adjust_for_ambient_noise(source, duration=1.2)
            audio = r.listen(source, timeout=5, phrase_time_limit=10)
            query = r.recognize_google(audio, language='en-IN').lower()
            log_msg(f"Nawin: {query}")

            if 'play' in query:
                song = query.replace('play','').strip()
                speak_now(f"Sure Nawin, direct-aa play pandren.")
                def yt_task():
                    try:
                        # Direct video play logic
                        pywhatkit.playonyt(song)
                        
                        # Browser open aaga chinna delay
                        time.sleep(5) 
                        
                        # Force Play shortcut
                        pyautogui.press('k') 
                    except: pass
                threading.Thread(target=yt_task, daemon=True).start()
            elif 'volume' in query:
                for _ in range(15): pyautogui.press("volumeup" if "up" in query or "yethu" in query else "volumedown")
                speak_now("Volume Adjusted.")
            elif 'brightness' in query:
                try:
                    curr = sbc.get_brightness()[0]
                    new_level = min(curr + 25, 100) if ('up' in query or 'yethu' in query) else max(curr - 25, 0)
                    set_brightness_fixed(new_level)
                    speak_now(f"Brightness Adjusted.")
                except: set_brightness_fixed(75 if 'up' in query else 25)
            elif 'read' in query:
                speak_now("Select file."); f = filedialog.askopenfilename()
                if f: threading.Thread(target=smart_read_task, args=(f,), daemon=True).start()
            elif 'screenshot' in query:
                pyautogui.screenshot(os.path.join(os.path.expanduser("~"), "Desktop", "ROXY_SC.png"))
                speak_now("Screenshot saved.")
            elif 'message' in query or 'whatsapp' in query:
                try:
                    with open('contacts.json', 'r') as f: contacts = json.load(f)
                    for name, num in contacts.items():
                        if name in query:
                            speak_now(f"What should I say to {name}?")
                            msg_body = r.recognize_google(r.listen(source))
                            threading.Thread(target=lambda: (pywhatkit.sendwhatmsg_instantly(num, msg_body, 15), time.sleep(2), pyautogui.press('enter')), daemon=True).start()
                            speak_now(f"Sending message to {name}"); break
                except: speak_now("Contacts error.")
            elif 'clean' in query: 
                os.system(r'del /q/f/s %TEMP%\*')
                speak_now("System Optimized.")
            elif 'exit' in query: app.safe_exit()
            else:
                if api_ready:
                    res = model.generate_content(f"Respond to Nawin: {query}. ROXY mode."); speak_now(res.text.replace("*", ""))
                else: speak_now(wikipedia.summary(query, sentences=1))
        except: speak_now("I couldn't catch that.")
    if app.is_running:
        app.canvas.itemconfig(app.inner_glow, outline=THEME_CYAN); app.canvas.itemconfig(app.status_text, text="[ STANDBY ]", fill=THEME_CYAN)

# --- 7. EXECUTION SECTION ---
root = tk.Tk(); app = RoxySupreme(root)
log_box = tk.Text(root, height=25, width=45, bg=BG_BLACK, fg=THEME_CYAN, font=("Share Tech Mono", 10), bd=1, relief="flat", highlightbackground="#002F2F", highlightthickness=1)
app.canvas.create_window(app.width - 200, app.cy, window=log_box) 
tk.Button(root, text="ACTIVATE", command=lambda: threading.Thread(target=process_command, daemon=True).start(), bg=THEME_CYAN, font=("Orbitron", 14, "bold"), padx=40, pady=15).place(x=app.cx-100, y=app.height-120)
root.mainloop()

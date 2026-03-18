"""
Miracle Voice Assistant - APK Version
Created by Miracle Gideon
Powered by Google Gemini AI
"""

# ════════════════════════════════════════════════════════════
#  CONFIGURATION — EDIT YOUR API KEY HERE
# ════════════════════════════════════════════════════════════

GOOGLE_API_KEY = "AIzaSyDwHakiYSeWM92eKZMOiPrG6_tEKn_HV6A"
AI_MODEL       = "gemini-2.0-flash"
AI_MAX_TOKENS  = 300
TTS_RATE       = 175
STT_TIMEOUT    = 10
APP_NAME       = "Miracle"
CREATOR        = "Miracle Gideon"
VERSION        = "1.0.0"

# ════════════════════════════════════════════════════════════
#  IMPORTS
# ════════════════════════════════════════════════════════════

import os, re, json, time, random, threading
import subprocess, datetime, urllib.parse
import urllib.request, urllib.error

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.utils import get_color_from_hex

Window.clearcolor = get_color_from_hex("#0D0D1A")

try:
    import speech_recognition as sr
    _SR_OK = True
except ImportError:
    _SR_OK = False

try:
    from gtts import gTTS
    _GTTS_OK = True
except ImportError:
    _GTTS_OK = False


# ════════════════════════════════════════════════════════════
#  TEXT TO SPEECH
# ════════════════════════════════════════════════════════════

class TextToSpeech:

    def __init__(self):
        self._lock   = threading.Lock()
        self.backend = self._detect()

    def _detect(self):
        try:
            subprocess.run(["termux-tts-speak", "--help"],
                           capture_output=True, timeout=3)
            return "termux"
        except Exception:
            pass
        if _GTTS_OK:
            try:
                subprocess.run(["mpg123", "--version"],
                               capture_output=True, timeout=3)
                return "gtts"
            except Exception:
                pass
        return "silent"

    def speak(self, text):
        if not text:
            return
        clean = re.sub(r"[\*\`\#\[\]]", "", text)[:500]
        with self._lock:
            try:
                if self.backend == "termux":
                    subprocess.run(
                        ["termux-tts-speak", "-r", str(TTS_RATE), clean],
                        timeout=30)
                elif self.backend == "gtts":
                    tts = gTTS(text=clean, lang="en", slow=False)
                    tmp = "/tmp/miracle_tts.mp3"
                    tts.save(tmp)
                    subprocess.run(["mpg123", "-q", tmp], timeout=30)
                    os.remove(tmp)
            except Exception:
                pass


# ════════════════════════════════════════════════════════════
#  SPEECH TO TEXT
# ════════════════════════════════════════════════════════════

class SpeechToText:

    def __init__(self):
        self.recognizer = None
        if _SR_OK:
            self.recognizer = sr.Recognizer()
            self.recognizer.energy_threshold         = 300
            self.recognizer.dynamic_energy_threshold = True
            self.recognizer.pause_threshold          = 0.8

    def listen(self):
        if _SR_OK and self.recognizer:
            try:
                with sr.Microphone() as source:
                    self.recognizer.adjust_for_ambient_noise(
                        source, duration=0.5)
                    audio = self.recognizer.listen(
                        source, timeout=STT_TIMEOUT,
                        phrase_time_limit=15)
                return self.recognizer.recognize_google(audio)
            except Exception:
                return None
        try:
            result = subprocess.run(
                ["termux-speech-to-text"],
                capture_output=True, text=True, timeout=15)
            return result.stdout.strip() or None
        except Exception:
            return None


# ════════════════════════════════════════════════════════════
#  APP LAUNCHER
# ════════════════════════════════════════════════════════════

class AppLauncher:

    APPS = {
        "whatsapp":   "com.whatsapp",
        "telegram":   "org.telegram.messenger",
        "instagram":  "com.instagram.android",
        "facebook":   "com.facebook.katana",
        "youtube":    "com.google.android.youtube",
        "chrome":     "com.android.chrome",
        "gmail":      "com.google.android.gm",
        "maps":       "com.google.android.apps.maps",
        "camera":     "com.android.camera2",
        "settings":   "com.android.settings",
        "calculator": "com.google.android.calculator",
        "calendar":   "com.google.android.calendar",
        "clock":      "com.google.android.deskclock",
        "contacts":   "com.android.contacts",
        "messages":   "com.google.android.apps.messaging",
        "spotify":    "com.spotify.music",
        "netflix":    "com.netflix.mediaclient",
        "twitter":    "com.twitter.android",
        "tiktok":     "com.zhiliaoapp.musically",
        "snapchat":   "com.snapchat.android",
        "discord":    "com.discord",
        "zoom":       "us.zoom.videomeetings",
        "files":      "com.google.android.apps.nbu.files",
        "drive":      "com.google.android.apps.docs",
        "photos":     "com.google.android.apps.photos",
        "play store": "com.android.vending",
        "termux":     "com.termux",
    }

    def launch(self, app_name):
        name = app_name.lower().strip()
        pkg  = self.APPS.get(name)
        if not pkg:
            for key, p in self.APPS.items():
                if name in key or key in name:
                    pkg = p
                    break
        if not pkg:
            return f"I don't know how to open '{app_name}'."
        try:
            subprocess.run(
                ["monkey", "-p", pkg, "-c",
                 "android.intent.category.LAUNCHER", "1"],
                capture_output=True, timeout=10)
            return f"Opening {app_name.title()}!"
        except Exception as e:
            return f"Couldn't open {app_name}: {e}"


# ════════════════════════════════════════════════════════════
#  DEVICE CONTROL
# ════════════════════════════════════════════════════════════

class DeviceControl:

    def flashlight(self, on):
        try:
            subprocess.run(["termux-torch", "on" if on else "off"],
                           capture_output=True, timeout=5)
            return f"Flashlight {'on' if on else 'off'}!"
        except Exception as e:
            return f"Flashlight error: {e}"

    def volume(self, action, level=None):
        keycodes = {"up": "24", "down": "25", "mute": "164"}
        try:
            if action in keycodes:
                subprocess.run(["input", "keyevent", keycodes[action]],
                               capture_output=True, timeout=5)
                return {"up": "Volume up!",
                        "down": "Volume down!", "mute": "Muted!"}[action]
        except Exception as e:
            return f"Volume error: {e}"

    def battery_status(self):
        try:
            r = subprocess.run(["termux-battery-status"],
                               capture_output=True, text=True, timeout=10)
            data     = json.loads(r.stdout)
            pct      = data.get("percentage", "?")
            plugged  = data.get("plugged", "UNPLUGGED")
            charging = "charging" if "CHARGING" in plugged.upper() \
                       else "not charging"
            return f"Battery is at {pct}% and {charging}."
        except Exception as e:
            return f"Battery check failed: {e}"

    def set_alarm(self, time_str):
        try:
            m = re.search(r"(\d{1,2})(?::(\d{2}))?\s*(am|pm)?",
                          time_str.lower())
            if m:
                h    = int(m.group(1))
                mins = int(m.group(2)) if m.group(2) else 0
                p    = m.group(3)
                if p == "pm" and h != 12:
                    h += 12
                elif p == "am" and h == 12:
                    h = 0
                subprocess.run(
                    ["am", "start", "-a",
                     "android.intent.action.SET_ALARM",
                     "--ei", "android.intent.extra.alarm.HOUR", str(h),
                     "--ei", "android.intent.extra.alarm.MINUTES", str(mins),
                     "--ez", "android.intent.extra.alarm.SKIP_UI", "true"],
                    capture_output=True, timeout=10)
                return f"Alarm set for {h:02d}:{mins:02d}!"
            return f"Alarm set for {time_str}."
        except Exception as e:
            return f"Alarm error: {e}"


# ════════════════════════════════════════════════════════════
#  WEB SEARCH
# ════════════════════════════════════════════════════════════

class WebSearch:
    def search(self, query):
        url = "https://www.google.com/search?q=" + urllib.parse.quote(query)
        try:
            subprocess.run(
                ["am", "start", "-a",
                 "android.intent.action.VIEW", "-d", url],
                capture_output=True, timeout=10)
            return f"Searching for '{query}'!"
        except Exception as e:
            return f"Search error: {e}"


# ════════════════════════════════════════════════════════════
#  COMMAND PARSER
# ════════════════════════════════════════════════════════════

class CommandParser:

    def __init__(self):
        self.launcher = AppLauncher()
        self.device   = DeviceControl()
        self.web      = WebSearch()

    def parse(self, text):
        t = text.lower().strip()

        m = re.search(
            r"(?:open|launch|start|run|go to) (\w+(?:\s\w+)?)", t)
        if m:
            return {"type": "cmd",
                    "msg": self.launcher.launch(m.group(1))}

        if any(x in t for x in ["torch on", "flashlight on",
                                  "turn on torch", "turn on flashlight"]):
            return {"type": "cmd", "msg": self.device.flashlight(True)}
        if any(x in t for x in ["torch off", "flashlight off",
                                  "turn off torch", "turn off flashlight"]):
            return {"type": "cmd", "msg": self.device.flashlight(False)}

        if any(x in t for x in ["volume up", "louder"]):
            return {"type": "cmd", "msg": self.device.volume("up")}
        if any(x in t for x in ["volume down", "quieter"]):
            return {"type": "cmd", "msg": self.device.volume("down")}
        if "mute" in t:
            return {"type": "cmd", "msg": self.device.volume("mute")}

        if any(x in t for x in ["battery", "check battery"]):
            return {"type": "cmd", "msg": self.device.battery_status()}

        m = re.search(r"set (?:an )?alarm (?:for )?(.+)", t)
        if m:
            return {"type": "cmd",
                    "msg": self.device.set_alarm(m.group(1))}

        m = re.search(
            r"(?:search|google|look up|find) (?:for )?(.+)", t)
        if m:
            return {"type": "cmd", "msg": self.web.search(m.group(1))}

        if any(x in t for x in ["what time", "current time"]):
            now = datetime.datetime.now()
            return {"type": "cmd",
                    "msg": f"It's {now.strftime('%I:%M %p')}."}
        if any(x in t for x in ["what date", "what day"]):
            now = datetime.datetime.now()
            return {"type": "cmd",
                    "msg": f"Today is {now.strftime('%A, %B %d, %Y')}."}

        return {"type": "ai", "msg": None}


# ════════════════════════════════════════════════════════════
#  OFFLINE FALLBACK
# ════════════════════════════════════════════════════════════

class OfflineFallback:

    JOKES = [
        "Why don't scientists trust atoms? They make up everything!",
        "Why did the phone go to school? Better connections!",
    ]
    PATTERNS = [
        (["who are you", "your name"],
         f"I'm {APP_NAME}, your AI assistant by {CREATOR}!"),
        (["who made you", "who created you"],
         f"I was created by {CREATOR}!"),
        (["hello", "hi", "hey"],
         f"Hello! I'm {APP_NAME}. How can I help?"),
        (["bye", "goodbye"],   "Goodbye! Have a great day!"),
        (["thank you", "thanks"], "You're welcome!"),
        (["how are you"],      "I'm great and ready to help!"),
        (["joke"],             None),
    ]

    def respond(self, text):
        t = text.lower()
        for keywords, response in self.PATTERNS:
            if any(k in t for k in keywords):
                if response:
                    return response
                if "joke" in t:
                    return random.choice(self.JOKES)
        return "Sorry, I could not reach the AI. Please try again!"


# ════════════════════════════════════════════════════════════
#  AI BRAIN
# ════════════════════════════════════════════════════════════

class AIBrain:

    SYSTEM = (
        f"You are {APP_NAME}, a helpful AI voice assistant by {CREATOR}. "
        f"Be concise — text is spoken aloud. Max 3 sentences. "
        f"No markdown. Be warm and friendly."
    )
    API_URL = (
        "https://generativelanguage.googleapis.com/v1beta/models/"
        "{model}:generateContent?key={key}"
    )

    def __init__(self):
        self.fallback  = OfflineFallback()
        self.available = bool(GOOGLE_API_KEY)

    def chat(self, message, history=None):
        if self.available:
            for attempt in range(3):
                try:
                    return self._call_gemini(message, history or [])
                except urllib.error.HTTPError as e:
                    if e.code == 429:
                        time.sleep(5)
                        continue
                    break
                except Exception:
                    break
        return self.fallback.respond(message)

    def _call_gemini(self, message, history):
        contents = []
        for h in history[-10:]:
            role    = h.get("role", "")
            content = h.get("content", "")
            if role == "user":
                contents.append({"role": "user",
                                  "parts": [{"text": content}]})
            elif role == "assistant":
                contents.append({"role": "model",
                                  "parts": [{"text": content}]})
        contents.append({"role": "user",
                          "parts": [{"text": message}]})

        body = json.dumps({
            "system_instruction": {"parts": [{"text": self.SYSTEM}]},
            "contents": contents,
            "generationConfig": {
                "maxOutputTokens": AI_MAX_TOKENS,
                "temperature": 0.7
            }
        }).encode("utf-8")

        url = self.API_URL.format(model=AI_MODEL, key=GOOGLE_API_KEY)
        req = urllib.request.Request(
            url, data=body,
            headers={"Content-Type": "application/json"},
            method="POST")

        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        return (data["candidates"][0]["content"]
                    ["parts"][0]["text"].strip())


# ════════════════════════════════════════════════════════════
#  KIVY UI
# ════════════════════════════════════════════════════════════

class MiracleUI(BoxLayout):

    BG      = "#0D0D1A"
    BG2     = "#1A1A2E"
    PURPLE  = "#7B2FFF"
    CYAN    = "#00E5FF"
    GREEN   = "#00FF99"
    RED     = "#FF3366"
    YELLOW  = "#FFCC00"
    WHITE   = "#FFFFFF"
    GRAY    = "#555577"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.padding     = [12, 24, 12, 12]
        self.spacing     = 8

        self.tts       = TextToSpeech()
        self.stt       = SpeechToText()
        self.parser    = CommandParser()
        self.brain     = AIBrain()
        self.history   = []
        self.listening = False

        self._build()
        self._welcome()

    def _build(self):

        # ── Header ──
        hdr = BoxLayout(orientation="horizontal",
                        size_hint_y=None, height=56)
        title = Label(
            text=f"[b]✦ {APP_NAME.upper()}[/b]",
            markup=True, font_size="22sp",
            color=get_color_from_hex(self.WHITE),
            size_hint_x=0.65, halign="left")
        title.bind(size=title.setter("text_size"))

        self.status_lbl = Label(
            text="● Ready", font_size="11sp",
            color=get_color_from_hex(self.CYAN),
            size_hint_x=0.35, halign="right")
        self.status_lbl.bind(size=self.status_lbl.setter("text_size"))

        hdr.add_widget(title)
        hdr.add_widget(self.status_lbl)
        self.add_widget(hdr)

        sub = Label(
            text=f"by {CREATOR}  •  Gemini AI",
            font_size="10sp",
            color=get_color_from_hex(self.GRAY),
            size_hint_y=None, height=16,
            halign="left")
        sub.bind(size=sub.setter("text_size"))
        self.add_widget(sub)

        # ── Chat area ──
        self.scroll = ScrollView(size_hint=(1, 1))
        self.chat   = BoxLayout(
            orientation="vertical",
            size_hint_y=None, spacing=6,
            padding=[0, 8])
        self.chat.bind(minimum_height=self.chat.setter("height"))
        self.scroll.add_widget(self.chat)
        self.add_widget(self.scroll)

        # ── Input row ──
        row = BoxLayout(orientation="horizontal",
                        size_hint_y=None, height=48, spacing=8)
        self.txt = TextInput(
            hint_text="Type here or tap mic...",
            multiline=False, size_hint_x=0.82,
            background_color=get_color_from_hex(self.BG2),
            foreground_color=get_color_from_hex(self.WHITE),
            hint_text_color=get_color_from_hex(self.GRAY),
            cursor_color=get_color_from_hex(self.PURPLE),
            font_size="13sp", padding=[10, 10])
        self.txt.bind(on_text_validate=self._send)

        send = Button(
            text="➤", size_hint_x=0.18, font_size="18sp",
            background_color=get_color_from_hex(self.PURPLE),
            color=get_color_from_hex(self.WHITE))
        send.bind(on_press=self._send)
        row.add_widget(self.txt)
        row.add_widget(send)
        self.add_widget(row)

        # ── Buttons ──
        btns = BoxLayout(orientation="horizontal",
                         size_hint_y=None, height=60, spacing=8)

        self.mic_btn = Button(
            text="🎤  SPEAK", font_size="14sp",
            background_color=get_color_from_hex(self.PURPLE),
            color=get_color_from_hex(self.WHITE),
            size_hint_x=0.6)
        self.mic_btn.bind(on_press=self._toggle_mic)

        clr = Button(
            text="🗑 Clear", font_size="12sp",
            background_color=get_color_from_hex(self.BG2),
            color=get_color_from_hex(self.GRAY),
            size_hint_x=0.4)
        clr.bind(on_press=self._clear)

        btns.add_widget(self.mic_btn)
        btns.add_widget(clr)
        self.add_widget(btns)

    def _welcome(self):
        msg = (f"Hello! I'm {APP_NAME} by {CREATOR}. "
               f"Tap mic or type to begin!")
        self._add_msg(APP_NAME, msg)
        threading.Thread(
            target=self.tts.speak, args=(msg,), daemon=True).start()

    def _add_msg(self, role, text):
        is_you = role.lower() == "you"
        color  = self.CYAN if is_you else self.GREEN
        name   = "You" if is_you else APP_NAME
        lbl    = Label(
            text=f"[color={color}][b]{name}:[/b][/color]  {text}",
            markup=True, font_size="13sp",
            color=get_color_from_hex(self.WHITE),
            size_hint_y=None,
            text_size=(Window.width - 24, None),
            halign="left", valign="top")
        lbl.bind(texture_size=lbl.setter("size"))
        self.chat.add_widget(lbl)
        Clock.schedule_once(
            lambda dt: setattr(self.scroll, "scroll_y", 0), 0.1)

    def _set_status(self, text, color=None):
        color = color or self.CYAN
        def _u(dt):
            self.status_lbl.text  = text
            self.status_lbl.color = get_color_from_hex(color)
        Clock.schedule_once(_u, 0)

    def _send(self, *_):
        text = self.txt.text.strip()
        if text:
            self.txt.text = ""
            self._process(text)

    def _process(self, text):
        self._add_msg("You", text)
        self.history.append({"role": "user", "content": text})
        self._set_status("● Thinking...", self.YELLOW)
        threading.Thread(
            target=self._respond, args=(text,), daemon=True).start()

    def _respond(self, text):
        result = self.parser.parse(text)
        reply  = (result["msg"] if result["type"] == "cmd"
                  else self.brain.chat(text, self.history))
        self.history.append({"role": "assistant", "content": reply})
        Clock.schedule_once(lambda dt: self._show(reply), 0)

    def _show(self, reply):
        self._add_msg(APP_NAME, reply)
        self._set_status("● Speaking...", self.CYAN)
        threading.Thread(
            target=lambda: (self.tts.speak(reply),
                            self._set_status("● Ready")),
            daemon=True).start()

    def _toggle_mic(self, *_):
        if self.listening:
            return
        self.listening = True
        self.mic_btn.text = "⏹  STOP"
        self.mic_btn.background_color = get_color_from_hex(self.RED)
        self._set_status("● Listening...", self.RED)
        threading.Thread(target=self._listen_thread, daemon=True).start()

    def _listen_thread(self):
        text = self.stt.listen()
        self.listening = False
        Clock.schedule_once(lambda dt: self._reset_mic(), 0)
        if text:
            Clock.schedule_once(lambda dt: self._process(text), 0)
        else:
            self._set_status("● Didn't catch that", self.YELLOW)
            Clock.schedule_once(
                lambda dt: self._add_msg(
                    APP_NAME, "Didn't catch that — try again."), 0)

    def _reset_mic(self):
        self.mic_btn.text = "🎤  SPEAK"
        self.mic_btn.background_color = get_color_from_hex(self.PURPLE)
        self._set_status("● Ready")

    def _clear(self, *_):
        self.chat.clear_widgets()
        self.history = []
        self._add_msg(APP_NAME, "Chat cleared! How can I help?")


class MiracleApp(App):
    def build(self):
        self.title = f"{APP_NAME} AI Assistant"
        return MiracleUI()


if __name__ == "__main__":
    MiracleApp().run()

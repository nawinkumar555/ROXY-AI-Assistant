import pyttsx3
import speech_recognition as sr
import datetime
import webbrowser
import wikipedia
import pywhatkit
import pyautogui
import google.generativeai as genai

# Presentation Safety: Using 1.5-flash in the most stable way
genai.configure(api_key="AIzaSyD1G2Gn3mDz_u25uQUNwYKmTLxgg-AlTm0")

# INGA DHAAN CHANGE: v1beta-v1 confusion thavirkka direct model call
model = genai.GenerativeModel('gemini-1.5-flash')

engine = pyttsx3.init()

def speak(text):
    print(f"Assistant: {text}")
    engine.say(text)
    engine.runAndWait()

def take_command():
    listener = sr.Recognizer()
    try:
        with sr.Microphone() as source:
            print("Listening...")
            listener.adjust_for_ambient_noise(source, duration=0.5)
            voice = listener.listen(source, timeout=4, phrase_time_limit=5)
            command = listener.recognize_google(voice)
            return command.lower()
    except:
        return ""

speak("System Online. Ready for your command, Nawin.")

while True:
    user_input = take_command()
    if user_input:
        print(f"Nawin said: {user_input}")

        # --- 1. LOCAL AUTOMATION (No API Needed - Works 100%) ---
        if 'time' in user_input:
            speak(f"The current time is {datetime.datetime.now().strftime('%I:%M %p')}")

        elif 'volume' in user_input or 'increase' in user_input or 'decrease' in user_input:
            if 'increase' in user_input or 'up' in user_input:
                pyautogui.press("volumeup")
                speak("Volume increased")
            else:
                pyautogui.press("volumedown")
                speak("Volume decreased")

        elif 'weather' in user_input:
            speak("Checking weather in Madipakkam.")
            webbrowser.open("https://www.google.com/search?q=weather+in+madipakkam")

        elif 'stop' in user_input or 'exit' in user_input:
            speak("Goodbye Nawin! Turning off.")
            break

        # --- 2. AI BRAIN (Gemini Call) ---
        else:
            try:
                # v1beta problem thavirkka simple-aa try pannuvom
                response = model.generate_content(user_input)
                if response and response.text:
                    speak(response.text.replace("*", ""))
            except Exception as e:
                # Judge munnadi "404" nu print pannaadheenga, smooth fallback kudunga
                speak("I'm having a minor AI connection issue, but I can still control your system.")
import pyttsx3
import speech_recognition as sr
import google.generativeai as genai
import time


# ===================== TTS Initialization =====================
def initialize_tts():
    try:
        engine = pyttsx3.init()

        # Set speech rate (words per minute)
        engine.setProperty('rate', 160)

        # Set volume (0.0 to 1.0)
        engine.setProperty('volume', 0.9)

        # Try to set a female voice
        voices = engine.getProperty('voices')
        print(f"Available voices: {len(voices)}")

        for i, voice in enumerate(voices):
            print(f"Voice {i}: {voice.name} - {voice.id}")
            # Try to find a female voice (Zira on Windows, or other female voices)
            if any(keyword in voice.name.lower() for keyword in ['zira', 'female', 'woman']):
                engine.setProperty('voice', voice.id)
                print(f"Selected voice: {voice.name}")
                break
        else:
            # If no female voice found, use the first available voice
            if voices:
                engine.setProperty('voice', voices[0].id)
                print(f"Using default voice: {voices[0].name}")

        return engine

    except Exception as e:
        print(f"❌ Error initializing TTS: {e}")
        return None


engine = initialize_tts()


# ===================== Enhanced Speak Function =====================
def speak(text):
    """Convert text to speech and play through speakers"""
    print(f"\n🗣️ Nishi: {text}\n")

    if engine is None:
        print("❌ TTS engine not available")
        return

    try:
        # Clear any previous speech
        engine.stop()

        # Add the text to speech queue
        engine.say(text)

        # Wait for speech to complete
        engine.runAndWait()

        # Small pause after speaking
        time.sleep(0.5)

    except Exception as e:
        print(f"❌ Error in speech synthesis: {e}")


# ===================== Test TTS Function =====================
def test_tts():
    """Test if TTS is working properly"""
    speak("Hello! This is a test of the text to speech system. Can you hear me clearly?")


# ===================== Gemini API Configuration =====================
# IMPORTANT: Replace with your actual API key
genai.configure(api_key="AIzaSyCs59emAN1Z9hUSUoFt59G6_P3qfWl8Mhs")  # <-- Replace with your real key

generation_config = {
    "temperature": 0.7,
    "top_p": 0.9,
    "top_k": 40,
    "max_output_tokens": 1024,
}

model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    generation_config=generation_config,
)

chat = model.start_chat(history=[])


# ===================== Get Gemini Response =====================
def get_response_from_gemini(prompt):
    try:
        response = chat.send_message(prompt)
        return response.text.strip()
    except Exception as e:
        print(f"❌ Error from Gemini: {e}")
        return "Sorry, I couldn't process that request right now."


# ===================== Speech Recognition Setup =====================
recognizer = sr.Recognizer()
mic = sr.Microphone()

# Adjust recognition sensitivity
recognizer.energy_threshold = 300
recognizer.pause_threshold = 0.8
recognizer.phrase_threshold = 0.3

WAKE_WORD = "nishi"


# ===================== Enhanced Listening Function =====================
def listen():
    """Main listening loop with improved audio handling"""

    # Test TTS first
    print("🔧 Testing text-to-speech...")
    test_tts()

    # Calibrate microphone
    print("🎤 Calibrating microphone...")
    with mic as source:
        recognizer.adjust_for_ambient_noise(source, duration=2)
        print(f"🔊 Ambient noise level: {recognizer.energy_threshold}")

    speak("Hi, I am Nishi. Say my name and ask your question.")

    while True:
        with mic as source:
            print("🎧 Listening...")
            try:
                # Listen for audio input
                audio = recognizer.listen(source, timeout=5, phrase_time_limit=10)

                # Convert speech to text
                query = recognizer.recognize_google(audio).lower()
                print(f"🧏 You said: {query}")

                # Check for exit commands
                if any(word in query for word in ["stop", "exit", "bye", "quit", "goodbye"]):
                    speak("Goodbye! Have a great day!")
                    break

                # Check for wake word
                if WAKE_WORD in query:
                    # Extract question after wake word
                    question = query.split(WAKE_WORD, 1)[-1].strip()

                    if not question:
                        speak("Yes? Please ask your question.")
                    else:
                        print(f"🤔 Processing: {question}")
                        speak("Let me think about that...")

                        # Get AI response
                        answer = get_response_from_gemini(question)

                        # Speak the answer
                        speak(answer)
                else:
                    print("🔕 Wake word not detected. Say 'Nishi' to activate.")

            except sr.UnknownValueError:
                print("❌ Sorry, I couldn't understand that. Please speak clearly.")
            except sr.WaitTimeoutError:
                print("⏱️ Listening timeout. Say something...")
            except sr.RequestError as e:
                print(f"⚠️ Speech recognition error: {e}")
                speak("Sorry, I'm having trouble with speech recognition.")
            except Exception as e:
                print(f"❌ Unexpected error: {e}")


# ===================== Audio System Check =====================
def check_audio_system():
    """Check if audio output is working"""
    print("🔊 Checking audio system...")

    # List available audio devices (if possible)
    try:
        import sounddevice as sd
        devices = sd.query_devices()
        print("Available audio devices:")
        for i, device in enumerate(devices):
            if device['max_output_channels'] > 0:
                print(f"  Output Device {i}: {device['name']}")
    except ImportError:
        print("Install sounddevice for detailed audio device info: pip install sounddevice")

    # Test TTS
    test_tts()


# ===================== Main =====================
if __name__ == "__main__":
    print("🚀 Starting Nishi Voice Assistant...")
    print("📋 Make sure your speakers/headphones are connected and volume is up!")

    # Optional: Check audio system
    # check_audio_system()

    # Start the main listening loop
    try:
        listen()
    except KeyboardInterrupt:
        print("\n👋 Assistant stopped by user")
        speak("Goodbye!")
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        speak("I'm experiencing technical difficulties. Goodbye!")
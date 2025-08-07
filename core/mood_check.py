import speech_recognition as sr
import pyttsx3
from transformers import pipeline
import random

# Initialize text-to-speech engine
engine = pyttsx3.init()

def speak(text):
    print("🤖", text)
    engine.say(text)
    engine.runAndWait()

def listen():
    recognizer = sr.Recognizer()

    with sr.Microphone() as source:
        print(" Listening...")
        audio = recognizer.listen(source)

    try:
        text = recognizer.recognize_google(audio)
        print("You said:", text)
        return text
    except sr.UnknownValueError:
        speak("Sorry, I didn't catch that. Can you try saying that again?")

        with sr.Microphone() as source:
            print("Listening again...")
            audio = recognizer.listen(source)

        try:
            text = recognizer.recognize_google(audio)
            print("You said:", text)
            return text
        except sr.UnknownValueError:
            speak("Still couldn't understand you. We'll go with neutral for now.")
            return "neutral"
        except sr.RequestError:
            speak("Speech service is unavailable.")
            return "neutral"

    except sr.RequestError:
        speak("Speech service is unavailable.")
        return "neutral"




emotion_pipeline = pipeline(
    "text-classification", 
    model="j-hartmann/emotion-english-distilroberta-base", 
    top_k=1
)

def fallback_keyword_emotion(text):
    text = text.lower()
    if any(word in text for word in ["happy", "great", "good", "excited", "awesome"]):
        return "joy"
    elif any(word in text for word in ["sad", "tired", "down", "upset", "depressed"]):
        return "sadness"
    elif any(word in text for word in ["angry", "mad", "frustrated"]):
        return "anger"
    elif any(word in text for word in ["anxious", "worried", "scared"]):
        return "fear"
    elif any(word in text for word in ["gross", "nasty", "disgusted"]):
        return "disgust"
    return None


def analyze_emotion(text):
    results = emotion_pipeline(text)[0]
    for result in results:
        emotion = result["label"].lower()
        score = result["score"]
        if emotion in responses and score > 0.6:
            return emotion
    
    fallback = fallback_keyword_emotion(text)
    if fallback:
        print(f"Fallback to keyword: {fallback}")
        return fallback

    return "neutral"



responses = {
    "joy": [
        "Love that energy! Let’s get it!",
        "You're on fire today !",
        "Awesome mood! This workout’s gonna be great!"
    ],
    "sadness": [
        "Hey, we all have off days — let’s turn it around.",
        "You got this. Moving your body helps your mind too.",
        "I'm here with you — let's start slow."
    ],
    "anger": [
        "Channel that fire into your reps!",
        "Let’s burn it out with some intensity!",
        "Time to smash this workout!"
    ],
    "fear": [
        "No worries — you’re safe here with me.",
        "You’re stronger than you think.",
        "One step at a time. I’m with you."
    ],
    "disgust": [
        "Let’s shake that off — fresh start now!",
        "You’ve already won by showing up.",
        "Time to clear the mind with some movement."
    ],
    "surprise": [
        "Surprises can be good — let’s channel that!",
        "Let’s see where this workout takes you!",
        "Unexpected energy? Let’s go with it!"
    ],
    "neutral": [
        "Cool. Let’s ease into the workout.",
        "Let’s make this a good one.",
        "Alright, starting steady. Let’s move."
    ]
}

def main():
    speak("Hi! How are you feeling today?")
    user_input = listen()
    emotion = analyze_emotion(user_input)

    reply = random.choice(responses.get(emotion, responses["neutral"]))
    speak(reply)

if __name__ == "__main__":
    main()

""" # main.py

from core.mood_check import speak, listen, analyze_emotion, responses
from core.rep_counter import start_workout
import random
import sys

def main():
    speak("Hi! How are you feeling today?")
    user_input = listen()

    emotion = analyze_emotion(user_input)
    reply = random.choice(responses.get(emotion, responses["neutral"]))
    speak(reply)

    # Keep asking until understood
    while True:
        speak("Which workout would you like to do today? Curls, pushups, situps, squats, plank, or say 'let you detect it' to let me watch and detect automatically.")
        workout_input = listen().lower()

        if "let you detect it" in workout_input:
            speak("Alright, I will watch and detect your workout live. Get ready!")
            import free_for_all
            free_for_all.main()
            return  # exit main after free_for_all finishes

        elif "curl" in workout_input:
            workout_type = "curl"
            break
        elif "pushup" in workout_input:
            workout_type = "pushup"
            break
        elif "situp" in workout_input:
            workout_type = "situp"
            break
        elif "squat" in workout_input:
            workout_type = "squat"
            break
        elif "plank" in workout_input:
            workout_type = "plank"
            break
        else:
            speak("Sorry, I didn't understand that. Please say the workout again.")

    speak(f"Starting your {workout_type} workout now. Get ready!")
    start_workout(workout_type)


if __name__ == "__main__":
    main() """

# main.py
from ui.main_window import launch_app

if __name__ == "__main__":
    launch_app()

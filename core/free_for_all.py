
# (All your imports remain the same)
import cv2
import time
import numpy as np
import mediapipe as mp
import threading
import speech_recognition as sr
from queue import Queue
from core.predictor import model, label_encoder
from core.mood_check import speak
from keras.models import load_model
import joblib
from firebase_admin import firestore
from datetime import datetime

from utils.data_logger import save_workout_data

mp_pose = mp.solutions.pose
pose = mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)

# --- Voice Listener Thread for Break Detection ---
def voice_listener(break_queue, done_queue):
    recognizer = sr.Recognizer()
    mic = sr.Microphone()
    while True:
        try:
            with mic as source:
                recognizer.adjust_for_ambient_noise(source)
                print("🎤 Listening for voice commands...")
                audio = recognizer.listen(source, timeout=5)
            spoken = recognizer.recognize_google(audio).lower()
            print(f"🎙 Heard: {spoken}")
            if any(kw in spoken for kw in ["i'm tired", "need a break", "pause", "stop", "break time"]):
                break_queue.put(True)
                print("🛑 Break command detected.")
            elif "i'm done" in spoken or "i am done" in spoken:
                done_queue.put(True)
                print("👋 Done command detected.")
                break  # optional: stop listening after done
        except Exception:
            continue

# --- Ask for Break Duration ---
def ask_for_break_duration():
    recognizer = sr.Recognizer()
    mic = sr.Microphone()
    with mic as source:
        prompt = "How long do you want your break to be in seconds?"
        speak(prompt)
        print(f"🗣️ {prompt}")
        audio = recognizer.listen(source)
    try:
        spoken = recognizer.recognize_google(audio).lower()
        print(f"⏱️ You said: {spoken}")
        digits = ''.join(filter(str.isdigit, spoken))
        return int(digits) if digits else 10  # default to 10 seconds if unclear
    except:
        print("⚠️ Couldn't understand. Defaulting to 10 seconds break.")
        return 10

# --- Break Timer Overlay ---
def start_break_timer(seconds, frame_shape):
    end_time = time.time() + seconds
    while time.time() < end_time:
        time_left = int(end_time - time.time())
        frame = np.zeros(frame_shape, dtype=np.uint8)
        cv2.putText(frame, f"⏸️ Break: {time_left}s", (60, 200),
                    cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 255), 4)
        cv2.imshow("Break Timer", frame)
        if cv2.waitKey(1000) & 0xFF == ord('q'):
            break
    cv2.destroyWindow("Break Timer")

# --- Extract Landmarks ---
def extract_landmarks(results):
    if not results.pose_landmarks:
        return None
    return np.array([coord for lm in results.pose_landmarks.landmark for coord in (lm.x, lm.y, lm.z)], dtype=np.float32)

# --- Calculate Angle ---
def calculate_angle(a, b, c):
    a = np.array(a)
    b = np.array(b)
    c = np.array(c)
    radians = np.arctan2(c[1]-b[1], c[0]-b[0]) - np.arctan2(a[1]-b[1], a[0]-b[0])
    angle = np.abs(radians * 180.0 / np.pi)
    return 360 - angle if angle > 180 else angle

# --- Main Free-for-All Workout Detection with Break Support ---
def main(user_id=None):  # <–– Only change: allow optional user_id
    form_model = load_model('classifier/model/form_classifier_model.keras')
    form_label_encoder = joblib.load('classifier/model/form_label_encoder.pkl')

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not open webcam")
        return
    start_time = time.time()

    seq_length = 30
    landmark_seq = []

    current_workout = None
    last_change_time = time.time()
    stable_duration_required = 5.0

    rep_counts = {
    'curls': 0, 
    'pushups': 0, 
    'situps': 0,
    'squats': 0,
    'pushups_good': 0,
    'pushups_bad': 0,
    'curls_good': 0,
    'curls_bad': 0,
    'situps_good': 0,
    'situps_bad': 0,
    'squats_good': 0,
    'squats_bad': 0}
    calories = 0.0
    plank_timer_start = None
    plank_total_time = 0
    stages = {'curls': None, 'pushups': None, 'situps': None, 'squats': None}

    # --- Setup break detection ---
    break_queue = Queue()
    done_queue = Queue()
    threading.Thread(target=voice_listener, args=(break_queue, done_queue), daemon=True).start()

    speak("Starting free-for-all workout detection. Begin exercising!")

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            if not done_queue.empty():
                print("👋 User is done. Exiting workout.")
                break

            # --- Handle break request ---
            while not break_queue.empty():
                break_queue.get()  # Clear break command
                seconds = ask_for_break_duration()
                print(f"⏸️ Taking a {seconds}-second break...")
                start_break_timer(seconds, frame.shape)
                print("✅ Break over. Resuming workout.")

            img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = pose.process(img_rgb)
            landmarks = extract_landmarks(results)

            if landmarks is not None and results.pose_landmarks:
                lm = results.pose_landmarks.landmark
                landmark_seq.append(landmarks)
                if len(landmark_seq) > seq_length:
                    landmark_seq.pop(0)

                if len(landmark_seq) == seq_length:
                    input_data = np.expand_dims(np.array(landmark_seq), axis=0)
                    pred_label = label_encoder.inverse_transform([np.argmax(model.predict(input_data, verbose=0))])[0]
                    form_probs = form_model.predict(input_data, verbose=0)
                    form_pred_label = form_label_encoder.inverse_transform(np.argmax(form_probs, axis=1))[0]

                    # (🟢 Your full per-exercise logic is kept intact here)

                    # Override form prediction using angles consistent with rep_counter.py
                    if pred_label == "pushups":
                        shoulder = [lm[11].x, lm[11].y]
                        hip = [lm[23].x, lm[23].y]
                        ankle = [lm[27].x, lm[27].y]
                        back_angle = calculate_angle(shoulder, hip, ankle)

                        elbow_angle = calculate_angle([lm[11].x, lm[11].y],
                                   [lm[13].x, lm[13].y],
                                   [lm[15].x, lm[15].y])
                        shoulder_y = lm[11].y
                        form_pred_label = "pushupsgood" if 175 <= back_angle <= 183 and elbow_angle > 165 and shoulder_y < 0.35 else "pushupsbad"

                        # Looser rep movement detection
                        if elbow_angle < 90 and shoulder_y > 0.6:
                            stages['pushups'] = "down"
                        if elbow_angle > 150 and shoulder_y < 0.4 and stages['pushups'] == "down":
                            stages['pushups'] = "up"
                            rep_counts['pushups_good' if form_pred_label == "pushupsgood" else 'pushups_bad'] += 1
                            rep_counts['pushups'] += 1
                            calories += 0.5
                            print(f"✅ Push-up #{rep_counts['pushups']} | 🔥 {calories:.1f} cal")

                    elif pred_label == "curls":
                        shoulder = [lm[11].x, lm[11].y]
                        elbow = [lm[13].x, lm[13].y]
                        wrist = [lm[15].x, lm[15].y]
                        angle = calculate_angle(shoulder, elbow, wrist)

                        form_pred_label = "curlsgood" if angle < 25 or angle > 170 else "curlsbad"
                        if angle > 160:
                            stages['curls'] = "down"
                        if angle < 30 and stages['curls'] == "down":
                            stages['curls'] = "up"
                            rep_counts['curls_good' if form_pred_label == "curlsgood" else 'curls_bad'] += 1
                            rep_counts['curls'] += 1
                            calories += 0.5
                            print(f"✅ Curl #{rep_counts['curls']} | 🔥 {calories:.1f} cal")


                    elif pred_label == "situps":
                        shoulder = [lm[11].x, lm[11].y]
                        hip = [lm[23].x, lm[23].y]
                        knee = [lm[25].x, lm[25].y]
                        angle = calculate_angle(shoulder, hip, knee)

                        form_pred_label = "situpsgood" if angle < 50 else "situpsbad"
                        if angle > 120:
                            stages['situps'] = "down"
                        if angle < 75 and stages['situps'] == "down":
                            stages['situps'] = "up"
                            rep_counts['situps_good' if form_pred_label == "situpsgood" else 'situps_bad'] += 1
                            rep_counts['situps'] += 1
                            calories += 0.6
                            print(f"✅ Sit-up #{rep_counts['situps']} | 🔥 {calories:.1f} cal")

                    elif pred_label == "squats":
                        hip = [lm[23].x, lm[23].y]
                        knee = [lm[25].x, lm[25].y]
                        ankle = [lm[27].x, lm[27].y]
                        angle = calculate_angle(hip, knee, ankle)

                        form_pred_label = "squatsgood" if angle < 70 else "squatsbad"

                        if angle > 150:
                            stages['squats'] = "up"
                        if angle < 90 and stages['squats'] == "up":
                            stages['squats'] = "down"
                            rep_counts['squats_good' if form_pred_label == "squatsgood" else 'squats_bad'] += 1
                            rep_counts['squats'] += 1
                            calories += 0.7
                            print(f"🏋️ Squat #{rep_counts['squats']} | 🔥 {calories:.1f} cal")


                    # Reset stage and form feedback
                    if pred_label != current_workout:
                        current_workout = pred_label
                        last_change_time = time.time()
                        if current_workout in stages:
                            stages[current_workout] = None

                    border_color = (0, 255, 0) if form_pred_label.endswith("good") else (0, 0, 255)
                    cv2.rectangle(frame, (0, 0), (frame.shape[1], frame.shape[0]), border_color, 10)

                    current_time = time.time()
                    if current_time - last_change_time >= stable_duration_required:
                        speak(f"Now you're doing {current_workout}")
                        last_change_time = current_time + 10000

            # --- Display overlays ---
            y = 30
            for workout, count in rep_counts.items():
                cv2.putText(frame, f"{workout}: {count}", (10, y), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                y += 30
            cv2.putText(frame, f"Calories: {calories:.1f}", (10, y), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)

            cv2.imshow('Free-for-all Workout Detection', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    finally:
        print("\nWorkout Summary:")
        for workout, count in rep_counts.items():
            print(f"  {workout.capitalize()}: {count} reps")
        print(f"  Total Calories burned: {calories:.1f} cal")

        if user_id:
            print(f"🔐 User ID: {user_id} (ready to save data if needed)")

        """ db = firestore.client()
        doc_ref = db.collection('workout_data').document(f"{user_id}_{datetime.today().date()}")

        doc_ref.set({
            'reps': sum(rep_counts.values()),
            'calories': round(calories, 1),
            'duration': round(time.time() - start_time) // 60  # in minutes
            }) """
        

        duration = round(time.time() - start_time) // 60  # in minutes
        save_workout_data(
            user_id=user_id,
            reps_dict=rep_counts,
            calories=calories,
            duration=duration,
            plank_time=0  # Free-for-all doesn't track plank
)

        cap.release()
        cv2.destroyAllWindows()
        return "done"  # This allows GUI to return to dashboard


if __name__ == "__main__":
    main()

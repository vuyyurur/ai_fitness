""" import cv2
import mediapipe as mp
import numpy as np
import time
import threading
import speech_recognition as sr
from queue import Queue
from core.mood_check import speak


mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose

# === Angle Calculation ===
def calculate_angle(a, b, c):
    a, b, c = np.array(a), np.array(b), np.array(c)
    radians = np.arctan2(c[1]-b[1], c[0]-b[0]) - np.arctan2(a[1]-b[1], a[0]-b[0])
    angle = np.abs(radians * 180.0 / np.pi)
    return 360 - angle if angle > 180 else angle

# === Voice Listener Thread ===
def voice_listener(break_queue):
    recognizer = sr.Recognizer()
    mic = sr.Microphone()
    while True:
        try:
            with mic as source:
                recognizer.adjust_for_ambient_noise(source)
                print("🎤 Listening in background...")
                audio = recognizer.listen(source, timeout=5)
            spoken = recognizer.recognize_google(audio).lower()
            print(f"🎙 Heard: {spoken}")
            if any(kw in spoken for kw in ["i'm tired", "need a break", "pause", "stop", "break time"]):
                break_queue.put(True)
                print("🛑 Break command detected.")
        except Exception:
            continue

# === Simple Voice Prompt ===
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
        return int(digits) if digits else 10  # default to 10s if no digits
    except:
        print("⚠️ Couldn't understand. Defaulting to 10s break.")
        return 10

# === Break Timer Overlay ===
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

# === Workout Loop ===
def start_workout(workout_type='curl'):
    cap = cv2.VideoCapture(0)
    counter = 0
    stage = None
    calories = 0
    plank_timer_start = None
    plank_total_time = 0
    break_queue = Queue()

    # Start voice listener thread
    threading.Thread(target=voice_listener, args=(break_queue,), daemon=True).start()

    with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            # === Pause if user requested break ===
            while not break_queue.empty():
                break_queue.get()  # Clear previous break command
                seconds = ask_for_break_duration()
                print(f"⏸️ Taking a {seconds}-second break...")
                start_break_timer(seconds, frame.shape)
                print("✅ Break over. Resuming workout.")

            image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            image.flags.writeable = False
            results = pose.process(image)
            image.flags.writeable = True
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

            try:
                landmarks = results.pose_landmarks.landmark

                if workout_type == 'curl':
                    shoulder = [landmarks[11].x, landmarks[11].y]
                    elbow = [landmarks[13].x, landmarks[13].y]
                    wrist = [landmarks[15].x, landmarks[15].y]
                    angle = calculate_angle(shoulder, elbow, wrist)

                    if angle > 160:
                        stage = "down"
                    if angle < 30 and stage == "down":
                        stage = "up"
                        counter += 1
                        calories += 0.5
                        print(f"💪 Curl #{counter} | 🔥 Calories: {calories:.1f}")

                elif workout_type == 'pushup':
                    shoulder = [landmarks[11].x, landmarks[11].y]
                    elbow = [landmarks[13].x, landmarks[13].y]
                    wrist = [landmarks[15].x, landmarks[15].y]
                    hip = [landmarks[23].x, landmarks[23].y]
                    ankle = [landmarks[27].x, landmarks[27].y]

                    elbow_angle = calculate_angle(shoulder, elbow, wrist)
                    body_angle = calculate_angle(shoulder, hip, ankle)
                    shoulder_y = shoulder[1]
                    is_down = elbow_angle < 90 and shoulder_y > 0.6
                    is_up = elbow_angle > 160 and shoulder_y < 0.4
                    form_good = 165 < body_angle < 195

                    if is_down and form_good:
                        stage = "down"
                    if is_up and stage == "down" and form_good:
                        stage = "up"
                        counter += 1
                        calories += 0.5
                        print(f"✅ Push-up #{counter} | 🔥 Calories: {calories:.1f}")
                    elif not form_good:
                        print("⚠️ Fix your form!")

                elif workout_type == 'situp':
                    shoulder = [landmarks[11].x, landmarks[11].y]
                    hip = [landmarks[23].x, landmarks[23].y]
                    knee = [landmarks[25].x, landmarks[25].y]
                    angle = calculate_angle(shoulder, hip, knee)

                    if angle > 120:
                        stage = "down"
                    if angle < 80 and stage == "down":
                        stage = "up"
                        counter += 1
                        calories += 0.6
                        print(f"✅ Sit-up #{counter} | 🔥 Calories: {calories:.1f}")

                elif workout_type == 'squat':
                    hip = [landmarks[23].x, landmarks[23].y]
                    knee = [landmarks[25].x, landmarks[25].y]
                    ankle = [landmarks[27].x, landmarks[27].y]
                    angle = calculate_angle(hip, knee, ankle)

                    if angle > 160:
                        stage = "up"
                    if angle < 90 and stage == "up":
                        stage = "down"
                        counter += 1
                        calories += 0.7
                        print(f"🏋️ Squat #{counter} | 🔥 Calories: {calories:.1f}")

                elif workout_type == 'plank':
                    shoulder = [landmarks[11].x, landmarks[11].y]
                    hip = [landmarks[23].x, landmarks[23].y]
                    ankle = [landmarks[27].x, landmarks[27].y]
                    body_angle = calculate_angle(shoulder, hip, ankle)

                    if 160 < body_angle < 195:
                        if plank_timer_start is None:
                            plank_timer_start = time.time()
                        elapsed = time.time() - plank_timer_start
                    else:
                        if plank_timer_start:
                            plank_total_time += time.time() - plank_timer_start
                            plank_timer_start = None
                        elapsed = 0

                    total_time = plank_total_time + (elapsed if plank_timer_start else 0)
                    calories = total_time / 60 * 5  # 5 cal/min

                    cv2.putText(image, f"⏱ {total_time:.1f}s", (10, 60),
                                cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 0), 2)
                    cv2.putText(image, f"🔥 {calories:.1f} cal", (10, 100),
                                cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 255), 2)

            except Exception:
                pass

            # Display counter and calories
            if workout_type != 'plank':
                cv2.rectangle(image, (0, 0), (250, 100), (245, 117, 16), -1)
                cv2.putText(image, f'Reps: {counter}', (10, 35),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
                cv2.putText(image, f'🔥 {calories:.1f} cal', (10, 75),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

            mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)
            cv2.imshow(f'{workout_type.capitalize()} Tracker', image)

            if cv2.waitKey(10) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()

        if workout_type == 'plank' and plank_timer_start:
            plank_total_time += time.time() - plank_timer_start

        print(f"✅ Workout complete!")
        print(f"🔁 Total reps: {counter}")
        print(f"🔥 Total calories burned: {calories:.1f} cal") """



import cv2
import mediapipe as mp
import time
import numpy as np
from utils.data_logger import save_workout_data  # 🔥 Firestore logger

mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose


def calculate_angle(a, b, c):
    a = np.array(a)
    b = np.array(b)
    c = np.array(c)

    radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - \
              np.arctan2(a[1] - b[1], a[0] - b[0])
    angle = np.abs(radians * 180.0 / np.pi)

    if angle > 180.0:
        angle = 360 - angle

    return angle


def start_workout(workout_type='curl', user_id=None):  # user_id added ✅
    cap = cv2.VideoCapture(0)
    counter = 0
    stage = None
    calories = 0
    plank_start_time = None
    plank_total_time = 0

    with mp_pose.Pose(min_detection_confidence=0.5,
                      min_tracking_confidence=0.5) as pose:

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            image.flags.writeable = False
            results = pose.process(image)

            image.flags.writeable = True
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

            try:
                landmarks = results.pose_landmarks.landmark

                shoulder = [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x,
                            landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
                elbow = [landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].x,
                         landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].y]
                wrist = [landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].x,
                         landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].y]

                hip = [landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].x,
                       landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].y]
                knee = [landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].x,
                        landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].y]
                ankle = [landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].x,
                         landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].y]

                if workout_type == 'curl':
                    angle = calculate_angle(shoulder, elbow, wrist)
                    if angle > 160:
                        stage = "down"
                    if angle < 30 and stage == 'down':
                        stage = "up"
                        counter += 1
                        calories += 0.3

                elif workout_type == 'squat':
                    angle = calculate_angle(hip, knee, ankle)
                    if angle > 160:
                        stage = "up"
                    if angle < 90 and stage == 'up':
                        stage = "down"
                        counter += 1
                        calories += 0.5

                elif workout_type == 'pushup':
                    angle = calculate_angle(shoulder, elbow, wrist)
                    if angle > 160:
                        stage = "up"
                    if angle < 90 and stage == 'up':
                        stage = "down"
                        counter += 1
                        calories += 0.4

                elif workout_type == 'situp':
                    angle = calculate_angle(hip, shoulder, wrist)
                    if angle > 150:
                        stage = "down"
                    if angle < 100 and stage == "down":
                        stage = "up"
                        counter += 1
                        calories += 0.35

                elif workout_type == 'plank':
                    if plank_start_time is None:
                        plank_start_time = time.time()
                    plank_total_time = time.time() - plank_start_time
                    calories = plank_total_time * 0.05

            except Exception as e:
                print("Error:", e)

            # Draw landmarks
            mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)

            # Display rep count and calories
            cv2.putText(image, f'Reps: {counter}', (10, 40),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            cv2.putText(image, f'Calories: {round(calories, 1)}', (10, 80),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

            if workout_type == 'plank':
                cv2.putText(image, f'Time: {int(plank_total_time)} sec', (10, 120),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)

            cv2.imshow('Workout', image)

            if cv2.waitKey(10) & 0xFF == ord('q'):
                break

    cap.release()
    cv2.destroyAllWindows()

    print(f"\n✅ Workout finished!")
    print(f"Total reps: {counter}")
    print(f"🔥 Total calories burned: {round(calories, 1)}")

    # Save data to Firestore ✅
    duration = plank_total_time if workout_type == 'plank' else counter * 2  # Estimate: 2 sec per rep

    if user_id:
        save_workout_data(
            user_id=user_id,
            reps=counter,
            calories=round(calories, 1),
            duration=int(duration)
        )
        print(f"✅ Data saved to Firestore for user {user_id}")
    else:
        print("⚠️ No user_id provided — workout data not saved.")




        


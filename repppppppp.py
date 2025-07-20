import cv2
import mediapipe as mp
import time
import numpy as np
from keras.models import load_model
import joblib
from utils.data_logger import save_workout_data  # 🔥 Firestore logger

mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose

# Initialize MediaPipe Pose
pose = mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)

# Load form classification model and label encoder
form_model = load_model('classifier/model/form_classifier_model.keras')
form_label_encoder = joblib.load('classifier/model/form_label_encoder.pkl')

def calculate_angle(a, b, c):
    a = np.array(a)
    b = np.array(b)
    c = np.array(c)
    radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - np.arctan2(a[1] - b[1], a[0] - b[0])
    angle = np.abs(radians * 180.0 / np.pi)
    return 360 - angle if angle > 180 else angle

def extract_landmarks(results):
    if not results.pose_landmarks:
        return None
    return np.array([coord for lm in results.pose_landmarks.landmark for coord in (lm.x, lm.y, lm.z)], dtype=np.float32)

def start_workout(workout_type='curl', user_id=None):
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not open webcam")
        return

    start_time = time.time()
    seq_length = 30
    landmark_seq = []

    # Initialize rep counts and stages
    rep_counts = {
        'curls': 0, 'pushups': 0, 'situps': 0, 'squats': 0,
        'curls_good': 0, 'curls_bad': 0,
        'pushups_good': 0, 'pushups_bad': 0,
        'situps_good': 0, 'situps_bad': 0,
        'squats_good': 0, 'squats_bad': 0
    }
    calories = 0.0
    stages = {'curls': None, 'pushups': None, 'situps': None, 'squats': None}
    plank_start_time = None
    plank_total_time = 0

    # Map workout_type to internal naming
    workout_map = {
        'curl': 'curls',
        'squat': 'squats',
        'pushup': 'pushups',
        'situp': 'situps',
        'plank': 'plank'
    }
    internal_workout_type = workout_map.get(workout_type, 'curls')

    print(f"Starting {internal_workout_type} workout...")

    try:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                print("Error: Failed to capture frame")
                break

            img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = pose.process(img_rgb)
            img_bgr = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2BGR)
            landmarks = extract_landmarks(results)

            form_pred_label = None
            if landmarks is not None and results.pose_landmarks:
                lm = results.pose_landmarks.landmark
                landmark_seq.append(landmarks)
                if len(landmark_seq) > seq_length:
                    landmark_seq.pop(0)

                if len(landmark_seq) == seq_length and internal_workout_type != 'plank':
                    input_data = np.expand_dims(np.array(landmark_seq), axis=0)
                    form_probs = form_model.predict(input_data, verbose=0)
                    form_pred_label = form_label_encoder.inverse_transform(np.argmax(form_probs, axis=1))[0]

                    if internal_workout_type == 'pushups':
                        shoulder = [lm[11].x, lm[11].y]
                        hip = [lm[23].x, lm[23].y]
                        ankle = [lm[27].x, lm[27].y]
                        back_angle = calculate_angle(shoulder, hip, ankle)
                        elbow_angle = calculate_angle([lm[11].x, lm[11].y], [lm[13].x, lm[13].y], [lm[15].x, lm[15].y])
                        shoulder_y = lm[11].y
                        form_pred_label = "pushupsgood" if 175 <= back_angle <= 183 and elbow_angle > 165 and shoulder_y < 0.35 else "pushupsbad"

                        if elbow_angle < 90 and shoulder_y > 0.6:
                            stages['pushups'] = "down"
                        if elbow_angle > 150 and shoulder_y < 0.4 and stages['pushups'] == "down":
                            stages['pushups'] = "up"
                            rep_counts['pushups_good' if form_pred_label == "pushupsgood" else 'pushups_bad'] += 1
                            rep_counts['pushups'] += 1
                            calories += 0.5
                            print(f"✅ Push-up #{rep_counts['pushups']} | Form: {'Good' if form_pred_label == 'pushupsgood' else 'Bad'} | 🔥 {calories:.1f} cal")

                    elif internal_workout_type == 'curls':
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
                            print(f"✅ Curl #{rep_counts['curls']} | Form: {'Good' if form_pred_label == 'curlsgood' else 'Bad'} | 🔥 {calories:.1f} cal")

                    elif internal_workout_type == 'situps':
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
                            print(f"✅ Sit-up #{rep_counts['situps']} | Form: {'Good' if form_pred_label == 'situpsgood' else 'Bad'} | 🔥 {calories:.1f} cal")

                    elif internal_workout_type == 'squats':
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
                            print(f"✅ Squat #{rep_counts['squats']} | Form: {'Good' if form_pred_label == 'squatsgood' else 'Bad'} | 🔥 {calories:.1f} cal")

                    elif internal_workout_type == 'plank':
                        if plank_start_time is None:
                            plank_start_time = time.time()
                        plank_total_time = time.time() - plank_start_time
                        calories = plank_total_time * 0.05
                        form_pred_label = None  # No form classification for plank

                # Draw landmarks
                mp_drawing.draw_landmarks(img_bgr, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)

                # Display form feedback with border
                if form_pred_label:
                    border_color = (0, 255, 0) if form_pred_label.endswith("good") else (0, 0, 255)
                    cv2.rectangle(img_bgr, (0, 0), (img_bgr.shape[1], img_bgr.shape[0]), border_color, 10)

                # Display rep counts and calories
                y = 30
                for workout, count in rep_counts.items():
                    if count > 0 or workout == internal_workout_type:
                        cv2.putText(img_bgr, f"{workout}: {count}", (10, y), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                        y += 30
                cv2.putText(img_bgr, f"Calories: {calories:.1f}", (10, y), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)

                if internal_workout_type == 'plank':
                    cv2.putText(img_bgr, f"Time: {int(plank_total_time)} sec", (10, y + 30),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)

            cv2.imshow('Workout', img_bgr)
            if cv2.waitKey(10) & 0xFF == ord('q'):
                break

    except Exception as e:
        print(f"Error: {e}")

    finally:
        cap.release()
        cv2.destroyAllWindows()

        print(f"\n✅ {internal_workout_type.capitalize()} Workout Summary:")
        for workout, count in rep_counts.items():
            if count > 0:
                print(f"  {workout.capitalize()}: {count} reps")
        print(f"  Total Calories burned: {calories:.1f} cal")
        duration = plank_total_time if internal_workout_type == 'plank' else (time.time() - start_time) // 60

        if user_id:
            save_workout_data(
                user_id=user_id,
                reps_dict=rep_counts,
                calories=round(calories, 1),
                duration=int(duration),
                plank_time=int(plank_total_time) if internal_workout_type == 'plank' else 0
            )
            print(f"✅ Data saved to Firestore for user {user_id}")
        else:
            print("⚠️ No user_id provided — workout data not saved.")

    return "done"

if __name__ == "__main__":
    start_workout(workout_type='curl', user_id='test_user')

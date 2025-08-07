import cv2
import mediapipe as mp
import time
import numpy as np
from keras.models import load_model
import joblib
from utils.data_logger import save_workout_data

mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose

pose = mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)

try:
    form_model = load_model('classifier/model/form_classifier_model.keras')
    form_label_encoder = joblib.load('classifier/model/form_label_encoder.pkl')
except Exception as e:
    print(f"Error loading model or label encoder: {e}")
    form_model = None
    form_label_encoder = None

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
    workout_config = {
        'curls': {
            'landmarks': [(11, 13, 15)], 
            'angle_ranges': {'up': (160, 180), 'down': (0, 30)},
            'calories_per_rep': 0.5,
            'form_labels': ['curlsgood', 'curlsbad']
        },
        'pushups': {
            'landmarks': [(11, 13, 15), (11, 23, 27)], 
            'angle_ranges': {'up': (150, 180, 175, 183), 'down': (0, 90, None, None)},
            'extra_condition': lambda lm: lm[11].y < 0.4,
            'calories_per_rep': 0.5,
            'form_labels': ['pushupsgood', 'pushupsbad']
        },
        'situps': {
            'landmarks': [(11, 23, 25)], 
            'angle_ranges': {'up': (120, 180), 'down': (0, 75)},
            'calories_per_rep': 0.6,
            'form_labels': ['situpsgood', 'situpsbad']
        },
        'squats': {
            'landmarks': [(23, 25, 27)],
            'angle_ranges': {'up': (150, 180), 'down': (0, 90)},
            'calories_per_rep': 0.7,
            'form_labels': ['squatsgood', 'squatsbad']
        },
        'plank': {
            'landmarks': [(11, 23, 27)], 
            'angle_ranges': {'plank': (170, 190)},
            'extra_condition': lambda lm: lm[11].y > 0.6 and lm[23].y > 0.6, 
            'calories_per_second': 0.05,
            'form_labels': ['plankgood', 'plankbad']
        }
    }

    workout_map = {
        'curl': 'curls',
        'squat': 'squats',
        'pushup': 'pushups',
        'situp': 'situps',
        'plank': 'plank'
    }

    internal_workout_type = workout_map.get(workout_type.lower() if workout_type else None, None)
    if internal_workout_type not in workout_config:
        print(f"Error: Invalid workout type '{workout_type}'. Supported types: {list(workout_map.keys())}")
        return "error"

    config = workout_config[internal_workout_type]
    print(f"Starting {internal_workout_type} workout...")

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not open webcam")
        return "error"

    start_time = time.time()
    seq_length = 30
    landmark_seq = []
    rep_counts = {
        'curls': 0, 'pushups': 0, 'situps': 0, 'squats': 0,
        'curls_good': 0, 'curls_bad': 0,
        'pushups_good': 0, 'pushups_bad': 0,
        'situps_good': 0, 'situps_bad': 0,
        'squats_good': 0, 'squats_bad': 0
    }
    calories = 0.0
    stage = None
    plank_start_time = None
    plank_total_time = 0
    in_plank_position = False

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

                if internal_workout_type != 'plank' and len(landmark_seq) == seq_length:
                    if form_model is not None and form_label_encoder is not None:
                        input_data = np.expand_dims(np.array(landmark_seq), axis=0)
                        try:
                            form_probs = form_model.predict(input_data, verbose=0)
                            form_pred_label = form_label_encoder.inverse_transform(np.argmax(form_probs, axis=1))[0]
                        except Exception as e:
                            print(f"Error predicting form: {e}")
                            form_pred_label = None

                    angles = []
                    for lm_indices in config['landmarks']:
                        a, b, c = lm_indices
                        angle = calculate_angle([lm[a].x, lm[a].y], [lm[b].x, lm[b].y], [lm[c].x, lm[c].y])
                        angles.append(angle)

                    if not form_pred_label or form_pred_label not in config['form_labels']:
                        if internal_workout_type == 'pushups':
                            back_angle = angles[1] if len(angles) > 1 else 180
                            form_pred_label = "pushupsgood" if 175 <= back_angle <= 183 and angles[0] > 165 and lm[11].y < 0.35 else "pushupsbad"
                        elif internal_workout_type == 'curls':
                            form_pred_label = "curlsgood" if angles[0] < 25 or angles[0] > 170 else "curlsbad"
                        elif internal_workout_type == 'situps':
                            form_pred_label = "situpsgood" if angles[0] < 50 else "situpsbad"
                        elif internal_workout_type == 'squats':
                            form_pred_label = "squatsgood" if angles[0] < 70 else "squatsbad"

                    if 'angle_ranges' in config:
                        up_range = config['angle_ranges']['up']
                        down_range = config['angle_ranges']['down']
                        main_angle = angles[0]
                        extra_condition = config.get('extra_condition', lambda lm: True)

                        if (up_range[0] <= main_angle <= up_range[1] and
                                (len(up_range) <= 2 or (up_range[2] <= angles[1] <= up_range[3] if len(angles) > 1 else True))):
                            stage = "up"
                        if (down_range[0] <= main_angle <= down_range[1] and stage == "up" and
                                extra_condition(lm)):
                            stage = "down"
                            rep_counts[internal_workout_type] += 1
                            rep_counts[f"{internal_workout_type}_good" if form_pred_label.endswith("good") else f"{internal_workout_type}_bad"] += 1
                            calories += config['calories_per_rep']
                            print(f"{internal_workout_type.capitalize()} #{rep_counts[internal_workout_type]} | Form: {'Good' if form_pred_label.endswith('good') else 'Bad'} | 🔥 {calories:.1f} cal")

                elif internal_workout_type == 'plank':
                    angles = []
                    for lm_indices in config['landmarks']:
                        a, b, c = lm_indices
                        angle = calculate_angle([lm[a].x, lm[a].y], [lm[b].x, lm[b].y], [lm[c].x, lm[c].y])
                        angles.append(angle)

                    plank_angle = angles[0] if angles else 180
                    extra_condition = config.get('extra_condition', lambda lm: True)
                    in_plank_position = (config['angle_ranges']['plank'][0] <= plank_angle <= config['angle_ranges']['plank'][1] and
                                        extra_condition(lm))

                    if len(landmark_seq) == seq_length:
                        if form_model is not None and form_label_encoder is not None:
                            input_data = np.expand_dims(np.array(landmark_seq), axis=0)
                            try:
                                form_probs = form_model.predict(input_data, verbose=0)
                                form_pred_label = form_label_encoder.inverse_transform(np.argmax(form_probs, axis=1))[0]
                            except Exception as e:
                                print(f"Error predicting form: {e}")
                                form_pred_label = None

                        if not form_pred_label or form_pred_label not in config['form_labels']:
                            form_pred_label = "plankgood" if in_plank_position else "plankbad"

                    if in_plank_position:
                        if plank_start_time is None:
                            plank_start_time = time.time()
                        plank_total_time += time.time() - plank_start_time
                        calories += (time.time() - plank_start_time) * config['calories_per_second']
                        print(f"Plank active: {int(plank_total_time)} sec | 🔥 {calories:.1f} cal")
                    else:
                        if plank_start_time is not None:
                            print("⏸️ Plank paused: Not in plank position")
                    plank_start_time = time.time() if in_plank_position else None

                mp_drawing.draw_landmarks(img_bgr, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)

                if form_pred_label:
                    border_color = (0, 255, 0) if form_pred_label.endswith("good") else (0, 0, 255)
                    cv2.rectangle(img_bgr, (0, 0), (img_bgr.shape[1], img_bgr.shape[0]), border_color, 10)

                y = 30
                if internal_workout_type != 'plank':
                    cv2.putText(img_bgr, f"{internal_workout_type}: {rep_counts[internal_workout_type]}", 
                                (10, y), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                    y += 30
                    cv2.putText(img_bgr, f"Good: {rep_counts[f'{internal_workout_type}_good']}", 
                                (10, y), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                    y += 30
                    cv2.putText(img_bgr, f"Bad: {rep_counts[f'{internal_workout_type}_bad']}", 
                                (10, y), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
                    y += 30
                else:
                    status = "Active" if in_plank_position else "Paused"
                    cv2.putText(img_bgr, f"Plank: {status}", (10, y), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                    y += 30
                    cv2.putText(img_bgr, f"Time: {int(plank_total_time)} sec", (10, y),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
                    y += 30
                cv2.putText(img_bgr, f"Calories: {calories:.1f}", (10, y), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)

            cv2.imshow('Workout', img_bgr)
            if cv2.waitKey(10) & 0xFF == ord('q'):
                break

    except Exception as e:
        print(f"Error during workout: {e}")
        return "error"

    finally:
        cap.release()
        cv2.destroyAllWindows()

        print(f"\n{internal_workout_type.capitalize()} Workout Summary:")
        if internal_workout_type != 'plank':
            print(f"  {internal_workout_type.capitalize()}: {rep_counts[internal_workout_type]} reps")
            print(f"  Good: {rep_counts[f'{internal_workout_type}_good']} reps")
            print(f"  Bad: {rep_counts[f'{internal_workout_type}_bad']} reps")
        else:
            print(f"  Plank Time: {int(plank_total_time)} sec")
        print(f"  Total Calories burned: {calories:.1f} cal")
        duration = plank_total_time if internal_workout_type == 'plank' else (time.time() - start_time) // 60

        if user_id:
            try:
                save_workout_data(
                    user_id=user_id,
                    reps_dict=rep_counts,
                    calories=round(calories, 1),
                    duration=int(duration),
                    plank_time=int(plank_total_time) if internal_workout_type == 'plank' else 0
                )
                print(f"Data saved to Firestore for user {user_id}")
            except Exception as e:
                print(f"Error saving workout data: {e}")
        else:
            print("No user_id provided — workout data not saved.")

    return "done"

if __name__ == "__main__":
    start_workout(workout_type='curl', user_id='test_user')
# data_collector.py

import cv2
import mediapipe as mp
import numpy as np
import pandas as pd
import time
import os
from datetime import datetime

# Setup MediaPipe
mp_pose = mp.solutions.pose
pose = mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)
mp_drawing = mp.solutions.drawing_utils

# Create output directory
os.makedirs("collected_data", exist_ok=True)

def extract_landmarks(landmarks):
    """
    Flattens 33 pose landmarks into a list of 99 values: [x1, y1, z1, x2, y2, z2, ..., x33, y33, z33]
    """
    data = []
    for lm in landmarks.landmark:
        data.extend([lm.x, lm.y, lm.z])
    return data

def collect_data(label, duration=5):
    cap = cv2.VideoCapture(0)
    data = []

    print(f"📹 Starting collection for label: '{label}'")
    print(f"⏳ Collecting for {duration} seconds. Get ready...")
    time.sleep(3)
    print("✅ Recording started!")

    start_time = time.time()

    while time.time() - start_time < duration:
        ret, frame = cap.read()
        if not ret:
            break

        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = pose.process(image)

        if results.pose_landmarks:
            features = extract_landmarks(results.pose_landmarks)
            features.append(label)
            data.append(features)

            # Optional: draw landmarks on screen
            image_bgr = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            mp_drawing.draw_landmarks(
                image_bgr, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)
            cv2.imshow('Collecting Data', image_bgr)
        else:
            cv2.imshow('Collecting Data', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

    # Save data to CSV
    df = pd.DataFrame(data)
    #columns = [f'x{i},y{i},z{i}' for i in range(33)]
   #flattened_columns = []
    #for triplet in columns:
    #    flattened_columns.extend(triplet.split(','))
    flattened_columns = [f'{coord}{i}' for i in range(33) for coord in ['x', 'y', 'z']]
    flattened_columns.append('label')
    df.columns = flattened_columns
    flattened_columns.append('label')
    df.columns = flattened_columns

    filename = f"collected_data/{label}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    df.to_csv(filename, index=False)
    print(f"💾 Data saved to {filename} with {len(df)} frames.")

if __name__ == "__main__":
    label = input("🏷️ Enter workout label (e.g., pushup, squat, etc.): ").strip().lower()
    collect_data(label)

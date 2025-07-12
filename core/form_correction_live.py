# form_correction_live.py
import cv2
import numpy as np
import mediapipe as mp
import joblib
from core.model_utils import extract_pose_row

# Load model and label encoder
model = joblib.load("classifier/model/form_classifier.pkl")
label_encoder = joblib.load("classifier/model/form_label_encoder.pkl")

mp_pose = mp.solutions.pose
pose = mp_pose.Pose()

def get_form_label(pose_landmarks):
    row = extract_pose_row(pose_landmarks)  # shape (99,)
    X = np.array([row])  # shape (1, 99)
    pred = model.predict(X)[0]
    label = label_encoder.inverse_transform([pred])[0]
    return label

def main():
    cap = cv2.VideoCapture(0)
    print("🟢 Starting form correction. Press 'q' to quit.")

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = pose.process(image_rgb)

        if result.pose_landmarks:
            label = get_form_label(result.pose_landmarks)

            if "good" in label:
                color = (0, 255, 0)  # Green
                text = "✅ Good Form"
            else:
                color = (0, 0, 255)  # Red
                text = "⚠️ Fix Form"

            # Draw border
            frame = cv2.rectangle(frame, (0, 0), (frame.shape[1], frame.shape[0]), color, 10)
            cv2.putText(frame, label.upper(), (30, 60), cv2.FONT_HERSHEY_SIMPLEX, 1.4, color, 3)

        cv2.imshow("Real-Time Form Correction", frame)

        if cv2.waitKey(10) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()

# classifier/predictor.py

import numpy as np
import joblib
from keras.models import load_model

MODEL_PATH = "classifier/model/workout_classifier.keras"      # your saved model path
LABEL_ENCODER_PATH = "classifier/model/label_encoder.pkl"    # your saved label encoder path

# Load model and label encoder once when module is imported
model = load_model(MODEL_PATH)
label_encoder = joblib.load(LABEL_ENCODER_PATH)

def preprocess_landmarks(landmarks, sequence_length=30):
    """
    landmarks: List or np.array of pose landmarks flattened [x0,y0,z0, x1,y1,z1, ...] for one frame
    Returns: np.array of shape (1, sequence_length, 99) padded or truncated
    """
    # For inference, we expect a sequence of frames, but if only one frame given,
    # you can pad with zeros or repeat frames.
    # Here, assume landmarks is a list of frames (list of lists)
    
    seq = np.array(landmarks, dtype=np.float32)
    if len(seq) < sequence_length:
        # pad with zeros at start
        pad_len = sequence_length - len(seq)
        pad = np.zeros((pad_len, seq.shape[1]), dtype=np.float32)
        seq = np.vstack([pad, seq])
    elif len(seq) > sequence_length:
        seq = seq[-sequence_length:]  # take last sequence_length frames

    return np.expand_dims(seq, axis=0)  # shape: (1, sequence_length, 99)

def predict_workout_type(landmark_sequence):
    """
    landmark_sequence: list of frames; each frame is list/array of 99 float features (x,y,z for 33 landmarks)
    Returns: predicted label string
    """
    X = preprocess_landmarks(landmark_sequence)
    preds = model.predict(X)  # shape (1, num_classes)
    pred_label_encoded = np.argmax(preds, axis=1)[0]
    pred_label = label_encoder.inverse_transform([pred_label_encoded])[0]
    return pred_label

# classifier/predictor.py

import numpy as np
import joblib
from keras.models import load_model

MODEL_PATH = "classifier/model/workout_classifier.keras"  
LABEL_ENCODER_PATH = "classifier/model/label_encoder.pkl"  

model = load_model(MODEL_PATH)
label_encoder = joblib.load(LABEL_ENCODER_PATH)

def preprocess_landmarks(landmarks, sequence_length=30):
    """
    landmarks: List or np.array of pose landmarks flattened [x0,y0,z0, x1,y1,z1, ...] for one frame
    Returns: np.array of shape (1, sequence_length, 99) padded or truncated
    """

    
    seq = np.array(landmarks, dtype=np.float32)
    if len(seq) < sequence_length:
        # pad with zeros at start
        pad_len = sequence_length - len(seq)
        pad = np.zeros((pad_len, seq.shape[1]), dtype=np.float32)
        seq = np.vstack([pad, seq])
    elif len(seq) > sequence_length:
        seq = seq[-sequence_length:]  

    return np.expand_dims(seq, axis=0)  

def predict_workout_type(landmark_sequence):
    """
    landmark_sequence: list of frames; each frame is list/array of 99 float features (x,y,z for 33 landmarks)
    Returns: predicted label string
    """
    X = preprocess_landmarks(landmark_sequence)
    preds = model.predict(X) 
    pred_label_encoded = np.argmax(preds, axis=1)[0]
    pred_label = label_encoder.inverse_transform([pred_label_encoded])[0]
    return pred_label

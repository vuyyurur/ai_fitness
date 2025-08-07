import pandas as pd
import numpy as np
import glob
from sklearn.preprocessing import LabelEncoder
from keras.utils import to_categorical

SEQUENCE_LENGTH = 30

def load_data(path='classifier/collected_data/*.csv'):
    all_sequences = []
    all_labels = []
    label_encoder = LabelEncoder()

    csv_files = glob.glob(path)
    raw_data = []

    for file in csv_files:
        try:
            df = pd.read_csv(file)
        except Exception as e:
            print(f"Could not read {file}: {e}")
            continue
        
        pose_cols = [col for col in df.columns if col != 'label']
        df[pose_cols] = df[pose_cols].apply(pd.to_numeric, errors='coerce')

        bad_rows = df[df[pose_cols].isnull().any(axis=1)]
        if not bad_rows.empty:
            print(f"File {file} has {len(bad_rows)} rows with invalid numeric data. These rows will be dropped.")
            df = df.dropna(subset=pose_cols)

        if len(df) < SEQUENCE_LENGTH:
            print(f"Skipping {file} because it has too few valid frames ({len(df)})")
            continue

        label = df['label'].iloc[0]
        df = df.drop('label', axis=1)
        raw_data.append((df.values, label))

    for frames, label in raw_data:
        for i in range(len(frames) - SEQUENCE_LENGTH + 1):
            seq = frames[i:i + SEQUENCE_LENGTH]
            all_sequences.append(seq)
            all_labels.append(label)

    if not all_sequences:
        raise ValueError("No valid sequences found. Check your CSV files and cleaning steps.")

    X = np.array(all_sequences, dtype=np.float32)
    y = label_encoder.fit_transform(all_labels)
    y = to_categorical(y)

    return X, y, label_encoder

def extract_pose_row(pose_landmarks):
    keypoints = []
    for lm in pose_landmarks.landmark:
        keypoints.extend([lm.x, lm.y, lm.z])
    return np.array(keypoints, dtype=np.float32)

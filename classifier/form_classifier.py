import os
import numpy as np
import pandas as pd
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from keras.models import Sequential
from keras.layers import LSTM, Dense, Dropout
from keras.utils import to_categorical
from keras.callbacks import EarlyStopping

WINDOW_SIZE = 30
FEATURE_COUNT = 99
DATA_DIR = 'collected_data_goodbad'

def load_data():
    X = []
    y = []

    for filename in os.listdir(DATA_DIR):
        if not filename.endswith(".csv"):
            continue

        filepath = os.path.join(DATA_DIR, filename)
        df = pd.read_csv(filepath)

        if 'label' in df.columns:
            df_features = df.drop(columns=['label'])
        else:
            df_features = df

        if df_features.shape[1] != FEATURE_COUNT:
            print(f"⛔ Skipped {filename} — wrong number of features (expected {FEATURE_COUNT}, got {df_features.shape[1]})")
            continue

        if df_features.shape[0] < WINDOW_SIZE:
            print(f"⛔ Skipped {filename} — only {df_features.shape[0]} frames (need ≥ {WINDOW_SIZE})")
            continue

        for start in range(df_features.shape[0] - WINDOW_SIZE + 1):
            window = df_features.iloc[start:start + WINDOW_SIZE].values
            X.append(window)

            if 'label' in df.columns:
                label_series = df['label']
                label = label_series.iloc[0] 
                y.append(label)
            else:
                print(f"⚠️ Skipped {filename} — no 'label' column found")
                continue


    if len(X) == 0:
        raise ValueError("No valid samples found.")

    X = np.array(X)
    y = np.array(y)

    # Encode labels to one-hot vectors
    le = LabelEncoder()
    y_encoded = le.fit_transform(y)
    y_categorical = to_categorical(y_encoded)

    print("Form classifier label classes:", le.classes_)


    print(f"Loaded {X.shape[0]} samples with shape {X.shape[1:]} features")
    print(f"Labels: {list(le.classes_)}")
    return X, y_categorical, le

def build_model(input_shape, num_classes):
    model = Sequential([
        LSTM(64, return_sequences=True, input_shape=input_shape),
        Dropout(0.4),

        LSTM(64, return_sequences=True),
        Dropout(0.4),

        LSTM(32),
        Dropout(0.5),

        Dense(64, activation='relu'),
        Dropout(0.4),

        Dense(num_classes, activation='softmax')
    ])

    model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
    return model

def main():
    X, y, label_encoder = load_data()

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, stratify=y, test_size=0.2, random_state=42
    )

    model = build_model(input_shape=(WINDOW_SIZE, FEATURE_COUNT), num_classes=y.shape[1])

    noise = np.random.normal(0, 0.003, X_train.shape)
    X_train_noisy = X_train + noise

    early_stop = EarlyStopping(monitor='val_loss', patience=5, restore_best_weights=True)

    model.fit(
        X_train_noisy, y_train,
        epochs=25,
        validation_data=(X_test, y_test),
        callbacks=[early_stop]
    )

    model.save("form_classifier_model.keras")
    import joblib
    joblib.dump(label_encoder, "form_label_encoder.pkl")

if __name__ == "__main__":
    main()

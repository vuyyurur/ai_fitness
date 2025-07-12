# classifier/train_classifier.py
from keras.models import Sequential
from keras.layers import LSTM, Dense, Dropout, Input
import numpy as np
from sklearn.model_selection import train_test_split
from core.model_utils import load_data
from keras.callbacks import EarlyStopping
import joblib

X, y, label_encoder = load_data()
X_train, X_test, y_train, y_test = train_test_split(X, y, stratify=y, test_size=0.2)

model = Sequential([
    #Input(shape=(30, 99)),
    LSTM(64, return_sequences=True, input_shape=(30, 99)),
    Dropout(0.4),  # 🔸 Increased

    LSTM(64, return_sequences=True),
    Dropout(0.4),  # 🔸 New: dropout between stacked LSTM layers

    LSTM(32),  # 🔸 Smaller LSTM to regularize further
    Dropout(0.5),  # 🔸 More aggressive dropout

    Dense(64, activation='relu'),
    Dropout(0.4),  # 🔸 Dropout after dense layer

    Dense(y.shape[1], activation='softmax')
])


model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
print(f"✅ X_train shape: {X_train.shape}, dtype: {X_train.dtype}")
print(f"✅ y_train shape: {y_train.shape}, dtype: {y_train.dtype}")
print(f"✅ Labels: {label_encoder.classes_}")
noise = np.random.normal(loc=0.0, scale=0.003, size=X_train.shape)
X_train_noisy = X_train + noise


model.fit(X_train_noisy, y_train, epochs=25, validation_data=(X_test, y_test))

model.save("classifier/model/workout_classifier.keras")
joblib.dump(label_encoder, "classifier/model/label_encoder.pkl")


#!/usr/bin/env python
# coding: utf-8

# In[1]:


import os
import cv2
import numpy as np
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import TimeDistributed, LSTM, Dense, Conv2D, MaxPooling2D, Flatten
from tensorflow.keras.utils import to_categorical
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split


# In[2]:


# ---------------- Configuration ----------------
FRAME_COUNT = 70              # Capture ~7 seconds if sampling every 3rd frame at 30 FPS
IMG_HEIGHT, IMG_WIDTH = 64, 64
CHANNELS = 3
SAMPLE_RATE = 3               # Capture every 3rd frame to reduce load
DATASET_PATH = "dataset"      # Folder structure: dataset/class_name/video.mp4


# In[3]:


# ---------------- Helper Function ----------------
def load_video_frames(video_path, max_frames=FRAME_COUNT, sample_rate=SAMPLE_RATE):
    cap = cv2.VideoCapture(video_path)
    frames = []
    count = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        if count % sample_rate == 0:
            frame = cv2.resize(frame, (IMG_WIDTH, IMG_HEIGHT))
            frame = frame / 255.0
            frames.append(frame)
        count += 1
        if len(frames) >= max_frames:
            break

    cap.release()
    while len(frames) < max_frames:
        frames.append(np.zeros((IMG_HEIGHT, IMG_WIDTH, CHANNELS)))

    return np.array(frames)


# In[4]:


# ---------------- Load Dataset ----------------
X, y = [], []
if not os.path.exists(DATASET_PATH):#download mminimum 10 seconds (4)videos from Youtube and make the folder look like the below structure
    print(f"❌ Folder '{DATASET_PATH}' not found! Create it and add videos like:")
    print("dataset/")
    print(" ├── action/")
    print(" │   ├── video1.mp4")
    print(" │   └── video2.mp4")
    print(" └── dance/")
    print("     ├── dance1.mp4")
    print("     └── dance2.mp4")
    exit()

for label in os.listdir(DATASET_PATH):
    class_folder = os.path.join(DATASET_PATH, label)
    if os.path.isdir(class_folder):
        for video_file in os.listdir(class_folder):
            if video_file.lower().endswith((".mp4", ".avi", ".mov", ".mkv")):
                video_path = os.path.join(class_folder, video_file)
                frames = load_video_frames(video_path)
                X.append(frames)
                y.append(label)
                print(f"✅ Loaded: {video_file} ({label})")

X = np.array(X)
y = np.array(y)


# In[5]:


# ---------------- Label Encoding ----------------
le = LabelEncoder()
y = le.fit_transform(y)
y = to_categorical(y)


# In[6]:


# ---------------- Split Dataset ----------------
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)


# In[7]:


# ---------------- Build Model ----------------
model = Sequential()
model.add(TimeDistributed(Conv2D(32, (3, 3), activation='relu'),
                          input_shape=(FRAME_COUNT, IMG_HEIGHT, IMG_WIDTH, CHANNELS)))
model.add(TimeDistributed(MaxPooling2D((2, 2))))
model.add(TimeDistributed(Conv2D(64, (3, 3), activation='relu')))
model.add(TimeDistributed(MaxPooling2D((2, 2))))
model.add(TimeDistributed(Flatten()))
model.add(LSTM(64))
model.add(Dense(64, activation='relu'))
model.add(Dense(y.shape[1], activation='softmax'))

model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
model.summary()


# In[8]:


# ---------------- Train Model ----------------
print("\n🚀 Training the model...\n")
model.fit(X_train, y_train, epochs=10, batch_size=2, validation_data=(X_test, y_test))


# In[9]:


# ---------------- Evaluate ----------------
loss, acc = model.evaluate(X_test, y_test)
print(f"\n✅ Test Accuracy: {acc * 100:.2f}%")


# In[10]:


# ---------------- Predict (Demo) ----------------
print("\n🎥 Running a demo prediction:")
demo_video = os.path.join(DATASET_PATH, os.listdir(os.path.join(DATASET_PATH, os.listdir(DATASET_PATH)[0]))[0])
demo_frames = load_video_frames(demo_video)
demo_input = np.expand_dims(demo_frames, axis=0)
pred = model.predict(demo_input)
pred_label = le.inverse_transform([np.argmax(pred)])
print(f"Predicted class: {pred_label[0]}")


# In[ ]:





# In[ ]:





# In[ ]:





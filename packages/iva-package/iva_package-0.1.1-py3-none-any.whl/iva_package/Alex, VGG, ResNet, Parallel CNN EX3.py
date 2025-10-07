#!/usr/bin/env python
# coding: utf-8

# In[1]:


# Import required libraries
import os
import numpy as np
import matplotlib.pyplot as plt
import tensorflow as tf
from tensorflow.keras import layers, models, Input
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import ReduceLROnPlateau, EarlyStopping


# In[2]:

train_dir = "./cars-dataset-main/train"
test_dir = "./cars-dataset-main/test"


# In[3]:


# Image size and batch size
img_width, img_height = 128, 128
batch_size = 32
num_classes = 7


# In[4]:


# Data generators
train_datagen = ImageDataGenerator(
    rescale=1./255,
    rotation_range=10,
    horizontal_flip=True,
    zoom_range=0.2,
    width_shift_range=0.2,
    height_shift_range=0.2
)
test_datagen = ImageDataGenerator(rescale=1./255)


# In[5]:


train_generator = train_datagen.flow_from_directory(
    train_dir,
    target_size=(img_width, img_height),
    batch_size=batch_size,
    class_mode="sparse",
    shuffle=True
)


# In[6]:


test_generator = test_datagen.flow_from_directory(
    test_dir,
    target_size=(img_width, img_height),
    batch_size=batch_size,
    class_mode="sparse",
    shuffle=False
)


# In[7]:


num_classes = len(train_generator.class_indices)
print("Classes:", train_generator.class_indices)


# In[9]:


#AlexNet
def AlexNet():
    inp = Input((img_width, img_height, 3))
    x = layers.Conv2D(32, 3, activation='relu')(inp)
    x = layers.MaxPooling2D(2)(x)
    x = layers.Conv2D(64, 3, activation='relu')(x)
    x = layers.MaxPooling2D(2)(x)
    x = layers.Flatten()(x)
    x = layers.Dense(256, activation='relu')(x)  # reduced from 4096
    x = layers.Dropout(0.3)(x)
    x = layers.Dense(128, activation='relu')(x)
    x = layers.Dropout(0.3)(x)
    out = layers.Dense(num_classes, activation='softmax')(x)
    return models.Model(inputs=inp, outputs=out)

model_alex = AlexNet()
model_alex.summary()

# Compile
model_alex.compile(
    optimizer=Adam(1e-4),
    loss='sparse_categorical_crossentropy',
    metrics=['accuracy']
)

# Callbacks
callbacks = [
    ReduceLROnPlateau(monitor='val_loss', factor=0.2, patience=3, min_lr=1e-6, verbose=1),
    EarlyStopping(monitor='val_loss', patience=5, restore_best_weights=True, verbose=1)
]

# Train
history_alex = model_alex.fit(
    train_generator,
    validation_data=test_generator,
    epochs=2,
    callbacks=callbacks
)

# Evaluate
loss, acc = model_alex.evaluate(test_generator)
print(f"AlexNet Test Accuracy: {acc*100:.2f}%")

# Plot
plt.figure(figsize=(12,4))
plt.subplot(1,2,1)
plt.plot(history_alex.history['loss'], label='Train Loss')
plt.plot(history_alex.history['val_loss'], label='Val Loss')
plt.legend(); plt.title("AlexNet Loss")
plt.subplot(1,2,2)
plt.plot(history_alex.history['accuracy'], label='Train Acc')
plt.plot(history_alex.history['val_accuracy'], label='Val Acc')
plt.legend(); plt.title("AlexNet Accuracy")
plt.show()


# In[10]:


#VGGNet
def VGGNet():
    inp = Input((img_width, img_height, 3))
    x = layers.Conv2D(32, 3, activation='relu', padding='same')(inp)
    x = layers.Conv2D(32, 3, activation='relu', padding='same')(x)
    x = layers.MaxPooling2D(2)(x)

    x = layers.Conv2D(64, 3, activation='relu', padding='same')(x)
    x = layers.Conv2D(64, 3, activation='relu', padding='same')(x)
    x = layers.MaxPooling2D(2)(x)

    x = layers.Flatten()(x)
    x = layers.Dense(256, activation='relu')(x)  # reduced
    x = layers.Dropout(0.3)(x)
    out = layers.Dense(num_classes, activation='softmax')(x)
    return models.Model(inputs=inp, outputs=out)

model_vgg = VGGNet()
model_vgg.summary()
model_vgg.compile(optimizer=Adam(1e-4), loss='sparse_categorical_crossentropy', metrics=['accuracy'])

history_vgg = model_vgg.fit(train_generator, validation_data=test_generator, epochs=2, callbacks=callbacks)
loss, acc = model_vgg.evaluate(test_generator)
print(f"VGG Test Accuracy: {acc*100:.2f}%")

plt.figure(figsize=(12,4))
plt.subplot(1,2,1)
plt.plot(history_vgg.history['loss'], label='Train Loss')
plt.plot(history_vgg.history['val_loss'], label='Val Loss')
plt.legend(); plt.title("VGG Loss")
plt.subplot(1,2,2)
plt.plot(history_vgg.history['accuracy'], label='Train Acc')
plt.plot(history_vgg.history['val_accuracy'], label='Val Acc')
plt.legend(); plt.title("VGG Accuracy")
plt.show()


# In[12]:


#Resnet34
def residual_block(x, filters, kernel_size=3, stride=1):
    if x.shape[-1] != filters:
        shortcut = layers.Conv2D(filters, 1, strides=stride, padding='same')(x)
    else:
        shortcut = x
    x = layers.Conv2D(filters, kernel_size, padding='same', activation='relu')(x)
    x = layers.Conv2D(filters, kernel_size, padding='same')(x)
    x = layers.add([shortcut, x])
    x = layers.Activation('relu')(x)
    return x

def ResNet34():
    inp = Input((img_width, img_height, 3))
    x = layers.Conv2D(32, 3, activation='relu')(inp)
    x = residual_block(x, 32)
    x = layers.MaxPooling2D(2)(x)
    x = residual_block(x, 64)
    x = layers.MaxPooling2D(2)(x)
    x = layers.Flatten()(x)
    x = layers.Dense(256, activation='relu')(x)
    x = layers.Dropout(0.3)(x)
    out = layers.Dense(num_classes, activation='softmax')(x)
    return models.Model(inputs=inp, outputs=out)

model_res = ResNet34()
model_res.summary()
model_res.compile(optimizer=Adam(1e-4), loss='sparse_categorical_crossentropy', metrics=['accuracy'])

history_res = model_res.fit(train_generator, validation_data=test_generator, epochs=2, callbacks=callbacks)
loss, acc = model_res.evaluate(test_generator)
print(f"ResNet Test Accuracy: {acc*100:.2f}%")

plt.figure(figsize=(12,4))
plt.subplot(1,2,1)
plt.plot(history_res.history['loss'], label='Train Loss')
plt.plot(history_res.history['val_loss'], label='Val Loss')
plt.legend(); plt.title("ResNet Loss")
plt.subplot(1,2,2)
plt.plot(history_res.history['accuracy'], label='Train Acc')
plt.plot(history_res.history['val_accuracy'], label='Val Acc')
plt.legend(); plt.title("ResNet Accuracy")
plt.show()


# In[13]:


#Parallel CNN
def ParallelCNN():
    inp = Input((img_width, img_height, 3))

    # Branch 1
    x1 = layers.Conv2D(32, 3, activation='relu', padding='same')(inp)
    x1 = layers.MaxPooling2D(2)(x1)
    x1 = layers.Conv2D(64, 3, activation='relu', padding='same')(x1)
    x1 = layers.MaxPooling2D(2)(x1)
    x1 = layers.Flatten()(x1)

    # Branch 2
    x2 = layers.Conv2D(32, 5, activation='relu', padding='same')(inp)
    x2 = layers.MaxPooling2D(2)(x2)
    x2 = layers.Conv2D(64, 5, activation='relu', padding='same')(x2)
    x2 = layers.MaxPooling2D(2)(x2)
    x2 = layers.Flatten()(x2)

    # Combine
    x = layers.concatenate([x1, x2])
    x = layers.Dense(256, activation='relu')(x)
    x = layers.Dropout(0.3)(x)
    out = layers.Dense(num_classes, activation='softmax')(x)
    return models.Model(inputs=inp, outputs=out)

model_parallel = ParallelCNN()
model_parallel.summary()
model_parallel.compile(optimizer=Adam(1e-4), loss='sparse_categorical_crossentropy', metrics=['accuracy'])

history_parallel = model_parallel.fit(train_generator, validation_data=test_generator, epochs=2, callbacks=callbacks)
loss, acc = model_parallel.evaluate(test_generator)
print(f"Parallel CNN Test Accuracy: {acc*100:.2f}%")

plt.figure(figsize=(12,4))
plt.subplot(1,2,1)
plt.plot(history_parallel.history['loss'], label='Train Loss')
plt.plot(history_parallel.history['val_loss'], label='Val Loss')
plt.legend(); plt.title("Parallel CNN Loss")
plt.subplot(1,2,2)
plt.plot(history_parallel.history['accuracy'], label='Train Acc')
plt.plot(history_parallel.history['val_accuracy'], label='Val Acc')
plt.legend(); plt.title("Parallel CNN Accuracy")
plt.show()


# In[ ]:





# In[ ]:





# In[ ]:





#!/usr/bin/env python
# coding: utf-8

# In[1]:


#MNIST using Keras EX2:
import numpy as np
import matplotlib.pyplot as plt
from tensorflow.keras.datasets import mnist
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout, Flatten, Conv2D, MaxPooling2D ,Input
from tensorflow.keras.utils import to_categorical


# In[2]:


# Load MNIST
(x_train, y_train), (x_test, y_test) = mnist.load_data()
x_train = x_train.reshape(-1,28,28,1).astype('float32')/255
x_test = x_test.reshape(-1,28,28,1).astype('float32')/255
y_train = to_categorical(y_train, 10)
y_test = to_categorical(y_test, 10)


# In[3]:


# Create CNN model
model = Sequential()
model.add(Input(shape=(28,28,1)))
model.add(Conv2D(32, kernel_size=(5,5), activation='relu'))
model.add(MaxPooling2D(pool_size=(2,2)))
model.add(Conv2D(64, (3,3), activation='relu'))
model.add(MaxPooling2D(pool_size=(2,2)))
model.add(Flatten())
model.add(Dense(128, activation='relu'))
model.add(Dropout(0.3))
model.add(Dense(64, activation='relu'))
model.add(Dropout(0.5))
model.add(Dense(10, activation='softmax'))


# In[4]:


# Compile model
model.compile(loss='categorical_crossentropy', optimizer='adadelta', metrics=['accuracy'])


# In[5]:


# Train model
model.fit(x_train, y_train, batch_size=128, epochs=10, validation_data=(x_test, y_test))


# In[6]:


# Evaluate
score = model.evaluate(x_test, y_test, verbose=0)
print('Test loss:', score[0])
print('Test accuracy:', score[1]*100)


# In[7]:


# Predict and display an image
image_index = int(input("Enter image index (0-9999): "))
img = x_test[image_index].reshape(1,28,28,1)
predicted_class = np.argmax(model.predict(img))
plt.imshow(x_test[image_index].reshape(28,28), cmap='gray')
plt.title(f'Predicted class: {predicted_class}')
plt.axis('off')
plt.show()


# In[ ]:





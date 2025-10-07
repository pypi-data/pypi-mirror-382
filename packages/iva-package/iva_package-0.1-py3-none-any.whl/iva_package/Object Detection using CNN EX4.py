#!/usr/bin/env python
# coding: utf-8

# In[2]:


import tensorflow as tf
from tensorflow.keras import layers, models
import numpy as np
import matplotlib.pyplot as plt


# In[3]:


X, y_boxes, y_labels = [], [], []
for _ in range(100):
    img = np.zeros((100,100,3))
    x1, y1 = np.random.randint(10,60,2)
    x2, y2 = x1+np.random.randint(10,30), y1+np.random.randint(10,30)
    img[y1:y2, x1:x2] = np.random.rand(3)
    X.append(img)
    y_boxes.append([x1/100, y1/100, x2/100, y2/100])
    y_labels.append(np.random.randint(0,3))
X = np.array(X); y_boxes = np.array(y_boxes); y_labels = np.array(y_labels)


# In[4]:


# ------------------ Build simple CNN ------------------
inp = layers.Input((100,100,3))
x = layers.Conv2D(16,3,activation='relu',padding='same')(inp)
x = layers.MaxPooling2D(2)(x)
x = layers.Conv2D(32,3,activation='relu',padding='same')(x)
x = layers.MaxPooling2D(2)(x)
x = layers.Flatten()(x)
x = layers.Dense(64,activation='relu')(x)

bbox_out = layers.Dense(4,activation='sigmoid',name='bbox')(x)
class_out = layers.Dense(3,activation='softmax',name='class')(x)

model = models.Model(inp,[bbox_out,class_out])


# In[5]:


model.compile(optimizer='adam',
              loss={'bbox':'mse','class':'sparse_categorical_crossentropy'},
              metrics={'bbox':'mae','class':'accuracy'})


# In[6]:


# ------------------ Train ------------------
model.fit(X, {'bbox':y_boxes,'class':y_labels}, epochs=5, batch_size=16, validation_split=0.2)


# In[7]:


# ------------------ Predict and visualize ------------------
idx = np.random.randint(len(X))
img, true_box, true_label = X[idx], y_boxes[idx], y_labels[idx]
pred_box, pred_class = model.predict(np.expand_dims(img,0))
pred_box, pred_class = pred_box[0], np.argmax(pred_class[0])

plt.imshow(img)
plt.gca().add_patch(plt.Rectangle((true_box[0]*100,true_box[1]*100),
                                  (true_box[2]-true_box[0])*100,
                                  (true_box[3]-true_box[1])*100,
                                  fill=False,color='green',linewidth=2))
plt.gca().add_patch(plt.Rectangle((pred_box[0]*100,pred_box[1]*100),
                                  (pred_box[2]-pred_box[0])*100,
                                  (pred_box[3]-pred_box[1])*100,
                                  fill=False,color='red',linewidth=2))
plt.title(f"True: {true_label}, Pred: {pred_class}")
plt.show()


# In[ ]:





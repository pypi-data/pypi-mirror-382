#!/usr/bin/env python
# coding: utf-8

# In[1]:


get_ipython().system('pip install ultralytics opencv-python matplotlib')
get_ipython().system('pip install "numpy<2" --force-reinstall')


# In[2]:


from ultralytics import YOLO
import cv2
from matplotlib import pyplot as plt
model = YOLO("yolov8n.pt") 
img_path = "yolo.jpg" # download any image which has few objects
img = cv2.imread(img_path)
results = model(img)
plt.figure(figsize=(10, 6))
plt.imshow(cv2.cvtColor(results[0].plot(), cv2.COLOR_BGR2RGB))
plt.axis('off')
plt.show()


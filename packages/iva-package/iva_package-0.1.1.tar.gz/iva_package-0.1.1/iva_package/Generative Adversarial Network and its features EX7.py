#!/usr/bin/env python
# coding: utf-8

# In[2]:


import tensorflow as tf
import matplotlib.pyplot as plt
import numpy as np


# In[3]:


# ----------------- Dataset -----------------
(x_train,_),(_,_) = tf.keras.datasets.mnist.load_data()
x_train = x_train/127.5 - 1
x_train = np.expand_dims(x_train,-1)
ds = tf.data.Dataset.from_tensor_slices(x_train).shuffle(60000).batch(256)


# In[4]:


# ----------------- Models -----------------
gen = tf.keras.Sequential([
    tf.keras.layers.Dense(7*7*256,input_shape=(100,),use_bias=False),
    tf.keras.layers.BatchNormalization(), tf.keras.layers.LeakyReLU(),
    tf.keras.layers.Reshape((7,7,256)),
    tf.keras.layers.Conv2DTranspose(128,5,strides=1,padding='same',use_bias=False),
    tf.keras.layers.BatchNormalization(), tf.keras.layers.LeakyReLU(),
    tf.keras.layers.Conv2DTranspose(64,5,2,'same',use_bias=False),
    tf.keras.layers.BatchNormalization(), tf.keras.layers.LeakyReLU(),
    tf.keras.layers.Conv2DTranspose(1,5,2,'same',activation='tanh')
])

disc = tf.keras.Sequential([
    tf.keras.layers.Conv2D(64,5,2,'same',input_shape=[28,28,1]),
    tf.keras.layers.LeakyReLU(), tf.keras.layers.Dropout(0.3),
    tf.keras.layers.Conv2D(128,5,2,'same'), tf.keras.layers.LeakyReLU(), tf.keras.layers.Dropout(0.3),
    tf.keras.layers.Flatten(), tf.keras.layers.Dense(1)
])


# In[5]:


# ----------------- Optimizers & Loss -----------------
ce = tf.keras.losses.BinaryCrossentropy(from_logits=True)
g_opt = tf.keras.optimizers.Adam(1e-4)
d_opt = tf.keras.optimizers.Adam(1e-4)


# In[6]:


# ----------------- Training -----------------
for epoch in range(2):   # 2 epochs for demo
    for real in ds:
        noise = tf.random.normal([real.shape[0],100])
        with tf.GradientTape() as gt, tf.GradientTape() as dt:
            fake = gen(noise)
            g_loss = ce(tf.ones_like(disc(fake)), disc(fake))
            d_loss = ce(tf.ones_like(disc(real)), disc(real)) + ce(tf.zeros_like(disc(fake)), disc(fake))
        g_opt.apply_gradients(zip(gt.gradient(g_loss,gen.trainable_variables),gen.trainable_variables))
        d_opt.apply_gradients(zip(dt.gradient(d_loss,disc.trainable_variables),disc.trainable_variables))
    print(f"Epoch {epoch+1}, Gen Loss:{g_loss:.4f}, Disc Loss:{d_loss:.4f}")
    
    # Show generated images
    noise = tf.random.normal([16,100])
    imgs = gen(noise)
    plt.figure(figsize=(4,4))
    for i in range(16):
        plt.subplot(4,4,i+1)
        plt.imshow((imgs[i,:,:,0]+1)/2,cmap='gray'); plt.axis('off')
    plt.show()


# In[ ]:





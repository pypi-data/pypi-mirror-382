#!/usr/bin/env python
# coding: utf-8

# In[1]:


# MNIST using Tensorflow EX1
import tensorflow as tf
import numpy as np


# In[2]:


tf.compat.v1.disable_eager_execution()


# In[3]:


# Load MNIST from tf.keras.datasets
(x_train, y_train), (x_test, y_test) = tf.keras.datasets.mnist.load_data()
x_train = x_train.reshape(-1, 784)/255.0
x_test = x_test.reshape(-1, 784)/255.0


# In[4]:


# One-hot encode labels and cast to float32
y_train = np.eye(10)[y_train].astype(np.float32)
y_test = np.eye(10)[y_test].astype(np.float32)


# In[5]:


# Placeholders
x = tf.compat.v1.placeholder(tf.float32, [None, 784])
y = tf.compat.v1.placeholder(tf.float32, [None, 10])


# In[6]:


# Model
W = tf.Variable(tf.zeros([784, 10]))
b = tf.Variable(tf.zeros([10]))
logits = tf.matmul(x, W) + b


# In[7]:


# Loss and optimizer
loss = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits(labels=y, logits=logits))
train = tf.compat.v1.train.GradientDescentOptimizer(0.5).minimize(loss)


# In[8]:


# Accuracy
accuracy = tf.reduce_mean(tf.cast(tf.equal(tf.argmax(logits,1), tf.argmax(y,1)), tf.float32))


# In[9]:


# Train
with tf.compat.v1.Session() as sess:
    sess.run(tf.compat.v1.global_variables_initializer())
    for _ in range(1000):
        idx = np.random.randint(0, x_train.shape[0], 100).tolist()  # <-- convert to list
        sess.run(train, feed_dict={x: x_train[idx], y: y_train[idx]})
    print("Test Accuracy:", sess.run(accuracy, feed_dict={x: x_test, y: y_test}))


# In[ ]:





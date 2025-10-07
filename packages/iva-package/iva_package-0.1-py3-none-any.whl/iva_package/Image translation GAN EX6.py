#!/usr/bin/env python
# coding: utf-8

# In[3]:


import tensorflow as tf
from tensorflow.keras import layers
import matplotlib.pyplot as plt
import os, tarfile


# In[4]:


# 1. Dataset
_URL = "http://efrosgans.eecs.berkeley.edu/pix2pix/datasets/facades.tar.gz"
path = tf.keras.utils.get_file("facades.tar.gz", origin=_URL)
extract_path = os.path.join(os.path.dirname(path), "facades")
if not os.path.exists(extract_path):
    with tarfile.open(path) as tar: tar.extractall(path=os.path.dirname(path))
PATH = extract_path


# In[5]:


IMG_SIZE = 256
train_files = tf.data.Dataset.list_files(os.path.join(PATH,"train/*.jpg"))
test_files = tf.data.Dataset.list_files(os.path.join(PATH,"test/*.jpg"))


# In[6]:


def process_img(f):
    img = tf.image.decode_jpeg(tf.io.read_file(f))
    w = tf.shape(img)[1]//2
    inp, tar = img[:,:w,:], img[:,w:,:]
    inp = tf.image.resize(inp,[IMG_SIZE,IMG_SIZE])/127.5-1
    tar = tf.image.resize(tar,[IMG_SIZE,IMG_SIZE])/127.5-1
    return inp, tar

train_ds = train_files.map(process_img).shuffle(400).batch(1)
test_ds = test_files.map(process_img).batch(1)


# In[7]:


# 2. Generator & Discriminator
gen_input = tf.keras.Input([IMG_SIZE,IMG_SIZE,3])
x = layers.Conv2D(32,4,2,"same",activation="relu")(gen_input)
x = layers.Conv2DTranspose(3,4,2,"same",activation="tanh")(x)
gen = tf.keras.Model(gen_input,x)

disc_input = tf.keras.Input([IMG_SIZE,IMG_SIZE,3])
x = layers.Conv2D(32,4,2,"same",activation="relu")(disc_input)
x = layers.Conv2D(1,4,1,"same")(x)
disc = tf.keras.Model(disc_input,x)

gen_opt = tf.keras.optimizers.Adam(2e-4,0.5)
disc_opt = tf.keras.optimizers.Adam(2e-4,0.5)
bce = tf.keras.losses.BinaryCrossentropy(from_logits=True)


# In[8]:


# 3. Training Loop (short demo)
EPOCHS = 2
for epoch in range(EPOCHS):
    print(f"Epoch {epoch+1}")
    for inp, tar in train_ds.take(5):
        with tf.GradientTape() as g_tape, tf.GradientTape() as d_tape:
            gen_out = gen(inp, training=True)
            d_real = disc(tar, training=True)
            d_fake = disc(gen_out, training=True)
            g_loss = bce(tf.ones_like(d_fake), d_fake) + 100*tf.reduce_mean(tf.abs(tar-gen_out))
            d_loss = bce(tf.ones_like(d_real), d_real) + bce(tf.zeros_like(d_fake), d_fake)

        gen_grad = g_tape.gradient(g_loss, gen.trainable_variables)
        disc_grad = d_tape.gradient(d_loss, disc.trainable_variables)
        gen_opt.apply_gradients(zip(gen_grad, gen.trainable_variables))    # separate optimizer
        disc_opt.apply_gradients(zip(disc_grad, disc.trainable_variables))  # separate optimizer

        # show images
        plt.figure(figsize=(10,4))
        plt.subplot(1,3,1); plt.imshow((inp[0]+1)/2); plt.title("Input"); plt.axis("off")
        plt.subplot(1,3,2); plt.imshow((tar[0]+1)/2); plt.title("Target"); plt.axis("off")
        plt.subplot(1,3,3); plt.imshow((gen(inp,training=False)[0]+1)/2); plt.title("Generated"); plt.axis("off")
        plt.show()


# In[ ]:





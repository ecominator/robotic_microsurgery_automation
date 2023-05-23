import tensorflow as tf
import tensorflow.nn as nn
import tensorflow.keras as keras
from tensorflow.keras import layers
from tensorflow.keras import losses
from tensorflow.keras import optimizers
from tensorflow.keras import metrics
from tensorflow.keras import regularizers
from tensorflow.keras import activations
from tensorflow.keras import models
from tensorflow.keras import datasets
from tensorflow.keras import utils


def conv2d_block(input, filters_num, kernel_size, flag_batch_norm):
    for _ in range(2):
        x = layers.Conv2D(filters=filters_num, kernel_size=kernel_size, 
                        kernel_initializer='glorot_uniform', padding='same')(input) # he-normal
        if flag_batch_norm:
            x = layers.BatchNormalization(axis=-1)(x) 
        x = layers.Activation('relu')(x)
    return x


def build_model(input, filters_num, kernel_size, stride, dropout, flag_batch_norm):
    c1 = conv2d_block(input, filters_num*1, kernel_size, flag_batch_norm)
    p1 = layers.MaxPool2D((stride, stride))(c1)
    p1 = layers.Dropout(dropout)(p1)

    c2 = conv2d_block(p1, filters_num*2, kernel_size, flag_batch_norm)
    p2 = layers.MaxPool2D((stride, stride))(c2)
    p2 = layers.Dropout(dropout)(p2)

    c3 = conv2d_block(p2, filters_num*4, kernel_size, flag_batch_norm)
    p3 = layers.MaxPool2D((stride, stride))(c3)
    p3 = layers.Dropout(dropout)(p3)

    c4 = conv2d_block(p3, filters_num*8, kernel_size, flag_batch_norm)
    p4 = layers.MaxPool2D((stride, stride))(c4)
    p4 = layers.Dropout(dropout)(p4)
    
    c5 = conv2d_block(p4, filters_num*16, kernel_size, flag_batch_norm)
    
    u6 = layers.Conv2DTranspose(filters=filters_num*8, kernel_size=kernel_size,
                                strides=stride, padding='same')(c5)
    u6 = layers.concatenate([u6, c4], axis=-1)
    u6 = layers.Dropout(dropout)(u6)
    c6 = conv2d_block(u6, filters_num*8, kernel_size, flag_batch_norm)

    u7 = layers.Conv2DTranspose(filters=filters_num*4, kernel_size=kernel_size,
                                strides=stride, padding='same')(c6)
    u7 = layers.concatenate([u7, c3], axis=-1)
    u7 = layers.Dropout(dropout)(u7)
    c7 = conv2d_block(u7, filters_num*4, kernel_size, flag_batch_norm)

    u8 = layers.Conv2DTranspose(filters=filters_num*2, kernel_size=kernel_size,
                                strides=stride, padding='same')(c7)
    u8 = layers.concatenate([u8, c2], axis=-1)
    u8 = layers.Dropout(dropout)(u8)
    c8 = conv2d_block(u8, filters_num*2, kernel_size, flag_batch_norm)

    u9 = layers.Conv2DTranspose(filters=filters_num*1, kernel_size=kernel_size,
                                strides=stride, padding='same')(c8)
    u9 = layers.concatenate([u9, c1], axis=-1)
    u9 = layers.Dropout(dropout)(u9)
    c9 = conv2d_block(u9, filters_num*1, kernel_size, flag_batch_norm)
    
    output = layers.Conv2D(filters=1, kernel_size=1, activation='sigmoid')(c9) 
    model = models.Model(inputs=[input], outputs=[output])
    return model


def load_model(path, image_size, filters_num, kernel_size, stride, dropout, flag_batch_norm):
    input = layers.Input((image_size, image_size, 1), name='input')
    model = build_model(input, filters_num, kernel_size, stride, dropout, flag_batch_norm)
    model.load_weights(path)
    return model

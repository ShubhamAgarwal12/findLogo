# -*- coding: utf-8 -*-
"""
Created on Sat Dec 24 12:01:35 2016

@author: shubham
"""
import tensorflow as tf
import os
import cv2
import numpy as np
from tensorflow.examples.tutorials.mnist import input_data
from sklearn.preprocessing import OneHotEncoder
nlabel =2
batch_size = 100
test_size = 10

def init_weights(shape):
    return tf.Variable(tf.random_normal(shape, stddev=0.01))


def model(X, w, w2, w3, w4, w_o, p_keep_conv, p_keep_hidden):
    l1a = tf.nn.relu(tf.nn.conv2d(X, w,                       # l1a shape=(?, 64,128, 32)
                        strides=[1, 1, 1, 1], padding='SAME'))
    l1 = tf.nn.max_pool(l1a, ksize=[1, 2, 2, 1],              # l1 shape=(?, 32, 64, 32)
                        strides=[1, 2, 2, 1], padding='SAME')
    print l1
    #l1 = tf.nn.dropout(l1, p_keep_conv)

    l2a = tf.nn.relu(tf.nn.conv2d(l1, w2,                     # l2a shape=(?, 32, 64, 64)
                        strides=[1, 1, 1, 1], padding='SAME'))
    l2 = tf.nn.max_pool(l2a, ksize=[1, 2, 1, 1],              # l2 shape=(?, 16, 32, 64)
                        strides=[1, 2, 1, 1], padding='SAME')
    #l2 = tf.nn.dropout(l2, p_keep_conv)
    print l2
    
    l3a = tf.nn.relu(tf.nn.conv2d(l2, w3,                     # l3a shape=(?, 16,32, 128)
                        strides=[1, 1, 1, 1], padding='SAME'))
    l3 = tf.nn.max_pool(l3a, ksize=[1, 2, 2, 1],              # l3 shape=(?, 8,16, 128)
                        strides=[1, 2, 2, 1], padding='SAME')
    l3 = tf.reshape(l3, [-1, w4.get_shape().as_list()[0]])    # reshape to (?, 2048)
    #l3 = tf.nn.dropout(l3, p_keep_conv)
    print l3

    l4 = tf.nn.relu(tf.matmul(l3, w4))
    #l4 = tf.nn.dropout(l4, p_keep_hidden)

    pyx = tf.matmul(l4, w_o)
    return pyx

enc = OneHotEncoder()
trainData=[]
trainLabel =[]
testData=[]
testLabel=[]
convertToInt=[]
dict={'vodafone':1,'redbull':2,'ford':0,'hp':3}

files=os.listdir('test_Shubham/')
for f in files:
    im=cv2.imread('test_Shubham/'+f,0)
    im = cv2.resize(im,(128,64))
    trainData.append(im)
    trainLabel.append(dict[f.split('_')[1].split('.')[0]])

with open('testData.txt') as f:
    lines = f.readlines()

for line in lines:
    im=cv2.imread('probes/'+line.split('\t')[0],0)
    im = cv2.resize(im,(128,64))
    testData.append(im)
    testLabel.append(dict[line.split('\t')[1].strip()])    


trX = np.array(trainData)
teX = np.array(testData)
trX = trX.reshape(-1, 128,64, 1) 
teX = teX.reshape(-1,128,64, 1) 

enc.fit(trainLabel)
trY = trainLabel
b = np.zeros((1000, nlabel))
b[np.arange(1000), trY] = 1
trY =b
#enc.fit(testLabel)
teY = testLabel
b = np.zeros((10, nlabel))
b[np.arange(10), teY] = 1
teY =b

#mnist = input_data.read_data_sets("MNIST_data/", one_hot=True)
#trX, trY, teX, teY = mnist.train.images, mnist.train.labels, mnist.test.images, mnist.test.labels
#trX = trX.reshape(-1, 128, 28, 1)  # 28x28x1 input img
#teX = teX.reshape(-1, 28, 28, 1)  # 28x28x1 input img

X = tf.placeholder("float", [None, 128, 64, 1])
Y = tf.placeholder("float", [None, nlabel])

w = init_weights([5, 5, 1, 48])       # 3x3x1 conv, 32 outputs
w2 = init_weights([5, 5, 48, 64])     # 3x3x32 conv, 64 outputs
w3 = init_weights([5, 5, 64, 128])    # 3x3x32 conv, 128 outputs
w4 = init_weights([128 * 8 * 32, 2048]) # FC 128 * 4 * 4 inputs, 625 outputs
w_o = init_weights([2048, nlabel])         # FC 625 inputs, 10 outputs (labels)

p_keep_conv = tf.placeholder("float")
p_keep_hidden = tf.placeholder("float")
py_x = model(X, w, w2, w3, w4, w_o, p_keep_conv, p_keep_hidden)

cost = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits(py_x, Y))
train_op = tf.train.RMSPropOptimizer(0.01, 0.9).minimize(cost)
predict_op = tf.argmax(py_x, 1)

# Launch the graph in a session
with tf.Session() as sess:
    # you need to initialize all variables
    tf.initialize_all_variables().run()

    for i in range(100):
        training_batch = zip(range(0, len(trX), batch_size),
                             range(batch_size, len(trX)+1, batch_size))
        for start, end in training_batch:
            sess.run(train_op, feed_dict={X: trX[start:end], Y: trY[start:end],
                                          p_keep_conv: 0.8, p_keep_hidden: 0.5})

        test_indices = np.arange(len(teX)) # Get A Test Batch
        np.random.shuffle(test_indices)
        test_indices = test_indices[0:test_size]

        print(i, np.mean(np.argmax(teY[test_indices], axis=1) ==
                         sess.run(predict_op, feed_dict={X: teX[test_indices],
                                                         p_keep_conv: 1.0,
                                                         p_keep_hidden: 1.0})))

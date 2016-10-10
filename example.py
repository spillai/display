#!/usr/bin/env python

import numpy as np
import random
import time
import cv2

import display
display.set_port(9000)

def generate_image():
    X, Y = np.meshgrid(np.linspace(0, np.pi, 512), np.linspace(0, 2, 512))
    z = (np.sin(X) + np.cos(Y)) ** 2 + 0.5
    return z

i1 = generate_image()
i2 = generate_image()

display.image(i1, title='gradient')

# display.images([i2, i2, i2, i2], width=200, title='super fabio', labels=['a', 'b', 'c', 'd'])

data = []
for i in range(15):
    data.append([i, random.random(), random.random() * 2])

win = display.plot(data, labels=[ 'position', 'a', 'b' ], title='progress')

for i in range(15, 25):
    time.sleep(0.2)
    data.append([i, random.random(), random.random() * 2])
    display.plot(data, win=win)

im = cv2.imread('example.png')
display.image(im, to_bgr=False, title='png')

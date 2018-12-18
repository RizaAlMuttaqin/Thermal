#!/usr/bin/env python3
#
# Based on thermal.py
# Author: Dean Miller
# copyright (c) 2017 Adafruit Industries
#

# Can enable debug output by uncommenting:
#import logging
#logging.basicConfig(level=logging.DEBUG)

import sys
from time import sleep, time
import signal

import numpy as np

from Adafruit_AMG88xx import Adafruit_AMG88xx

import pygame
import unicornhathd as uh

filters = ((10,20),(30,35))

absolute = False
colour = True
filter = False
interpolate = True

if  (filters[0][0] != filters[0][1]) or (filters[1][0] != filters[1][1]):
    filter = True

def signal_handler(signal, frame):
    #print('You pressed Ctrl+C!')
    if gotx:
        pygame.quit()
    uh.off()
    sys.exit(0)


#    used by
#    #img2.append(list(map(proj2, img[size - 2], img[size - 1])))
def proj2(col1, col2):
    return ((col2 - col1) / 2) + col2


def centre(img):
    img1 = np.empty((16,16), dtype=np.float16)
    
    # centre image
    for v in range(len(img1)):
        #print(img[v])
        #  mid rows only
        if v >= 4 and v <= 11:
            img1[v][4:12] = img[v - 4]
            img1[v][0:4] = 0
            img1[v][12:16] = 0
        else:
            img1[v][0:16] = 0
    return img1

def inter(img):
    #print("inter(img)")
    #print(img)
    #print("len(img)")
    #print(len(img))
    img1 = np.empty((16,16), dtype=np.float16)
    
    # horizontally interpolate
    for v in range(len(img)):
        #print(img[v])
        # every even place is original
        img1[v * 2][::2] = img[v]
        #every other place is interpolated
        img1[v * 2][1:14:2] = [(img[v][i] + img[v][i + 1]) / 2 for i in range(len(img[v]) - 1)]
        # final place is extended from last two real
        img1[v * 2][-1] = proj2(img1[v * 2][-4], img1[v * 2][-2])
        #print(img1[v * 2])
        
    # vertically interpolate
    # new rows are average of adjacent rows
    # last row is  of  last two rows
    for v in range(1, len(img1) - 1, 2):
        #print("v")
        #print(v)
        #img1[v] = [(img1[v - 1][i] + img1[v + 1][i]) / 2 for i in range(len(img1[v]))]
        img1[v] = [(img1[v - 1][i] + img1[v + 1][i]) / 2 for i in range(len(img1[v]))]
        #print(img2)
    #print(len(img) - 1)
    #img2.append(img1[-1])
    img1[-1] = list(map(proj2, img1[-4], img1[-2]))
    #print(img1)
    return img1


def greyToRGB(grey):
# false colour map from greyscale to RGB colour
    r = grey
    b = grey
    g = grey
    if b < 128:
        b = 64 - abs(b - 64)
    elif b > 192:
        b = int((b - 192) * 4)
    else:
        b = 0
    if g > 128:
        g = int((g - 128) * 2)
    else:
        g = 0
    
    return r, g, b


gotx = False

try:
    signal.signal(signal.SIGINT, signal_handler)
    print('Press Ctrl+C to stop.')
    #signal.pause()
    
    # Default constructor will pick a default I2C bus.
    #
    # For the Raspberry Pi this means you should hook up to the only exposed I2C bus
    # from the main GPIO header and the library will figure out the bus number based
    # on the Pi's revision.
    sensor = Adafruit_AMG88xx()

    #wait for it to boot
    sleep(.1)
    
    # colset is palette of false colour map
    # create once for efficiency
    colsets = np.zeros((2, 256, 3), dtype=np.uint8)
    for bw in range(0, 256):
        # greyscale
        colsets[0][bw] = greyToRGB(bw)
        # colour set
        colsets[1][bw] = (bw, bw, bw)
    ##print("colset")
    ##print(colsets)
    
    #try:
    #    pygame.init()
    #    window = pygame.display.set_mode((16,16))
    #    gotx = True
    #except:
    #    pass
    
    uh.clear()
    #uh.rotation(90)
    uh.brightness(1)
    uh.show()
    
    a = 80
    z = 0
    while(1):
        print(time(), int(time() % 10), absolute, colour)
        
        if int(time() % 8) == 0:
            absolute = True
        elif int(time() % 8) == 4:
            absolute = False
        
        if int(time() % 16) == 0:
            colour = True
        elif int(time() % 16) == 8:
            colour = False

        if int(time() % 32) == 0:
            interpolate = True
        elif int(time() % 32) == 16:
            interpolate = False
        
        data = sensor.readPixels()
        #print("data={}".format(data))
        
        img = np.array(data).reshape(8, 8)
        #print("img")
        #print(img)
        
        if interpolate:
            # interpolate the image to 16 by 16
            img1 = inter(img)
        else:
            # centre image same size
            img1 = centre(img)
        #print("img1")
        #print(img1)
        
        # calculate min and max of current image
        a2 = np.min(img1)
        if a2 < a:
            a = a2
        else:
            # adjust to new higher min by a fifth of difference
            a = a + ((a2 - a) / 10)
        z2 = np.max(img1)
        if z2 > z:
            z = z2
        else:
            # adjust to new lower max by a fifth of difference
            z = z - ((z - z2) / 10)
        #print("a={}, z={}".format(a, z))
        #print("a={}, a2={}, z={}, z2={}".format(a, a2, z, z2))
        
        # apply filters
        #if filter:
        #    for f, i in filters:
        #        if img1 >= f[0] and img1 <= f[1]:
        #            #keep img data 

        # change from temperature to greyscale or colour
        if absolute:
            #img1 += -a
            img1 /= ((80 - 0) / 255)
            img2 = img1.astype(np.int)
            #using nump 1d interpolation
            #img2 = np.interp(img1.astype(np.int), (0, 80), (0, 255))
        else:
            img1 += -a
            img1 /= ((z - a) / 255)
            img2 = img1.astype(np.int)
            #using nump 1d interpolation
            #img2 = np.interp(img1.astype(np.int), (a, z), (0, 255))
        #print("img2 greyscale")
        #print(img2)
        
        #print("colset[img2]")
        #print(colset[img2])
        
        # map to RGB
        if colour:
            uh.set_pixels(colsets[1][img2])
        else:
            uh.set_pixels(colsets[0][img2])

        if gotx:
            window = pygame.surfarray.make_surface(colsets[1][img2])
            display.blit(window, (0, 0))
        
        uh.show()
        if gotx:
            pygame.display.update()
                
        #sleep(0.02)

except (KeyboardInterrupt, SystemExit):
    # quit by passing to the finally section
    raise

except Exception as e:
    print("Error: " + str(e))

finally:
    if gotx:
        pygame.quit()
    uh.off()
    sys.exit()

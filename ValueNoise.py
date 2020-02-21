import cv2
import numpy as np
import math
import random


class ValueNoise:
    def __init__(self, height, width, lattice, seed):
        self.height = height
        self.width = width
        self.lattice = lattice
        random.seed(seed)
        ilen = int(self.height / self.lattice) + 1
        jlen = int(self.width / self.lattice) + 1
        self.suppleMat = [[0 for i in range(ilen)] for i in range(jlen)]
        for i in range(ilen):
            for j in range(jlen):
                self.suppleMat[i][j] = (int)(255 * random.random())

    def fade_old(self, t):
        return t * t * (3 - 2 * t)

    def fade(self, t):
        return t * t * t * (t * (t * 6 - 15) + 10)

    def value_noise(self, smooth=0):
        dst = np.zeros((self.height, self.width), np.uint8)
        for i in range(0, self.height):
            for j in range(0, self.width):
                x = i / self.lattice
                y = j / self.lattice

                sx = math.floor(x)
                sy = math.floor(y)
                fx = x - sx
                fy = y - sy
                if smooth == 0:
                    cbufx = [math.floor((1.0 - fx) * 2048)]
                    cbufx.append(2048 - cbufx[0])
                    cbufy = [math.floor((1.0 - fy) * 2048)]
                    cbufy.append(2048 - cbufy[0])
                elif smooth == 1:
                    cbufx = [math.floor(self.fade_old(1.0 - fx) * 2048)]
                    cbufx.append(2048 - cbufx[0])
                    cbufy = [math.floor(self.fade_old(1.0 - fy) * 2048)]
                    cbufy.append(2048 - cbufy[0])
                else:
                    cbufx = [math.floor(self.fade(1.0 - fx) * 2048)]
                    cbufx.append(2048 - cbufx[0])
                    cbufy = [math.floor(self.fade(1.0 - fy) * 2048)]
                    cbufy.append(2048 - cbufy[0])
                dst[i, j] = (self.suppleMat[sx][sy] * cbufx[0] * cbufy[0] +
                             self.suppleMat[sx + 1][sy] * cbufx[1] * cbufy[0] +
                             self.suppleMat[sx][sy + 1] * cbufx[0] * cbufy[1] +
                             self.suppleMat[sx + 1][sy + 1] * cbufx[1] * cbufy[1]) >> 22
        return dst

    def show_pic(self):
        value_noise_no_fade = self.value_noise()
        value_noise_old_fade = self.value_noise(1)
        value_noise_new_fade = self.value_noise(2)
        cv2.imshow("value_noise_no_fade", value_noise_no_fade)
        cv2.imshow("value_noise_old_fade", value_noise_old_fade)
        cv2.imshow("value_noise_new_fade", value_noise_new_fade)
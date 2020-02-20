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

class PerlinNoise:
    def __init__(self, height, width, lattice):
        self.height = height
        self.width = width
        self.lattice = lattice
        self.p = []
        self.premutation = []
        '''
        self.premutation = [151, 160, 137, 91, 90, 15,
                            131, 13, 201, 95, 96, 53, 194, 233, 7, 225, 140, 36, 103, 30, 69, 142, 8, 99, 37, 240, 21,
                            10,
                            23,
                            190, 6, 148, 247, 120, 234, 75, 0, 26, 197, 62, 94, 252, 219, 203, 117, 35, 11, 32, 57, 177,
                            33,
                            88, 237, 149, 56, 87, 174, 20, 125, 136, 171, 168, 68, 175, 74, 165, 71, 134, 139, 48, 27,
                            166,
                            77, 146, 158, 231, 83, 111, 229, 122, 60, 211, 133, 230, 220, 105, 92, 41, 55, 46, 245, 40,
                            244,
                            102, 143, 54, 65, 25, 63, 161, 1, 216, 80, 73, 209, 76, 132, 187, 208, 89, 18, 169, 200,
                            196,
                            135, 130, 116, 188, 159, 86, 164, 100, 109, 198, 173, 186, 3, 64, 52, 217, 226, 250, 124,
                            123,
                            5, 202, 38, 147, 118, 126, 255, 82, 85, 212, 207, 206, 59, 227, 47, 16, 58, 17, 182, 189,
                            28, 42,
                            223, 183, 170, 213, 119, 248, 152, 2, 44, 154, 163, 70, 221, 153, 101, 155, 167, 43, 172, 9,
                            129, 22, 39, 253, 19, 98, 108, 110, 79, 113, 224, 232, 178, 185, 112, 104, 218, 246, 97,
                            228,
                            251, 34, 242, 193, 238, 210, 144, 12, 191, 179, 162, 241, 81, 51, 145, 235, 249, 14, 239,
                            107,
                            49, 192, 214, 31, 181, 199, 106, 157, 184, 84, 204, 176, 115, 121, 50, 45, 127, 4, 150, 254,
                            138, 236, 205, 93, 222, 114, 67, 29, 24, 72, 243, 141, 128, 195, 78, 66, 215, 61, 156, 180]
        '''
        for i in range(0,256):
            self.premutation.append(i)
        random.seed(0)
        random.shuffle(self.premutation)
        for i in range(0, 512):
            self.p.append(self.premutation[i % 256])

    def fade_old(self, t):
        return t * t * (3 - 2 * t)

    def fade(self, t):
        return t * t * t * (t * (t * 6 - 15) + 10)

    def lerp(self, t, a, b):
        return a + t * (b - a)

    def grad(self, has, x, y):
        h = has & 3
        if h == 0:
            return x
        elif h == 1:
            return -x
        elif h == 2:
            return y
        elif h == 3:
            return -y
        else:
            return 0
    def grad_old(self, has, x, y):
        h = has & 3
        if h == 0:
            return x+y
        elif h == 1:
            return x-y
        elif h == 2:
            return -x+y
        elif h == 3:
            return -x-y
        else:
            return 0

    def perlin_noise(self, x, y, smooth, dir):
        X = math.floor(x) & 255
        Y = math.floor(y) & 255
        x -= math.floor(x)
        y -= math.floor(y)
        if smooth == 0:
            u = self.fade(x)
            v = self.fade(y)
        else:
            u = self.fade_old(x)
            v = self.fade_old(y)

        AA = self.p[self.p[X] + Y]
        AB = self.p[self.p[X] + Y + 1]
        BA = self.p[self.p[X + 1] + Y]
        BB = self.p[self.p[X + 1] + Y + 1]
        if dir == 0:
            x1 = self.lerp(u, self.grad(AA, x, y), self.grad(BA, x - 1, y))
            x2 = self.lerp(u, self.grad(AB, x, y - 1), self.grad(BB, x - 1, y - 1))
        else:
            x1 = self.lerp(u, self.grad_old(AA, x, y), self.grad_old(BA, x - 1, y))
            x2 = self.lerp(u, self.grad_old(AB, x, y - 1), self.grad_old(BB, x - 1, y - 1))
        y = self.lerp(v, x1, x2)
        return (y + 1) / 2

    def octave_perlin(self,octaves,persistence):
        pass


    def perlin_noise_main(self, smooth=0, dir = 0):
        dst = np.zeros((self.height, self.width), np.uint8)
        for i in range(0, self.height):
            for j in range(0, self.width):
                x = i / lattice
                y = j / lattice
                dst[i, j] = 255 * self.perlin_noise(x, y, smooth, dir)
        return dst

    def show_pic(self):
        perlin_noise_old_fade = self.perlin_noise_main(1)
        perlin_noise_old_dir = self.perlin_noise_main(0,1)
        perlin_noise_old = self.perlin_noise_main(1,1)
        perlin_noise_new = self.perlin_noise_main()
        cv2.imshow("perlin_noise_old_fade", perlin_noise_old_fade)
        cv2.imshow("perlin_noise_old_dir", perlin_noise_old_dir)
        cv2.imshow("perlin_noise_old", perlin_noise_old)
        cv2.imshow("perlin_noise_new", perlin_noise_new)


# All_Used
dstWidth = 600
dstHeight = 600
lattice = 600
vn = ValueNoise(dstHeight, dstWidth, lattice, 0)
# vn.show_pic()

pn = PerlinNoise(dstHeight, dstWidth, lattice)
pn.show_pic()
cv2.waitKey(0)
# for lattice in range(40,100):
#     pn  = PerlinNoise(256,256,lattice)
#     pn.show_pic()
#     print("lattice:",lattice)
#     cv2.waitKey(600)

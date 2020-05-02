import cv2
import math
import os
import random as rnd
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
def image(image_dir):
    images = os.listdir(image_dir)
    if len(images) > 0:
        pic = Image.open(
            os.path.join(
                image_dir, images[rnd.randint(0, len(images) - 1)]
            )
        )
        #pic_mask=Image.new(
            #"RGB", (pic.size[0], pic.size[1]), (0, 0, 0))
        return pic
    else:
        raise Exception("No images where found in the images folder!")

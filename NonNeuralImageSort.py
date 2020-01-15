from PIL import Image
import os

im = Image.open('AfricaImage.png', 'C:\Documents')
pix_val = list(im.getdata())
print(pix_val)

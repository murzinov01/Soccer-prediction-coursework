import csv
import numpy as np
import pandas as pd
import seaborn as sb
import random
# from keras.applications.resnet50 import ResNet50
# from keras.preprocessing import image
# from keras.applications.resnet50 import preprocess_input
import PIL
from PIL import Image
from matplotlib import image
from matplotlib import pyplot
from word2vec_model import PlayerEmbedding
import multiprocessing
from numpy import asarray

def show_image(data):
    pyplot.matshow(data)
    pyplot.show()

# Принтуем картинку как array

# Создаем картинку из array и принтуем
# check = np.zeros((8, 8, 3))
# check[:, :, 2] = 255
# check[::2, 1::2, 0] = 255
# check[1::2, ::2, 1] = 255

Emb = PlayerEmbedding()
Emb.w2v_load()
Emb.normalize_all_vectors()

rgb_img_matrix = np.zeros((80, Emb.VEC_SIZE, 3))
print(rgb_img_matrix.shape)

count = 0
for vec in Emb.NORMALIZED_VECTORS.values():
    rgb_img_matrix[count] += Emb.convert_to_rgb(vec)
    if count >= 79:
        break
    count += 1

print(rgb_img_matrix)
new_array = np.uint8(rgb_img_matrix)

im = Image.fromarray(new_array)
im.show()
im.save("doska.png")




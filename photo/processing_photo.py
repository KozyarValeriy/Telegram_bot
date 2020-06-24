import os
import string
import random

from sklearn.cluster import KMeans
import skimage
from skimage import io
import numpy as np


class Photo:

    def __init__(self, url: str, n_clusters: int = 3):
        """ Метод инициализации объекта фото

        :param url: url до фото,
        :param n_clusters: кол-во цветов, которые надо оставить в фото
        """
        self.image = io.imread(url)
        self.photo_y = len(self.image)
        self.photo_x = len(self.image[0])
        self.n_clusters = n_clusters

    def get_result_photo(self) -> bytes:
        """ Метод для изменения кол-ва цветов фото на указанное в параметре self.n_clusters

        :return: результирующую картинку в байтах.
        """
        transform_image = skimage.img_as_float(self.image)
        # Создание матрицы объекты-признаки
        obj = np.reshape(transform_image, (self.photo_y * self.photo_x, len(transform_image[0][0])))

        # Обучение алгоритма К-средних
        k_means = KMeans(init='k-means++', n_clusters=self.n_clusters).fit(obj)
        n_clusters = k_means.n_clusters
        rgb_r = [list() for _ in range(n_clusters)]
        rgb_g = [list() for _ in range(n_clusters)]
        rgb_b = [list() for _ in range(n_clusters)]

        # Получение значений цветов RGB для каждого кластера
        for i in range(len(k_means.labels_)):
            rgb_r[k_means.labels_[i]].append(obj[i][0])
            rgb_g[k_means.labels_[i]].append(obj[i][1])
            rgb_b[k_means.labels_[i]].append(obj[i][2])

        # Медиана цветов по кластеру
        r_median = [np.median(rgb_r[i]) for i in range(n_clusters)]
        g_median = [np.median(rgb_g[i]) for i in range(n_clusters)]
        b_median = [np.median(rgb_b[i]) for i in range(n_clusters)]

        image_median = np.zeros((self.photo_y, self.photo_x, 3))

        # Сбор картинки по пикселям по цветам кластеров
        for pos, i in enumerate(k_means.labels_):
            pos_x = pos % self.photo_x
            pos_y = pos // self.photo_x
            image_median[pos_y][pos_x] = np.array([r_median[i], g_median[i], b_median[i]])

        file_name = "".join(random.choice(string.ascii_letters) for _ in range(20)) + ".png"
        io.imsave(file_name, skimage.img_as_ubyte(image_median))
        with open(file_name, "rb") as f:
            res_img = f.read()
        os.remove(file_name)
        return res_img

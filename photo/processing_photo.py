import asyncio
import os
import random
import string
from multiprocessing import Process, Queue
from typing import List

import numpy as np
import skimage
import skimage.io
from sklearn.cluster import KMeans
from telebot import asyncio_helper


class PhotoWorker(Process):

    def __init__(self, url: str, n_clusters: int = 3):
        """ Method for initialization an instance

        :param url: image's url,
        :param n_clusters: a number of colors to save in image
        """
        super().__init__()

        self.image = skimage.io.imread(url)
        self.photo_y = len(self.image)
        self.photo_x = len(self.image[0])
        self.n_clusters = n_clusters
        self._queue: Queue = Queue(1)

    @property
    def queue(self):
        return self._queue

    @staticmethod
    def _close_session():
        """ Without call this func getting error:

        Unclosed client session
        client_session: <aiohttp.client.ClientSession object at 0x00000235C9C1D520>
        """
        asyncio.run(asyncio_helper.session_manager.session.close())

    def run(self):
        """ Method for changing a number of colors in image

        :return: image in bytes
        """
        transform_image = skimage.img_as_float(self.image)
        # creating feature objects matrix
        obj = np.reshape(transform_image, (self.photo_y * self.photo_x, len(transform_image[0][0])))

        # Training K-means algorithm
        k_means = KMeans(init='k-means++', n_clusters=self.n_clusters).fit(obj)
        n_clusters = k_means.n_clusters
        rgb_r: List[list] = [list() for _ in range(n_clusters)]
        rgb_g: List[list] = [list() for _ in range(n_clusters)]
        rgb_b: List[list] = [list() for _ in range(n_clusters)]

        # Getting RGB colors for each cluster
        for i in range(len(k_means.labels_)):
            rgb_r[k_means.labels_[i]].append(obj[i][0])
            rgb_g[k_means.labels_[i]].append(obj[i][1])
            rgb_b[k_means.labels_[i]].append(obj[i][2])

        # Getting median colors per cluster
        r_median = [np.median(rgb_r[i]) for i in range(n_clusters)]
        g_median = [np.median(rgb_g[i]) for i in range(n_clusters)]
        b_median = [np.median(rgb_b[i]) for i in range(n_clusters)]

        image_median = np.zeros((self.photo_y, self.photo_x, 3))

        # Building images by pixel by cluster's color
        for pos, i in enumerate(k_means.labels_):
            pos_x = pos % self.photo_x
            pos_y = pos // self.photo_x
            image_median[pos_y][pos_x] = np.array([r_median[i], g_median[i], b_median[i]])

        file_name = "".join(random.choice(string.ascii_letters) for _ in range(20)) + ".png"
        skimage.io.imsave(file_name, skimage.img_as_ubyte(image_median))
        with open(file_name, "rb") as f:
            res_img = f.read()
        os.remove(file_name)

        if os.sys.platform.startswith("win"):
            self._close_session()
        self._queue.put(res_img)

    # def get_result_photo(self) -> bytes:
    #     """ Method for changing a number of colors in image
    #
    #     :return: image in bytes
    #     """
    #     transform_image = skimage.img_as_float(self.image)
    #     # creating feature objects matrix
    #     obj = np.reshape(transform_image, (self.photo_y * self.photo_x, len(transform_image[0][0])))
    #
    #     # Training K-means algorithm
    #     k_means = KMeans(init='k-means++', n_clusters=self.n_clusters).fit(obj)
    #     n_clusters = k_means.n_clusters
    #     rgb_r = [list() for _ in range(n_clusters)]
    #     rgb_g = [list() for _ in range(n_clusters)]
    #     rgb_b = [list() for _ in range(n_clusters)]
    #
    #     # Getting RGB colors for each cluster
    #     for i in range(len(k_means.labels_)):
    #         rgb_r[k_means.labels_[i]].append(obj[i][0])
    #         rgb_g[k_means.labels_[i]].append(obj[i][1])
    #         rgb_b[k_means.labels_[i]].append(obj[i][2])
    #
    #     # Getting median colors per cluster
    #     r_median = [np.median(rgb_r[i]) for i in range(n_clusters)]
    #     g_median = [np.median(rgb_g[i]) for i in range(n_clusters)]
    #     b_median = [np.median(rgb_b[i]) for i in range(n_clusters)]
    #
    #     image_median = np.zeros((self.photo_y, self.photo_x, 3))
    #
    #     # Building images by pixel by cluster's color
    #     for pos, i in enumerate(k_means.labels_):
    #         pos_x = pos % self.photo_x
    #         pos_y = pos // self.photo_x
    #         image_median[pos_y][pos_x] = np.array([r_median[i], g_median[i], b_median[i]])
    #
    #     file_name = "".join(random.choice(string.ascii_letters) for _ in range(20)) + ".png"
    #     skimage.io.imsave(file_name, skimage.img_as_ubyte(image_median))
    #     with open(file_name, "rb") as f:
    #         res_img = f.read()
    #     os.remove(file_name)
    #     return res_img

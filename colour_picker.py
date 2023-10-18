from __future__ import print_function
import binascii
import struct
from PIL import Image
import numpy as np
import scipy
import scipy.misc
import scipy.cluster
import cv2

NUM_CLUSTERS = 10


def colour_picker(img):
    if img.shape[0] > 0 and img.shape[1] > 0:
        img = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
        img = img.resize((150, 150))  # optional, to reduce time
        img = img.convert("HSV")
        ar = np.asarray(img)
        shape = ar.shape
        ar = ar.reshape(np.product(shape[:2]), shape[2]).astype(float)

        codes, dist = scipy.cluster.vq.kmeans(ar, NUM_CLUSTERS)
        vecs, dist = scipy.cluster.vq.vq(ar, codes)  # assign codes
        counts, bins = np.histogram(vecs, len(codes))  # count occurrences

        index_max = np.argmax(counts)  # find most frequent
        peak = tuple(codes[index_max])
        # colour = binascii.hexlify(bytearray(int(c) for c in peak)).decode('ascii')

    else:
        peak = None

    return peak

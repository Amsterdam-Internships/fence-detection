import os
import io
import cv2
import yaml
import json
import torch
import types
import inspect

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from PIL import Image
from pprint import pprint

from skimage import io, transform
from torch.utils.data import Dataset
from torchvision import transforms


# helper functions
def pixel_to_viewpoint(pixel, image_width=8000, dtype=int):
    """
    Convert width in pixels to viewpoint in degrees
    """
    return dtype(360 * pixel / image_width)


def viewpoint_to_pixels(viewpoint, image_width=8000, dtype=int):
    """
    Convert viewpoint in degrees to width in pixels
    """
    return dtype(viewpoint / 360 * image_width)


def reindex(index, max):
    """
    Reindex out-of-bounds indices
    """
    if not index:
        return index

    if index < 0:
        index += max
    elif index > max:
        index -= max

    return index


class PanoramaImage(object):
    """
    """
    def __init__(self, img, metadata, show_method=None):
        # private
        self._metadata = metadata

        # general purpose
        self.image = img
        self.show_method = show_method

        self.height, self.width, self.channels = self.image.shape

        for key, item in metadata.iteritems():
            if not isinstance(item, str):
                setattr(self, key, item)
            else:
                setattr(self, key, yaml.safe_load(item))

        self.viewpoint_front = self.heading
        self.viewpoint_back = self.heading - 180

        self.reindex = lambda x: reindex(x, self.width)


    def __getitem__(self, args):
        """
        """
        concat = False
        slices = [slice(None, None, None), 
                  slice(None, None, None),
                  slice(None, None, None)]

        # convert out-of-bounds indices
        for i, arg in enumerate(args):
            if isinstance(arg, int):
                slices[i] = self.reindex(arg)
            elif isinstance(arg, slice):
                start = self.reindex(arg.start)
                stop = self.reindex(arg.stop)

                if start and stop and start > stop:
                    concat = True

                    if i != 1:
                        raise NotImplementedError

                slices[i] = slice(start, stop)

        # concatenate if reverse sliced
        if concat:
            left_half = self.image[slices[0], start:, slices[2]]
            right_half = self.image[slices[0], :stop, slices[2]]

            concatenated = np.concatenate((left_half, right_half), axis=1)
            ret = PanoramaImage(concatenated, self._metadata, self.show_method)
        else:
            ret = PanoramaImage(self.image[tuple(slices)], self._metadata, self.show_method)
        return ret


    def __setitem__(self, args, value):
        """
        """ 
        concat = False
        slices = [slice(None, None, None), 
                  slice(None, None, None),
                  slice(None, None, None)]

        # convert out-of-bounds indices
        for i, arg in enumerate(args):
            if isinstance(arg, int):
                slices[i] = self.reindex(arg)
            elif isinstance(arg, slice):
                start = self.reindex(arg.start)
                stop = self.reindex(arg.stop)

                if start and stop and start > stop:
                    concat = True

                    if i != 1:
                        raise NotImplementedError

                slices[i] = slice(start, stop)

        # concatenate if reverse sliced
        if concat:
            self.image[slices[0], start:, slices[2]] = value
            self.image[slices[0], :stop, slices[2]] = value
        else:
            self.image[tuple(slices)] = value
        

    def save(self, fname):
        """
        """
        cv2.imwrite(fname, self.image)


    def show(self, viewpoint_width=0):
        """
        """
        copy = self.image

        if viewpoint_width:
            front = viewpoint_to_pixels(self.viewpoint_front)
            back = viewpoint_to_pixels(self.viewpoint_back)

            copy[:, front - viewpoint_width:front + viewpoint_width, :] = (0, 255, 0)
            copy[:, back - viewpoint_width:back + viewpoint_width, :] = (255, 0, 0)

        self.show_method(copy)
        plt.show()


class PanoramaLoader(object):
    """
    """
    def __init__(self, dirname, shuffle=False, filter_corrupt=True, read_imgs=True):
        # private
        self._options = ['read_method', 
                         'show_method']

        # path data
        self.imgs_src = os.path.join(dirname, 'water_images_2')
        self.meta_src = os.path.join(dirname, 'metadata_with_new_filenames.csv')

        self.all_metadata = pd.read_csv(self.meta_src)

        self.imgs_list = self.all_metadata.filename_dump.map(lambda x: os.path.join(self.imgs_src, x)).to_numpy()

        # try to load from memory
        memory = os.path.join(dirname, '.notcorrupt')
        if os.path.isfile(memory):
            self.idxs = np.load(memory, allow_pickle=True)
        else:
            self.idxs = range(0, len(self.imgs_list))

        # filter corrupt images
        if filter_corrupt and not os.path.isfile(memory):
            self.idxs = []
            for i, img in enumerate(self.imgs_list):
                try:
                    statfile = os.stat(img)
                    filesize = statfile.st_size
                    if filesize > 0:
                        self.idxs.append(i)
                except:
                    pass
                print(i)

        self.idxs = np.array(self.idxs)
        self.idxs.dump(memory)

        # shuffle dataset
        if shuffle:
            np.random.shuffle(self.idxs)
        
        # options
        self.read_method = None
        self.show_method = None


    def __len__(self):
        """
        """
        return len(self.idxs)
    

    def __getitem__(self, idx):
        """
        """
        img_src = self.imgs_list[self.idxs[idx]]
        meta_src = self.all_metadata.iloc[self.idxs[idx]]

        if callable(self.read_method) and callable(self.show_method):
            try:
                return PanoramaImage(self.read_method(img_src), meta_src, show_method=self.show_method)
            except:
                raise NotImplementedError
        else:
            raise NotImplementedError


    def refresh(self):
        """
        """
        self.indices = np.array([i for i, metadata in enumerate(self.all_metadata) if metadata['surface_type'] in self.surface_type])

        self.imgs_list = self.imgs_list[self.indices]
        self.meta_list = self.meta_list[self.indices]


    def set_option(self, attr, value):
        """
        """
        if attr not in self._options:
            raise NotImplementedError

        if attr == 'surface_type':
            if value == '*':
                setattr(self, attr, self.surface_types)
            else:
                setattr(self, attr, [value])
            self.refresh()
        else:
            setattr(self, attr, value)

    
    def geoplot(self, img=None, **kwargs):
        """
        """
        lngs = self.all_metadata.lng
        lats = self.all_metadata.lat

        plt.scatter(lngs, lats)

        if img:
            plt.scatter(img.lng, img.lat, **kwargs)
        
        plt.show()
        
        return
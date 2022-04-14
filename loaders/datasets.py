import os
import io
import json
import torch

import numpy as np

from PIL import Image

from skimage import io, transform
from torch.utils.data import Dataset
from torchvision import transforms
from pycocotools.coco import COCO


class COCODataset(Dataset):
    """
    """
    def __init__(self, root_dir, subset='train', challenge='instances', task='segmentation', year=2017, transform=None, categories=''):
        """
        """
        self.task = task
        self.transform = transform

        # find directories
        self.image_dir = os.path.join(root_dir, f'{subset}{year}')
        self.ann_dir = f'annotations_trainval{year}'

        # find specific annotation directory
        for dirname in os.listdir(root_dir):
            if challenge in dirname:
                self.ann_dir = dirname
                break
        
        self.coco = COCO(os.path.join(root_dir, 
                                      self.ann_dir, 
                                      'annotations', 
                                      f'{challenge}_{subset}{year}.json'))

        # get annotations using COCO API
        category_ids = self.coco.getCatIds(catNms=categories)
        annotation_ids = self.coco.getAnnIds(catIds=category_ids)
        self.annotations = self.coco.loadAnns(annotation_ids)


    def __len__(self):
        return len(self.annotations)


    def __getitem__(self, idx):
        """
        """
        annotation = self.annotations[idx]

        fname = f'{annotation["image_id"]}'.zfill(12) + '.jpg'
        
        image = io.imread(os.path.join(self.image_dir, fname))
        label = self.coco.annToMask(annotation) \
            if self.task == 'segmentation' else annotation[self.task]

        if self.transform:
            image = self.transform(image)
            label = torch.as_tensor(label)
            
        return image, label


class ADE20KDataset(Dataset):
    """
    """
    def __init__(self):
        return


    def __len__(self):
        return


    def __getitem__(self):
        return


class AmsterdamDataset(Dataset):
    """
    """
    def __init__(self, imagedir, annotations, transform=None):
        """
        """
        self.transform = transform
        self.imagedir = imagedir
        
        # get annotations using COCO API
        self.coco = COCO(annotations)

        self.category_ids = self.coco.getCatIds()
        annotation_ids = self.coco.getAnnIds(catIds=self.category_ids)
        image_ids = self.coco.getImgIds(catIds=self.category_ids)

        self.images = self.coco.loadImgs(image_ids)
        self.annotations = self.coco.loadAnns(annotation_ids)


    def __len__(self):
        return len(self.images)


    def __getitem__(self, idx):
        """
        """
        # load image
        obj = self.images[idx]
        fname = os.path.join(self.imagedir, obj['file_name'])
        image = io.imread(fname)
        
        # get all annotations corresponding to image
        annotation_ids = self.coco.getAnnIds(imgIds=obj['id'], catIds=self.category_ids, iscrowd=None)
        annotations = self.coco.loadAnns(annotation_ids)

        # generate mask
        mask = np.zeros((obj['height'], obj['width']))

        for annotation in annotations:
            if annotation.get('mask'):
                mask = np.maximum(mask, np.array(annotation.get('mask')) * annotation['category_id'])
            else:
                mask = np.maximum(mask, self.coco.annToMask(annotation) * annotation['category_id'])

        if self.transform:
            image = self.transform(image)
            mask = torch.as_tensor(mask)
            
        return image, mask
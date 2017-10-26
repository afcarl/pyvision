"""
The MIT License (MIT)

Copyright (c) 2017 Marvin Teichmann
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
import sys

import numpy as np
import scipy as scp

import logging

logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s',
                    level=logging.INFO,
                    stream=sys.stdout)

from collections import OrderedDict


class SegmentationMetric(object):
    """docstring for SegmentationMetric"""
    def __init__(self, num_classes, name_list=None):
        super(SegmentationMetric, self).__init__()
        self.num_classes = num_classes
        self.name_list = name_list

        self.tps = np.zeros([num_classes])
        self.fps = np.zeros([num_classes])
        self.tns = np.zeros([num_classes])
        self.fns = np.zeros([num_classes])

        self.count = 0

    def add(self, gt, mask, prediction):
        self.count = self.count + np.sum(mask)
        relevant_classes = set(np.unique(prediction)).union(np.unique(gt))
        for cl_id in relevant_classes:
            pos = gt == cl_id
            pred = prediction == cl_id

            tp = np.sum(pos * pred * mask)
            fp = np.sum((1 - pos) * pred * mask)
            fn = np.sum(pos * (1 - pred) * mask)
            tn = np.sum((1 - pos) * (1 - pred) * mask)

            assert(tp + fp + fn + tn == np.sum(mask))

            self.tps[cl_id] = self.tps[cl_id] + tp
            self.fps[cl_id] = self.fps[cl_id] + fp
            self.fns[cl_id] = self.fns[cl_id] + fn
            self.tns[cl_id] = self.tns[cl_id] + tn

        return

    def get_iou_dict(self):

        if self.name_list is None:
            name_list = range(self.num_classes)
        else:
            name_list = self.name_list

        ious = self.tps / (self.tps + self.fps + self.fns)
        assert(len(name_list) == len(ious))

        result_dict = OrderedDict(zip(name_list, ious))

        return result_dict

    def compute_miou(self, ignore_first=False):

        ious = self.tps / (self.tps + self.fps + self.fns)

        if ignore_first:
            ious = ious[1:]

        return np.mean(ious)

    def get_accuracy(self, ignore_first=False):

        return np.sum(self.tps) / self.count


class SegmentationVisualizer(object):
    """docstring for label_converter"""
    def __init__(self, color_list=None, name_list=None,
                 mode='RGB'):
        super(SegmentationVisualizer, self).__init__()
        self.color_list = color_list
        self.name_list = name_list

        self.mask_color = [255, 255, 255]

        if mode == 'RGB':
            self.chan = 3

    def id2color(self, id_image, mask=None):

        shape = id_image.shape
        gt_out = np.zeros([shape[0], shape[1], self.chan], dtype=np.int32)
        id_image

        for train_id, color in enumerate(self.color_list):
            c_mask = id_image == train_id
            c_mask = c_mask.reshape(c_mask.shape + tuple([1]))
            gt_out = gt_out + color * c_mask

        if mask is not None:
            mask = mask.reshape(mask.shape + tuple([1]))
            bg_color = [0, 0, 0]
            mask2 = np.all(gt_out == bg_color, axis=2)
            mask2 = mask2.reshape(mask2.shape + tuple([1]))
            gt_out = gt_out + mask2 * (self.mask_color * (1 - mask))

        return gt_out

    def pred2color(self, pred_image, mask=None):

        color_image = np.dot(pred_image, self.color_list)

        return color_image

    def color2id(self, color_gt):
        assert(False)
        shape = color_gt.shape
        gt_reshaped = np.zeros([shape[0], shape[1]], dtype=np.int32)
        mask = np.zeros([shape[0], shape[1]], dtype=np.int32)

        for train_id, color in enumerate(self.color_list):
            gt_label = np.all(color_gt == color, axis=2)
            mask = mask + gt_label
            gt_reshaped = gt_reshaped + 10 * train_id * gt_label

        assert(np.max(mask) == 1)
        np.unique(gt_reshaped)
        assert(np.max(gt_reshaped) <= 200)

        gt_reshaped = gt_reshaped + 255 * (1 - mask)
        return gt_reshaped

    def underlay2(self, image, gt_image, labels):
        # TODO
        color_img = self.id2color(gt_image)
        color_labels = self.id2color(labels)

        output = np.concatenate((image, color_img, color_labels), axis=0)

        return output

    def overlay(self, image, gt_image):
        # TODO
        color_img = self.id2color((gt_image))
        output = 0.4 * color_img[:, :] + 0.6 * image

        return output


if __name__ == '__main__':
    logging.info("Hello World.")

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.image as im
import tensorflow as tf
import itertools
import math
import os
import argparse
import sys

tf.enable_eager_execution()

import waymo_open_dataset
from waymo_open_dataset.utils import range_image_utils
from waymo_open_dataset.utils import transform_utils
from waymo_open_dataset.utils import  frame_utils
from waymo_open_dataset import dataset_pb2 as open_dataset

def label_extractor(i, filename, Label_all, Label):

    FileName = filename
    dataset = tf.data.TFRecordDataset(FileName, compression_type='')
    # __lidar_list = ['_FRONT', '_FRONT_LEFT', '_FRONT_RIGHT', '_SIDE_LEFT', '_SIDE_RIGHT']
    __lidar_list = ['_FRONT', '_FRONT_RIGHT', '_FRONT_LEFT', '_SIDE_RIGHT', '_SIDE_LEFT']
    __type_list = ['unknown', 'Vehicle', 'Pedestrian', 'Sign', 'Cyclist']

    for data in dataset:

        i_str = '{0:06}'.format(i)

        frame = open_dataset.Frame()
        frame.ParseFromString(bytearray(data.numpy()))

        file_path = os.path.join(Label_all, "%s.txt"%(i_str))

        f_open = open(file_path, 'w+')

        id_to_bbox = dict()
        id_to_name = dict()
        for labels in frame.projected_lidar_labels:
            name = labels.name
            for label in labels.labels:
                bbox = [label.box.center_x - label.box.length / 2, label.box.center_y - label.box.width / 2,
                        label.box.center_x + label.box.length / 2, label.box.center_y + label.box.width / 2]
                id_to_bbox[label.id] = bbox
                id_to_name[label.id] = name - 1

        for obj in frame.laser_labels:

            # caculate bounding box
            bounding_box = None
            name = None
            id = obj.id
            for lidar in __lidar_list:
                if id + lidar in id_to_bbox:
                    bounding_box = id_to_bbox.get(id + lidar)
                    name = str(id_to_name.get(id + lidar))
                    break
            if bounding_box == None or name == None:
                continue

            my_type = __type_list[obj.type]
            truncated = 0
            occluded = 0
            height = obj.box.height
            width = obj.box.width
            length = obj.box.length
            x = obj.box.center_x
            y = obj.box.center_y
            z = obj.box.center_z
            rotation_y = obj.box.heading
            beta = math.atan2(x, z)
            alpha = (rotation_y + beta - math.pi / 2) % (2 * math.pi)

            # save the labels
            line = my_type + ' {} {} {} {} {} {} {} {} {} {} {} {} {} {}\n'.format(round(truncated, 2),
                                                                                   round(occluded, 2),
                                                                                   round(alpha, 2),
                                                                                   round(bounding_box[0], 2),
                                                                                   round(bounding_box[1], 2),
                                                                                   round(bounding_box[2], 2),
                                                                                   round(bounding_box[3], 2),
                                                                                   round(height, 2),
                                                                                   round(width, 2),
                                                                                   round(length, 2),
                                                                                   round(x, 2),
                                                                                   round(y, 2),
                                                                                   round(z, 2),
                                                                                   round(rotation_y, 2))
            line_all = line[:-1] + ' ' + '\n'
            # # store the label
            
            name_of_file = ("%s.txt"%(i_str))
            fp_label = open(Label + name + '/' + name_of_file, 'a')
            fp_label.write(line)
            fp_label.close()

            f_open.write(line_all)
        f_open.close()



        i = i + 1
    return i
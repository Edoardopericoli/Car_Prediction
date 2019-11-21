"""
Find and drop columns according to different criteria.

List of functions
-----------------
"""
from keras.models import load_model
from keras import backend as K
from cv2 import cv2
import numpy as np
import os
import glob
import pandas as pd
import yaml
from CarModelClassifier.utils import swish, FixedDropout
import tensorflow as tf


def evaluation(model, test_images_path, test_labels_path):
    # Loading paths and model information


    if os.path.isfile(test_images_path):
        img = cv2.imread(test_images_path)
        img = cv2.resize(img, (240,
                               240))
        images = np.reshape(img, [1, 240,
                                  240, 3])

        filenames = [os.path.basename(test_images_path)]

    elif os.path.isdir(test_images_path):
        test_images_path = glob.glob(test_images_path + "/*")
        images = [cv2.imread(f) for f in test_images_path]
        images = np.array([cv2.resize(img,
                                      (240,
                                       240))
                          for img in images])
        images = np.reshape(images, [len(test_images_path),
                                     240,
                                     240, 3])

        filenames = [os.path.basename(img_path)
                     for img_path in test_images_path]

    print('---------------------------------')
    print(filenames[:30])
    print('---------------------------------')
    classes_lists = model.predict(images)
    print(classes_lists[0])

    class_n = np.argwhere(classes_lists == 1)[:, 1].tolist()
    labels = sorted([str(i + 1) for i in range(21)])
    classes = []
    for el in class_n:
        classes.append(int(labels[el]))


    #for image in images:
    #    class_image = model.predict(tf.expand_dims(image, 0), steps=1)[0]
    #    classes.append(class_image)

    print(classes)

    output_df = pd.DataFrame({'filename': filenames,
                              'predicted_class': classes})
    labels_df = pd.read_csv(test_labels_path, sep=',')
    output_df = output_df.merge(labels_df, left_on='filename',
                                right_on='fname')
    print(output_df.head(30))
    accuracy = len(output_df.loc[output_df['predicted_class'] ==
                   output_df['model_label'], :]) / len(output_df)
    return accuracy


def prediction(execution_path, images_path, labels_info_path):
    # Loading paths and model information
    initial_parameters_path = execution_path + '/initial_parameters.yml'
    with open(initial_parameters_path) as f:
        initial_parameters = yaml.load(f)
    model_path = execution_path + '/model.h5'
    model = load_model(model_path)

    if os.path.isfile(images_path):
        img = cv2.imread(images_path)
        img = cv2.resize(img, (initial_parameters['IMG_HEIGHT'],
                               initial_parameters['IMG_WIDTH']))
        images = np.reshape(img, [1, initial_parameters['IMG_HEIGHT'],
                                  initial_parameters['IMG_WIDTH'], 3])

        filenames = [os.path.basename(images_path)]


    elif os.path.isdir(images_path):
        images_path = glob.glob(images_path + "/*")
        images = [cv2.imread(f) for f in images_path]
        images = np.array([cv2.resize(img,
                                      (initial_parameters['IMG_HEIGHT'],
                                       initial_parameters['IMG_WIDTH']))
                          for img in images])
        images = np.reshape(images, [len(images_path),
                                     initial_parameters['IMG_HEIGHT'],
                                     initial_parameters['IMG_WIDTH'], 3])

        filenames = [os.path.basename(img_path) for img_path in images_path]

    classes = model.predict_classes(images)

    output_df = pd.DataFrame({'filename': filenames, 'class': classes})
    labels_df = pd.read_csv(labels_info_path)
    output_df = output_df.merge(labels_df, left_on='class', right_on='label') \
                         .drop(columns=['class'])
    return output_df

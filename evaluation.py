from keras.models import load_model
from cv2 import cv2
import numpy as np
import os
import glob
import click
import pandas as pd
import yaml

# /home/edoardo/Desktop/University/Cars_Classification/Car_Prediction/trial_model
# /home/edoardo/Desktop/University/Cars_Classification/Car_Prediction/trial_images
# /home/edoardo/Desktop/University/Cars_Classification/Car_Prediction/data/labels_info.csv
@click.command()
@click.option('--execution_path', default=r"./", help='config model path',
              type=str)
@click.option('--test_images_path', default=r"./",
              help='path of images (file or directory)', type=str)
@click.option('--test_labels_path', default=r"./",
              help='path of images (file or directory)', type=str)
def main(execution_path, test_images_path, test_labels_path):
    # Loading paths and model information
    initial_parameters_path = execution_path + '/initial_parameters.yml'
    with open(initial_parameters_path) as f:
        initial_parameters = yaml.load(f)
    model_path = execution_path + '/model.h5'
    model = load_model(model_path)

    if os.path.isfile(test_images_path):
        img = cv2.imread(test_images_path)
        img = cv2.resize(img, (initial_parameters['IMG_HEIGHT'],
                               initial_parameters['IMG_WIDTH']))
        images = np.reshape(img, [1, initial_parameters['IMG_HEIGHT'],
                                  initial_parameters['IMG_WIDTH'], 3])

        filenames = [os.path.basename(test_images_path)]

    elif os.path.isdir(test_images_path):
        test_images_path = glob.glob(test_images_path + "/*")
        images = [cv2.imread(f) for f in test_images_path]
        images = np.array([cv2.resize(img,
                                      (initial_parameters['IMG_HEIGHT'],
                                       initial_parameters['IMG_WIDTH']))
                          for img in images])
        images = np.reshape(images, [len(test_images_path),
                                     initial_parameters['IMG_HEIGHT'],
                                     initial_parameters['IMG_WIDTH'], 3])

        filenames = [os.path.basename(img_path)
                     for img_path in test_images_path]
    classes = model.predict_classes(images)

    output_df = pd.DataFrame({'filename': filenames,
                              'predicted_class': classes})
    labels_df = pd.read_csv(test_labels_path)
    output_df = output_df.merge(labels_df, left_on='filename', right_on='fname') \
                         .drop(columns=['class'])
    accuracy = len(output_df.loc[output_df['predicted_class'] == output_df['label'], :]) / len(output_df)
    print(f'Accuracy: {accuracy:.2f}')


if __name__ == "__main__":
    main()

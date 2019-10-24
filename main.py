import numpy as np
from keras.models import Sequential
from keras.layers import Dense, Conv2D, Flatten, Dropout, MaxPooling2D
from keras.preprocessing.image import ImageDataGenerator
import pandas as pd
from keras_preprocessing.image import ImageDataGenerator
from keras.layers import Dense, Activation, Flatten, Dropout, BatchNormalization
from keras.layers import Conv2D, MaxPooling2D
from keras import regularizers, optimizers
import tensorflow as tf
import keras
from matplotlib import pyplot as plt
import csv
from math import ceil
import click
import logging
import os
import yaml
from utils.main_utils import asserting_batch_size
import sys


@click.command()
@click.option('--initial_parameters_path', default=r"config\initial_parameters.yml", help='config file containing initial parameters', type=str)
@click.option('--username', help='username to be used for model saving', type=str)
@click.option('--shows_only_summary', default=False, help='if True the program stops after having shown the model summary', type=bool)
def main(initial_parameters_path, username, shows_only_summary):
    logging.info('Starting the process')
    logging.info('Asserting dimensions of train, validation and test')

    # Asserting that dimensions of train, validation and test are consistent
    full_data_length = len(os.listdir('data/raw_data/cars_train'))
    train_length = len(os.listdir('data/train'))
    validation_length = len(os.listdir('data/validation'))
    test_length = len(os.listdir('data/test'))
    assert full_data_length == train_length + validation_length + test_length

    logging.info('Loading data')
    train_df = pd.read_csv("data/labels/train_labels.csv")
    validation_df = pd.read_csv("data/labels/validation_labels.csv")

    with open(initial_parameters_path) as file:
        initial_parameters = yaml.load(file)

    logging.info('Asserting batch sizes')
    # Asserting dimensions of batch sizes
    asserting_batch_size(length_data=len(train_df), batch_size=initial_parameters['train_batch_size'])
    asserting_batch_size(length_data=len(validation_df), batch_size=initial_parameters['validation_batch_size'])

    logging.info('Transforming data using ImageDataGenerator')
    train_image_generator = ImageDataGenerator(rescale=1./255)
    validation_image_generator = ImageDataGenerator(rescale=1./255)

    classes = np.arange(1, 197)
    classes = [str(i) for i in classes]
    train_generator = train_image_generator.flow_from_dataframe(
        dataframe=train_df,
        directory="data/train",
        x_col="fname",
        y_col=classes,
        batch_size=initial_parameters['train_batch_size'],
        seed=initial_parameters['seed'],
        shuffle=True,
        class_mode="other",
        target_size=(initial_parameters['IMG_HEIGHT'], initial_parameters['IMG_WIDTH'])
    )

    validation_generator = validation_image_generator.flow_from_dataframe(
        dataframe=validation_df,
        directory="data/validation",
        x_col="fname",
        y_col=classes,
        batch_size=initial_parameters['validation_batch_size'],
        seed=initial_parameters['seed'],
        shuffle=True,
        class_mode="other",
        target_size=(initial_parameters['IMG_HEIGHT'], initial_parameters['IMG_WIDTH'])
    )

    # Model
    model = Sequential([
        Conv2D(40, 4, activation='relu', input_shape=(initial_parameters['IMG_HEIGHT'], initial_parameters['IMG_WIDTH'], 3)),
        MaxPooling2D((4, 4)),
        Conv2D(8, 4, padding='same', activation='relu'),
        MaxPooling2D((4, 4)),
        Flatten(),
        Dense(64, activation='relu'),
        Dense(len(classes), activation='softmax')
    ])

    model.compile(optimizer='adam',
                  loss='categorical_crossentropy',
                  metrics=['accuracy'])

    model.summary()

    if shows_only_summary:
        sys.exit()
# TODO: Creare setting per scegliere se fare gridsearch

    logging.info('Fitting the model')
    history = model.fit_generator(
        train_generator,
        epochs=initial_parameters['epochs'],
        validation_data=validation_generator,
        steps_per_epoch=ceil(len(train_df) / initial_parameters['train_batch_size']),
        validation_steps=ceil(len(train_df) / initial_parameters['validation_batch_size'])
     )

    # Saving model
    model_names = [name for name in os.listdir('data/models') if name.startswith(username)]
    if len(model_names) == 0:
        model_name = username + '_' + '1'
        logging.info('Saving: model, initial parameters and architecture into {model_directory}'.format(
            model_directory='data/models/' + model_name))
        os.mkdir('data/models/' + model_name)
        yaml_string = model.to_yaml()
        with open('data/models/' + model_name + '/architecture.yml', 'w') as outfile:
            yaml.dump(yaml_string, outfile, default_flow_style=False)
        # Saving global parameters
        with open('data/models/' + model_name + '/initial_parameters.yml', 'w') as outfile:
            yaml.dump(initial_parameters, outfile, default_flow_style=False)
        # Saving estimator
        model.save('data/models/' + model_name + '/model.h5')
    else:
        model_name = username + '_' + str(int(model_names[-1].split('_')[-1]) + 1)
        logging.info('Saving: model, initial parameters and architecture into {model_directory}'.format(
            model_directory='data/models/' + model_name))
        os.mkdir('data/models/' + model_name)
        # Saving architecture
        yaml_string = model.to_yaml()
        with open('data/models/' + model_name + '/architecture.yml', 'w') as outfile:
            yaml.dump(yaml_string, outfile, default_flow_style=False)
        # Saving global parameters
        with open('data/models/' + model_name + '/initial_parameters.yml', 'w') as outfile:
            yaml.dump(initial_parameters, outfile, default_flow_style=False)
        # Saving estimator
        model.save('data/models/' + model_name + '/model.h5')

    # Model Performance
    train_accuracy = history.history['acc']
    validation_accuracy = history.history['val_acc']

    train_loss = history.history['loss']
    validation_loss = history.history['val_loss']

    list_epochs = np.arange(1, initial_parameters['epochs'] + 1)
    list_epochs = [str(epoch) for epoch in list_epochs]
    rows = zip(list_epochs, train_accuracy, validation_accuracy, train_loss, validation_loss)
    headers = ['Epoch', 'Train Accuracy', 'Validation Accuracy', 'Train Loss', 'Validation Loss']
    if len(model_names) == 0:
        model_name = username + '_' + '1'
        logging.info('Saving: model performance into {model_directory}'.format(
            model_directory='data/models/' + model_name))
        with open('data/models/' + model_name + '/evaluation.csv', 'w') as outfile:
            writer = csv.writer(outfile, delimiter='|')
            writer.writerow(headers)
            for row in rows:
                writer.writerow(row)
    else:
        model_name = username + '_' + str(int(model_names[-1].split('_')[-1]) + 1)
        logging.info('Saving: model performance into {model_directory}'.format(
            model_directory='data/models/' + model_name))
        with open('data/models/' + model_name + '/evaluation.csv', 'w') as outfile:
            writer = csv.writer(outfile, delimiter='|')
            writer.writerow(headers)
            for row in rows:
                writer.writerow(row)

    logging.info('Process finished')


if __name__ == '__main__':
    main()
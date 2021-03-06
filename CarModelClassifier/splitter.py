import pandas as pd
from sklearn.model_selection import train_test_split
import os
import shutil
from pathlib import Path


def split(initial_parameters, train_size=0.8, crop_images=False):
    """
    Perform splitting of the data.

    It splits the data starting from the csv file
    "data/labels/all_labels_new.csv" in a stratified
    fashion. The folder from which the images are taken
    dependes on the parameter "crop_images". Then it creates
    3 new csv files in the same folder: "train_labels.csv",
    "test_labels.csv", "validation_labels.csv".
    Finally creates 3 folders in "data" called: "train", "test",
    and "validation" containing the images splitted.

    Parameters
    ----------
    initial_parameters : string
        the name of the yaml file containing the initial
        parameters.
    train_size : float, optional
        the size of the train when splitting is performed.
        By default, the test and the validation will have
        the same size.
    crop_images : bool, optional
        If True, the images to be splitted are taken from
        the folder "data/object_detection_data/output_images_cropped",
        otherwise they are taken from "data/raw_data/cars_train_new".
    """
    file_path = Path((os.path.dirname(os.path.abspath(__file__))).replace('\\', '/'))

    data_path = Path('../' + initial_parameters['data_path'])
    origin_data_path = data_path / 'labels/all_labels_new.csv'

    # Reading data
    data = pd.read_csv(file_path / origin_data_path)

    if crop_images:
        data = pd.read_csv(file_path / data_path / 'labels/all_labels_new.csv')

    # Splitting train, validation, test
    X_train, X_test_temp, y_train, y_test_temp = train_test_split(data[['fname']],
                                                                  data['model_label'],
                                                                  test_size=1 - train_size,
                                                                  random_state=89,
                                                                  stratify=data['model_label']
                                                                 )

    train = pd.DataFrame(X_train).merge(pd.DataFrame(y_train), left_index=True, right_index=True)
    test_temp = pd.DataFrame(X_test_temp).merge(pd.DataFrame(y_test_temp), left_index=True, right_index=True)

    X_test, X_validation, y_test, y_validation = train_test_split(test_temp[['fname']],
                                                                    test_temp['model_label'],
                                                                    test_size=0.5,
                                                                    random_state=89,
                                                                    stratify=test_temp['model_label']
                                                                    )

    validation = pd.DataFrame(X_validation).merge(pd.DataFrame(y_validation), left_index=True, right_index=True)
    test = pd.DataFrame(X_test).merge(pd.DataFrame(y_test), left_index=True, right_index=True)

    data.set_index('fname', inplace=True)
    train.set_index('fname', inplace=True)
    validation.set_index('fname', inplace=True)
    test.set_index('fname', inplace=True)

    # Testing that the split has been executed correctly
    assert len(data) == len(train) + len(validation) + len(test)

    # Writing boxes data and class names data into csv files and writing a csv for each of train, validation and test
    train.to_csv(file_path / data_path / 'labels/train_labels.csv')
    validation.to_csv(file_path / data_path / 'labels/validation_labels.csv')
    test.to_csv(file_path / data_path / 'labels/test_labels.csv')

    # Sending images to train, validation and test folders
    indexes = {'train': train.index, 'validation': validation.index, 'test': test.index}

    src = file_path / data_path / 'raw_data/cars_train_new'
    if crop_images:
        src = file_path / data_path / 'object_detection_data/output_images_cropped'

    length_all_folders = []
    for index in indexes.keys():
        dest = file_path / data_path / str(index)
        if os.path.exists(dest):
            shutil.rmtree(dest, ignore_errors=True)
        os.mkdir(dest)
        for file_name in indexes[index]:
            full_file_name = src / file_name
            if full_file_name.is_file():
                shutil.copy(full_file_name, dest)

        length_folder = len(os.listdir(dest))
        length_all_folders.append(length_folder)

    assert len(data) == sum(length_all_folders)

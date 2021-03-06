from CarModelClassifier import utils, splitter, yolo
from CarModelClassifier.models import EffnetB1
import logging


def run(initial_parameters_path="./config/initial_parameters.yml",
        username="trial", shows_only_summary=False, net=EffnetB1,
        bounding_cpu=False, split_data=True,
        crop_images=False):
    """
    Perform all the steps for training and saving the model.

    Parameters
    ----------
    initial_parameters_path : string, optional
        the name of the yaml file containing the initial
        parameters.
    username : string, optional
        the name used to save the model in the folder
        "data/models".
    shows_only_summary : bool, optional
        if True the script exits after having shown
        the summary.
    net : net, optional
        specify the architecture to be used
    bounding_cpu : bool, optional
        if True, it limits the cpu usage
    split_data : bool, optional
        if True perform splitting
    crop_images : bool, optional
        if True, perform object detection and
        cropping of images
    """

    utils.setting_log()
    initial_parameters = utils.load_parameters(initial_parameters_path)

    if crop_images:
        yolo.crop()
    if split_data:
        logging.info('Starting splitting and preparing processes')
        splitter.split(initial_parameters,
                       crop_images=crop_images)
        logging.info('Splitting ended successfully')

    if bounding_cpu:
        utils.bound_cpu(n_threads=8)

    train_path = "../" + initial_parameters['data_path'] + "/train/"
    validation_path = "../" + initial_parameters['data_path'] + "/validation/"

    logging.info('Starting the process')
    train_df, validation_df = utils.load_labels_dfs(initial_parameters)
    train_image_generator, validation_image_generator = utils.get_image_generators()

    train_generator = utils.get_generator(train_image_generator,
                                          train_df, train_path,
                                          initial_parameters,
                                          train=True)

    validation_generator = utils.get_generator(
                                       validation_image_generator,
                                       validation_df,
                                       validation_path,
                                       initial_parameters,
                                       train=False)

    logging.info('Transforming data using ImageDataGenerator')

    model_net = net(train_generator, initial_parameters)
    model = model_net.model
    model.summary()

    if shows_only_summary:
        return

    history = utils.train_model(train_generator, validation_generator,
                                initial_parameters, train_df, model)

    utils.save_model_info(username, model, initial_parameters, history)
    logging.info('Process finished')

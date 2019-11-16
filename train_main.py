import click
from Car_Prediction import pipeline
from Car_Prediction import models


@click.command()
@click.option('--initial_parameters_path',
              default=r"./config/initial_parameters.yml",
              help='config file containing initial parameters', type=str)
@click.option('--username', help='username to be used for model saving',
              type=str)
@click.option('--shows_only_summary', default=False,
              help='if True the program stops after having shown \
                    the model summary',
              type=bool)
@click.option('--net', default='effnet',
              help='the model you want to use',
              type=str)
@click.option('--bounding_cpu', default=False,
              help='if True the program will use 8 threads',
              type=bool)
@click.option('--prepare_labels', default=False,
              help='if True labels will be prepared accordingly',
              type=bool)
@click.option('--split_data', default=True,
              help='if True data will be splitted accordingly',
              type=bool)
@click.option('--target_variable', default='model',
              help='target variable of the model',
              type=str)
@click.option('--origin_data_path', default='data/labels/all_labels.csv',
              help='path from which getting images',
              type=str)
def main(initial_parameters_path, username, shows_only_summary, net,
         bounding_cpu, prepare_labels, split_data, target_variable, origin_data_path):

    if net == 'effnet':
        net = models.Effnet
    if net == 'prototype':
        net = models.Prototype

    pipeline.run(initial_parameters_path,
                                        username,
                                        shows_only_summary,
                                        bounding_cpu=bounding_cpu,
                                        net=net,
                                        prepare_labels=prepare_labels,
                                        split_data=split_data,
                                        target_variable=target_variable,
                                        origin_data_path=origin_data_path)


if __name__ == "__main__":
    main()

#todo: nel merge ricordarsi di tenere i cambiamenti di pericoli edoardo per il model saving
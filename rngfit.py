#!/usr/bin/python3


import datetime
import os

import click
import pandas as pd
import numpy as np


VERSION = '0.0.1'


class Control():
	def __init__(self):
		self.verbose = False
		self.inf = None


pass_control = click.make_pass_decorator(Control, ensure=True)


@click.group()
@click.version_option(version=VERSION)
@click.option('--verbose', is_flag=True, help='Increase output verbosity (maybe).')
@click.argument('inf', type=str)
@pass_control
def main(control, verbose, inf):
	control.verbose = verbose
	control.inf = inf


@main.command()
@pass_control
def new_user(control):
    """
    Create a new user
    """

    if not os.path.exists('data'):
        print("Creating data folder")
        os.makedirs('data')

    path = 'data/' + control.inf + '.hdf5'
    if os.path.exists(path):
        print("User already exists")
    else:
        print("Creating user file")
        data = pd.HDFStore(path)

        exercises = pd.DataFrame({
            'name': [],
            'min_weight': [],
            'rounding': [],
        })
        workouts = pd.DataFrame({
            'date': [],
            'name': [],
            'time': [],
            'reps': [],
            'weight': [],
            'rir': [],
        })

        print(workouts)
        print(exercises)

        data.put('exercises', exercises, format='table', data_columns=True)
        data.put('workouts', workouts, format='table', data_columns=True)

        print(data['exercises'])

        data.close()


@main.command()
@pass_control
@click.option('-n', '--name', type=str)
@click.option('-r', '--rounding', type=float)
@click.option('-m', '--min-weight', type=str)
@click.option('-o', '--orm-guess', type=str)
def add_exercise(control, name, rounding, min_weight, orm_guess):
    """
    Add a new tracked exercise
    """

    path = 'data/' + control.inf + '.hdf5'
    assert os.path.exists(path)

    with pd.HDFStore(path) as data:
        pass



if __name__ == '__main__':
	main()

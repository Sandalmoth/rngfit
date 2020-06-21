#!/usr/bin/python3


import datetime
import os

import click
import numpy as np
import pandas as pd
import toml


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

    path = 'data/' + control.inf + '/'
    if os.path.exists(path):
        print("User already exists")
    else:
        print("Creating user file")
        os.makedirs(path)

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
        userstats = pd.DataFrame({
            'date': [],
            'bodyweight': [],
        })

        exercises.to_csv(path + 'exercises.csv', index=False)
        workouts.to_csv(path + 'workouts.csv', index=False)
        userstats.to_csv(path + 'userstats.csv', index=False)


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
    path = 'data/' + control.inf + '/'
    assert os.path.exists(path)

    exercises = pd.read_csv(path + 'exercises.csv')
    exercises = exercises.append({
        'name': name,
        'min_weight': min_weight,
        'rounding': rounding
    }, ignore_index=True)
    exercises.to_csv(path + 'exercises.csv', index=False)


if __name__ == '__main__':
	main()

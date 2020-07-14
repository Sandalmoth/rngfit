#!/usr/bin/python3


import datetime
import os
import subprocess
import sys

import click
import numpy as np
import pandas as pd
import toml

import particles as prt


VERSION = '0.0.1'
EDITOR = os.environ.get('EDITOR', 'vim') # https://stackoverflow.com/a/39989442


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

        exercises = {}
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
        history = pd.DataFrame({
            'name': [],
            'm_mean': [],
            'm_std': [],
            'h_mean': [],
            'h_std': [],
            'e_mean': [],
            'e_std': [],
        })

        with open(path + 'exercises.toml', 'w') as out_toml:
            toml.dump(exercises, out_toml)
        workouts.to_csv(path + 'workouts.csv', index=False)
        userstats.to_csv(path + 'userstats.csv', index=False)
        history.to_csv(path + 'history.csv', index=False)


@main.command()
@pass_control
@click.option('-n', '--name', type=str)
@click.option('-r', '--rounding', type=float)
@click.option('-m', '--min-weight', type=float)
@click.option('-o', '--orm-guess', type=float)
def add_exercise(control, name, rounding, min_weight, orm_guess):
    """
    Add a new tracked exercise
    """
    path = 'data/' + control.inf + '/'
    assert os.path.exists(path)

    with open(path + 'exercises.toml', 'r') as in_toml:
        exercises = toml.load(in_toml)

    particles = prt.make_particles(orm_guess, orm_guess*0.2)
    exercises[name] = {
        'min_weight': min_weight,
        'rounding': rounding,
        'particles': particles,
    }

    with open(path + 'exercises.toml', 'w') as out_toml:
        toml.dump(exercises, out_toml)

    history = pd.read_csv(path + 'history.csv')
    means, sigmas = prt.estimate(particles)
    for i, var in enumerate(['m', 'h', 'e']):
        history[var + '_mean'].append(means[0])
        history[var + '_std'].append(sigmas[0])
    history.to_csv(path + 'history.csv', index=False)


@main.command()
@pass_control
@click.option('--resume/--no-resumme', default=False)
def session(control, resume):
    """
    Enter a workout session
    """
    path = 'data/' + control.inf + '/'
    assert os.path.exists(path)

    with open(path + 'exercises.toml', 'r') as in_toml:
        exercises = toml.load(in_toml)

    with open('entry.txt', 'a' if resume else 'w') as entry:
        if not resume:
            entry.write('date,name,time,reps,weight,rir\n')
        entry.flush()
        subprocess.call([EDITOR, entry.name])

        entry.seek(0)
        session = pd.read_csv('entry.txt')

    print(session)
    session.to_csv('entry.txt')

    workouts = pd.read_csv(path + 'workouts.csv')
    for x, y in zip(session.columns, workouts.columns):
        assert x == y
    for name in set(session['name']):
        assert name in exercises


if __name__ == '__main__':
	main()

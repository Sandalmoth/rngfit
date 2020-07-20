#!/usr/bin/python3


import datetime
import os
import re
import subprocess
import sys
import tempfile

import click
import numpy as np
import pandas as pd
import toml

from scipy.optimize import minimize

import particles as prt


VERSION = '0.0.2'
EDITOR = os.environ.get('EDITOR', 'vim') # https://stackoverflow.com/a/39989442


def iso_to_date(iso):
    y, m, d = re.match(r'(\d+)-(\d+)-(\d+)', iso).groups()
    return datetime.date(int(y), int(m), int(d))


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
            'date': [],
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

    particles, weights = prt.make_particles(orm_guess, orm_guess*0.2)
    exercises[name] = {
        'min_weight': min_weight,
        'rounding': rounding,
        'particles': particles,
        'weights': weights,
    }

    with open(path + 'exercises.toml', 'w') as out_toml:
        toml.dump(exercises, out_toml)

    history = pd.read_csv(path + 'history.csv')
    means, sigmas = prt.estimate(particles, weights)
    new_row = {
        'name': name,
        'date': datetime.date.today(),
    }
    for i, var in enumerate(['m', 'h', 'e']):
        new_row[var + '_mean'] = means[i]
        new_row[var + '_std'] = sigmas[i]
    history = history.append(new_row, ignore_index=True)
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


def random_choice(m):
    v = m.group(1).split()
    return str(np.random.choice(v))

def generate_and_fit(x, work, ability):
    work['weight'] = [x[0] for __ in range(len(work['time']))]
    prt.predict_rir(
        ability['m_mean'][0], ability['h_mean'][0], ability['e_mean'][0], work
    )
    return abs(work['est_rir'][-1] - work['rir'][-1])

def find_weight(name, rirset, history):
    # rirset has format sets, reps, rir, rest
    rs = [float(x) for x in rirset.groups()]
    rs[0] = int(rs[0])
    rs[1] = int(rs[1])
    name = name.groups(1)[0]
    print(name, rs)
    ability = history[history['name'] == name].iloc[[-1]]
    print(ability)

    rir = [None for x in range(rs[0])]
    rir[-1] = rs[2]
    work = {
        'time': np.arange(rs[0])*rs[3],
        'reps': [rs[1] for __ in range(rs[0])],
        'rir': rir,
    }
    # generate_and_fit.work = work
    # generate_and_fit.ability = ability

    res = minimize(
        lambda x: generate_and_fit(x, work, ability),
        100,
        bounds=[(0, None)],
        method='L-BFGS-B'
    )
    print(work)
    print(res)

@main.command()
@pass_control
@click.argument('template', type=click.Path())
def parse_template(control, template):
    """
    Parse a template creating a new workout programme
    """
    path = 'data/' + control.inf + '/'
    assert os.path.exists(path)

    with open(path + 'exercises.toml', 'r') as in_toml:
        exercises = toml.load(in_toml)

    history = pd.read_csv(path + 'history.csv')
    print(history)

    # parsing works each line in the following steps
    # randomly select a value in brackets
    re_rng = re.compile(r'\[([0-9\s\.]+)\]')
    # replace 1x2@3p4 with 1x2@[w]p4 where
    # [w] is a weight such that the last set has @3 rir
    re_name = re.compile(r'([A-Za-z]+)\s.*')
    re_rirset = re.compile(r'(\d+\.?\d*)x(\d+\.?\d*)@(\d+\.?\d*)p(\d+\.?\d*)')

    with open(template, 'r') as input:
        # with tempfile.NamedTemporaryFile(suffix=".tmp") as program:
        for line in input:
            line = re.sub(re_rng, random_choice, line)
            print(line, end='')
            name = re_name.match(line)
            rirset = re_rirset.search(line)
            if name and rirset:
                find_weight(name, rirset, history)

    print('')

if __name__ == '__main__':
	main()

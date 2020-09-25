# rngfit
Data driven exercise tracking and workout generation tools

## amraplanner.py ##
This application uses an improved model of 1RM estimation to create a training program that
adapts to an individuals absolute-strength and repetition-strength. It was designed to
select appropriate weights for a randomly generated number of reps, but could also be
used to make an adaptive verison of a more traditionally planned training program.

### Usage
First, make a copy of `amrap.toml` for a new user. Then, edit the first line
```toml
exercises = [ "squat", "deadlift", "benchpress", "press", "frontsquat", "row",]
```
to include all the exercises to be tracked and planned using this application.

For each included exercise, modify the weight and reps in the csv data. In the
example below, we have an initial 1RM guess of 155, and a 10RM guess of 120.
```toml
[squat]
rounding = 2.5
amraps = "date,reps,weight,rir\r\n2019-07-01,1,155,0\r\n2019-07-01,10,120,0\r\n"
```
The dates for these guesses should be far in the past, as above, which means that
new data will be weighted as more important.

With the input file set, we can parse a training template. See `amrap.template` for
details on how the templates work. To parse it run:
```bash
python3 amraplanner.py NAME parse -i amrap.template -o amrap.txt
cat amrap.program
```
The output is simply a text file. Replace NAME above with the filename of the user.
For instance using `amrap` with load the `amrap.toml` database.

After completing a workout, register the result of any amrap set using
```bash
python3 amraplanner.py NAME entry EXERCISE REPSxWEIGHT
```
or
```bash
python3 amraplanner.py NAME entry EXERCISE REPSxWEIGHTrRIR
```
replacing EXERCISE with the exercise name (defined earlier), 
REPS with the number of reps performed, WEIGHT with the weight used,
and optionally RIR with your estimated RIR (if the set was not to fail).

To monitor progress with some plots, use:
```bash
python3 amraplanner.py NAME plotfit
python3 amraplanner.py NAME plottime
```

If you design a custom program, it is important to have relatively rested sets close
to failure, ase these are used to track progress and ability. Sets that are not
fairly close to maximum performance, and with a large inaccurate RIR will not
allow for an accurate prediction.

```bash
python3 amraplanner.py plotprogram -i amrap.template
```
replacing `amrap.template` with the name of your template shows the INOL distribution,
which can be helpful for planning.


Optionally add other stats for plotting, though these are not used for any important
calculation.
```toml
data = "date,name,measurement\r\n"
options = [ "bodyweight",]
```
Using
```bash
python3 amraplanner.py NAME plotstat
```
will plot all these measuruments with a running mean and median.

### Usage example
Some data entry and plotting for the amrap example user. The `-d` option can specify
that something was done on a particular day. Note 
```bash
python3 amraplanner.py amrap entry -d 2020-06-1 bodyweight 97.3
python3 amraplanner.py amrap entry -d 2020-06-3 bodyweight 98.0
python3 amraplanner.py amrap entry -d 2020-06-5 bodyweight 96.2
python3 amraplanner.py amrap plotstat

python3 amraplanner.py amrap entry -d 2020-06-1 squat 7x135
python3 amraplanner.py amrap entry -d 2020-06-3 squat 3x150
python3 amraplanner.py amrap entry -d 2020-06-5 squat 5x142.5
python3 amraplanner.py amrap plotfit
python3 amraplanner.py amrap plottime
```
For the sake of brevity, only squat results were entered, but the procedure is the
same for any tracked exercise.

The way I recommend using this program is using a template similar to `amrap.template`, generate
a 4 day program, perform it, and enter the result of the amrap sets. The new data
will adjust the 1RM and repetition strength. Then, generate a new program, do it, enter the results, and so on.
As the template allows for randomized reps, that varies the program to lower the repeated bout effect.
And, as it adjust to your current ability, it will always be heavy enough.

## rngfit.py
Not yet complete

# Notes
The software is released under a permissive open source license.

I am not a training professional, or a medical practitioner. This nerdy lifting math
that I do for fun, you are responsible for your own training. I take no responsibility for injuries, 
or lack of gains resulting from using this program. Do it at your own risk.


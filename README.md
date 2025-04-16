# FLL_PathPlanner

# Setup

Note: This is for raw code

Unpack this zip file and open it with pycharm, but keep the spike file separate. Open this in the spike app under spike prime.

Set up your interpreter.

You will most likely get an error, here are the steps to fix them.

Delete the venv folder

Run this in your terminal 

python -m pip install --upgrade pip setuptools

pip install Pillow

Run main.py

Whenever the game changes, change the fll_mat.png file to the file of whatever the years game is, or if you want a custom field. I reccomend 1200x700, but you may have to adjust it based on your display.

Note: This is the easier method I reccomend, but the code is not tweakable.

Go to releases, and pick a release of your choice, then run that release.

Install the llsp3 file and open it in spike prime for robot code.

# Tuning

First you want to set up the scripts and divide the length of your image in pixels by the real life length of your field in inches, set that as PIXELS_PER_INCH

Next you want to get your robot and find the center distance between your wheels, and find the offset of that from the true center of your robot.

You want to put this in your gui as your offset.

You then want to measure your robot in whole, and make that your robot size, in inches.

After that, set up your starting point in inches from the robots wheel center from the 0,0 point of your image.

In the Spike Script, enter in your wheel circumfernce. Change the movement motors in the 3 functions to the movement motors in your robot. 

You have now finisheed tuning, save your gui values however as they do not save.


# Using the software.

## GUI

Once you have tuned and set your starting pose, click anywhere in the map to create an angle and distance. Click add turn step, and move your cursor to the direction you want to face for a turn in place (tank turn). Click add marker to add a message in the telemetry, so that you can know where to add your arm movements and such in your spike code, and click reset to restart everything.

## Spike

Once you have entered the spike software, things get very simple. For all of the movement, you will be using Advanced Gyro forward and Gyro Turn.

Repeat the following steps for every mark you have made

First, add a Gyro Turn block, the first input is the degrees from telemetry, the second input is speed of your choice.

Second, if you have a Move block, add an Advanced Gyro Forward block, the first input is the distance from telemetry, the second input is speed of your choice.

Throughout the code, you can add other motors such as arms and joints to complete your missions, or even waits, but simulation of these arent supported in the GUI, rather markers signify either a pause in code or arm movements.

# Credits

Written by Akhil Atyam, FRC 4188

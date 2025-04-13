# FLL_PathPlanner

Unpack this zip file and open it with pycharm, but keep the spike file seperate. Open this in the spike app under spike prime.

Set up your interpreter.

You will most likely get an error, here are the steps to fix them.

Delete the venv folder

Run this in your terminal 

python -m pip install --upgrade pip setuptools

pip install Pillow

Run main.py

Whenever the game changes, change the fll_mat.png file to the file of whatever the years game is, or if you want a custom field. I reccomend 1200x700, but you may have to adjust it based on your display.

# Tuning

First you want to set up the scripts and divide the length of your image in pixels by the real life length of your field in inches, set that as PIXELS_PER_INCH

Next you want to get your robot and find the center distance between your wheels, and find the offset of that from the true center of your robot.

You want to put this in your gui as your offset.

You then want to measure your robot in whole, and make that your robot size, in inches.

After that, set up your starting point in inches from the robots wheel center from the 0,0 point of your image.

In the Spike Script, enter in your wheel circumfernce.


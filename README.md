# DroneB
#### ©2022. Brett Huffman
#### v.01
---------------------------------------

The DroneB project is meant to act as a starting point for Tello Drone programming in the Intro to Programming course at Principia College.

## Files Included
There are several python files available for use:
- DroneB.py - the original stand-alone drone program for controlling the drone via a laptop.

- DroneBLib.py - A library module that can be included in your python project to expose the DroneB functionality to your own program.  This includes to sample files:

    - BasicB.py - Shows how to use the DroneBlib.py in a minimalistic way.

    - AdvB.py - a more advanced way to use DroneBlib.py.  Be sure to read the comments in the AdvB.py file to see how to use it.

## Installation
To use this library, you must include the following with the pip3 command:

- cv2
- tellopy
- av
- numpy
- pygame

Install these libraries with the command:

    pip3 install <library>

ie:

    pip3 install cv2

## Execution
Execute the programs with the following:

    python <script>

ie

    python ./DroneB.py

## Credits
Credit goes to the work by Hanyazou for many of the ideas in these modules:
https://github.com/hanyazou/TelloPy

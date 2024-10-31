# Millumin Countdown OSC
Made on quickly onsite to provide the TRT countdown via OSC to then be displayed in Touchdesigner.

## OSC Messages
Millumin OSC API found [here](https://github.com/anome/millumin-dev-kit/wiki/OSC-documentation).

## Usage
Currently, it listens to all ```launchedColumn``` commands on all boards. It then sends the column name, minutes, and seconds as seperate arguments.

- Edit the CONFIG section to set the IP and port of the Millumin instance and set destination(s) IP and port.
- Running the script will then create a ```ports.txt``` file which the script will then use

## Dependencies
osc4py3
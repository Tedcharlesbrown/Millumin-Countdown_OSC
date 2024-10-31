# Millumin Countdown OSC
Made on quickly onsite to provide the TRT countdown via OSC to then be displayed in Touchdesigner.

## OSC Messages
Millumin OSC API found [here](https://github.com/anome/millumin-dev-kit/wiki/OSC-documentation).

## Usage
Currently, it listens to all ```launchedColumn``` commands on all boards. It then sends the column name, minutes, and seconds as seperate arguments.

- Edit the CONFIG section to set the IP and port of the Millumin instance and set destination(s) IP and port.
- Running the script will then create a ```ports.txt``` file which the script will then use

```
config = {
    "incoming_port": 8001,
    "outgoing_address": "/millumin/countdown",
    "outgoing_ip": "192.168.101.255,127.0.0.1",
    "outgoing_port": "10000,9000",
    "stopped_text": "STOPPED",
    "countdown_loop": "FALSE"               
}
```
- ```incoming_port``` is the port the script listens to for Millumin commands
- ```outgoing_address``` is the OSC address to send the countdown to
- ```outgoing_ip``` is a comma separated list of IPs to send the countdown to
- ```outgoing_port``` is a comma separated list of ports to send the countdown to
- ```stopped_text``` currently not implemented
- ```countdown_loop``` If set to FALSE, any column name with "Loop" will send minutes = 0 and seconds = 0

## Dependencies
osc4py3
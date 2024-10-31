import os
import time
from osc4py3.as_eventloop import osc_startup, osc_process, osc_udp_server, osc_udp_client, osc_method, osc_send, osc_terminate
from osc4py3 import oscmethod as osm
from osc4py3 import oscbuildparse as obp

# Filepath for ports.txt configuration
CONFIG_FILE = "ports.txt"

# Default configuration (if ports.txt doesn't exist)
config = {
    "incoming_port": 8001,
    "outgoing_address": "/millumin/countdown",
    "outgoing_ip": "192.168.101.255",
    "outgoing_port": 10000
}

# Variables to store the current and last values
current_column_name = ""
last_column_name = ""
last_minutes = -1
last_seconds = -1

# Load configuration from ports.txt
def load_config():
    if not os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'w') as f:
            for key, value in config.items():
                f.write(f"{key}={value}\n")
        print("ports.txt created with default settings.")
    else:
        with open(CONFIG_FILE, 'r') as f:
            for line in f:
                key, value = line.strip().split("=")
                config[key.strip()] = int(value.strip()) if "port" in key else value.strip()

# Initialize OSC settings
def initialize_osc():
    osc_startup()
    osc_udp_server("0.0.0.0", config["incoming_port"], "incoming")
    osc_udp_client(config["outgoing_ip"], config["outgoing_port"], "outgoing")

# Handle /millumin/layer:layer/media/time message
def handle_media_time(address, *args):
    global last_column_name, last_minutes, last_seconds, current_column_name
    current_time, total_time = args
    remaining_time = max(total_time - current_time, 0)
    minutes = int(remaining_time) // 60
    seconds = int(remaining_time) % 60

    # Only print/send if there's a change
    if (current_column_name != last_column_name) or (minutes != last_minutes) or (seconds != last_seconds):
        print(f"Sending OSC to: {config['outgoing_ip']}:{config['outgoing_port']}, Address: {config['outgoing_address']}, Data: {current_column_name}, {minutes}, {seconds}")
        msg = obp.OSCMessage(config["outgoing_address"], None, [current_column_name, minutes, seconds])
        # msg = obp.OSCMessage(config["outgoing_address"], None, [f"'{current_column_name}', {minutes}, {seconds}"])
        osc_send(msg, "outgoing")

        # Update last sent values
        last_column_name, last_minutes, last_seconds = current_column_name, minutes, seconds

# Handle /millumin/board/launchedColumn message
def handle_launched_column(address, *args):
    global current_column_name
    column_index, column_name = args
    current_column_name = column_name  # Update current column name

# Set OSC message handlers
# Set OSC message handlers
def set_osc_handlers():
    # Catch all layer media time messages regardless of the layer number
    osc_method("/millumin/layer:layer*/media/time", handle_media_time, argscheme=osm.OSCARG_ADDRESS + osm.OSCARG_DATAUNPACK)
    osc_method("/millumin/board/launchedColumn", handle_launched_column, argscheme=osm.OSCARG_ADDRESS + osm.OSCARG_DATAUNPACK)


# Main function
def main():
    load_config()
    initialize_osc()
    set_osc_handlers()
    
    print(f"Listening for incoming OSC on port {config['incoming_port']}. Press Ctrl+C to stop.")
    try:
        while True:
            osc_process()
            time.sleep(0.01)
    except KeyboardInterrupt:
        print("Shutting down OSC server.")
    finally:
        osc_terminate()

if __name__ == "__main__":
    main()

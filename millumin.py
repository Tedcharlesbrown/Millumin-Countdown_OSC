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
    "outgoing_ip": "192.168.101.255,127.0.0.1",
    "outgoing_port": "10000,9000",
    "stopped_text": "STOPPED",
    "countdown_loop": "FALSE"               
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
                config[key.strip()] = int(value.strip()) if "port" in key and ',' not in value else value.strip()

# Initialize OSC settings for multiple outgoing clients
def initialize_osc():
    osc_startup()
    osc_udp_server("0.0.0.0", config["incoming_port"], "incoming")

    # Parse outgoing IPs and ports as lists
    outgoing_ips = config["outgoing_ip"].split(",")
    outgoing_ports = config["outgoing_port"].split(",")
    
    # Initialize an OSC client for each IP and port
    for i, (ip, port) in enumerate(zip(outgoing_ips, outgoing_ports)):
        client_name = f"outgoing_{i}"
        osc_udp_client(ip.strip(), int(port.strip()), client_name)
        print(f"Initialized OSC client for {ip.strip()}:{port.strip()} with name {client_name}")

# Send message to all configured OSC clients
def send_to_all_clients(message):
    client_count = len(config["outgoing_ip"].split(","))
    for i in range(client_count):
        client_name = f"outgoing_{i}"
        osc_send(message, client_name)

# Handle /millumin/layer:layer*/media/time message
def handle_media_time(address, *args):
    global last_column_name, last_minutes, last_seconds, current_column_name
    current_time, total_time = args
    remaining_time = max(total_time - current_time, 0)
    minutes = int(remaining_time) // 60
    seconds = int(remaining_time) % 60

    if config["countdown_loop"].upper() == "FALSE":
        minutes = 0
        seconds = 0

    if (current_column_name != ""):
    # Only print/send if there's a change
        if (current_column_name != last_column_name) or (minutes != last_minutes) or (seconds != last_seconds):
            send_osc_message(config["outgoing_address"], current_column_name, minutes, seconds)

            # Update last sent values
            last_column_name, last_minutes, last_seconds = current_column_name, minutes, seconds

# Handle /millumin/board/launchedColumn message
def handle_launched_column(address, *args):
    global current_column_name
    column_index, column_name = args
    current_column_name = column_name  # Update current column name

# Handle /millumin/board/stoppedColumn message
def handle_stopped_column(address, *args):
    global last_column_name, last_minutes, last_seconds, current_column_name
    current_column_name = config["stopped_text"]  # Reset current column name
    last_column_name, last_minutes, last_seconds = "", 0, 0  # Reset last sent values


    send_osc_message(config["outgoing_address"], current_column_name, last_minutes, last_seconds)

def send_osc_message(address, *args):
    print(f"Sending OSC to: {config["outgoing_ip"]}, Address: {config['outgoing_address']}, Data: {current_column_name}, {last_minutes}, {last_seconds}")
    msg = obp.OSCMessage(address, None, args)
    send_to_all_clients(msg)

# Set OSC message handlers
def set_osc_handlers():
    # Catch all layer media time messages regardless of the layer number
    osc_method("/millumin/layer:layer*/media/time", handle_media_time, argscheme=osm.OSCARG_ADDRESS + osm.OSCARG_DATAUNPACK)
    osc_method("/millumin/board/launchedColumn", handle_launched_column, argscheme=osm.OSCARG_ADDRESS + osm.OSCARG_DATAUNPACK)
    osc_method("/millumin/board/stoppedColumn", handle_stopped_column, argscheme=osm.OSCARG_ADDRESS + osm.OSCARG_DATAUNPACK)

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

import requests
import socket
import psutil
import logging

# Set up logging
logging.basicConfig(filename='send_data.log', level=logging.INFO)

def get_cpu_usage():
    return psutil.cpu_percent(interval=1)

def get_temperature():
    temp = None
    try:
        with open("/sys/class/thermal/thermal_zone0/temp", "r") as f:
            temp = float(f.read()) / 1000.0
    except FileNotFoundError:
        temp = 0.0
    return temp

pi_id = socket.gethostname()
data = {
    'pi_id': pi_id,
    'cpu_usage': get_cpu_usage(),
    'temperature': get_temperature(),
}

try:
    response = requests.post(
        "http://gruppe10.codexenmo.no/receive_data",
        json=data,

        verify=True  # Ensure SSL verification
    )
    response.raise_for_status()
    logging.info(f"Data sent successfully at {response.json()}")
except requests.exceptions.RequestException as e:
    logging.error(f"Error sending data: {e}")

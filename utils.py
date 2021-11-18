import math
import socket

KEY_OMEGA = 'omega'
KEY_SPEED = 'speed'
KEY_ADDRESS = "address"
KEY_ACTION = "action"
KEY_CLIENT_ID = "client_id"
KEY_TYPE = "type"

TYPE_MONITOR = "monitor"
TYPE_REGISTER = "register"
TYPE_CONTROL = "control"
TYPE_START = "start"
TYPE_STOP = "stop"


def omega_to_speed(omega):
	return (omega * 30) / math.pi


def speed_to_omega(speed):
	return (speed * math.pi) / 30


def print_state(state_names, states, limit_values):
	for i in range(len(state_names)):
		value = states[i]
		value *= limit_values[state_names[i]]
		print(f"| {state_names[i]} = {value} |", end='')

		if state_names[i] == KEY_OMEGA:
			print(f"| speed = {omega_to_speed(value)} |", end='')

	print("")

def get_open_port():
	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	s.bind(('', 0))
	port = s.getsockname()[1]
	s.close()
	return port

def get_host_ip():

	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	s.connect(('8.8.8.8', 80))
	ip = s.getsockname()[0]
	s.close()

	return ip




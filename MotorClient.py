import sys

from motor import Motor
import time
from simple_pid import PID
from utils import *
import socket
import matplotlib.pylab as plt
import json
import os

from configs.ConfigLoader import ConfigLoader


class MotorClient:

    def __init__(self, client_id, target_rpm):

        self.client_id = client_id
        self.target_rpm = target_rpm

        self.motor = Motor(self.client_id, rpm=self.target_rpm)

        self.config_loader = ConfigLoader()

        self.control_interval = self.config_loader.get_control_interval()
        self.running_time = self.config_loader.get_running_time()

        self.client_address = self.config_loader.get_client_address()
        self.server_address = None

        self.client_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.client_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.client_sock.bind((self.client_address[0], self.client_address[1]))

    def start(self):
        self.motor.start()
        start_time = time.time()
        while(True):
            time.sleep(self.control_interval)
            states = self.motor.get_states()
            if not states:
                continue

            self.upload_monitor_info(states[KEY_OMEGA], states[KEY_SPEED])
            data = self.client_sock.recv(500).decode()

            try:
                data = json.loads(data)
                if data["type"] == TYPE_CONTROL:
                    action = data["action"]
                    self.motor.update_action(action)
            except Exception as e:
                print("指令数据包解析出错！", e)

            progress = round(((time.time() - start_time) / self.running_time) * 100, 1)
            print("\r", end="")
            print("Download progress: {}% ".format(progress), end="")
            sys.stdout.flush()

            if(time.time() - start_time >= self.running_time):
                break
        print("运行结束！")
        self.stop()

    def register(self):

        print("waiting for server signal...")
        while(True):
            data, address = self.client_sock.recvfrom(500)
            data = data.decode()
            try:
                data = json.loads(data)
                if data["type"] == TYPE_START:
                    self.server_address = address
                    break
            except Exception as e:
                print("数据包解析出错！", e)

        register_data = {"type": TYPE_REGISTER, "client_id": self.client_id, "address": self.client_address,
                         "target_rpm": self.target_rpm, "target_omega": self.motor.get_nominal_values()[KEY_OMEGA]}

        pkt = json.dumps(register_data)
        self.client_sock.sendto(pkt.encode(), self.server_address)

    def upload_monitor_info(self, omega, speed):
        monitor_data = {"type": TYPE_MONITOR, KEY_CLIENT_ID: self.client_id, KEY_OMEGA: omega, KEY_SPEED: speed}
        pkt = json.dumps(monitor_data)
        self.client_sock.sendto(pkt.encode(), self.server_address)

    def stop(self):
        print("stopping ...")
        stop_msg = {"type": "stop", KEY_CLIENT_ID: self.client_id}
        pkt = json.dumps(stop_msg).encode()
        self.client_sock.sendto(pkt, self.server_address)
        self.client_sock.close()


if __name__ == "__main__":
    motorClient = MotorClient("001", 4000)
    motorClient.register()
    motorClient.start()
    sys.exit()

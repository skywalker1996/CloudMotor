# coding: utf-8

import sys

from simplejson import JSONDecodeError

from motor import Motor
import time
from simple_pid import PID
from utils.utils import *
import socket
import matplotlib.pylab as plt
import json
import os
import argparse

from configs.configLoader import configLoader


class MotorClient:
    """
    MotorClient
    """
    def __init__(self, client_id, target_rpm, mark, control_interval):

        self.client_id = client_id
        self.target_rpm = target_rpm
        self.control_interval = control_interval

        self.mark = mark

        self.motor = Motor(id=self.client_id, nominal_rpm=self.target_rpm)

        self.config_loader = configLoader()

        self.running_time = self.config_loader.get_running_time()
        self.client_address = self.config_loader.get_client_address()
        self.server_address = None

        self.client_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.client_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.client_sock.bind((self.client_address[0], self.client_address[1]))

    def start(self):
        """
        start MotorClient
        """
        self.motor.start()
        start_time = time.time()
        while (True):
            time.sleep(self.control_interval/1000)
            states = self.motor.get_states()
            if not states:
                continue

            self.upload_monitor_info(states[KEY_OMEGA], states[KEY_SPEED], states[KEY_CURRENT], round(time.time()-start_time, 3))
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
            print(f"experiment progress: {int(progress)}% ", end="")
            sys.stdout.flush()

            if time.time() - start_time >= self.running_time:
                break
        print("运行结束！")
        self.stop()

    def register(self):
        """
        send registry message
        """
        print("waiting for server signal...")
        while (True):
            data, address = self.client_sock.recvfrom(500)
            data = data.decode()
            try:
                data = json.loads(data)
                if data["type"] == TYPE_START:
                    self.server_address = address
                    break
            except JSONDecodeError as json_error:
                print("数据包解析出错！", json_error)

        register_data = {"type": TYPE_REGISTER, "client_id": self.client_id, "address": self.client_address,
                         "target_rpm": self.target_rpm, "target_omega": self.motor.get_nominal_values()[KEY_OMEGA]}

        pkt = json.dumps(register_data)
        self.client_sock.sendto(pkt.encode(), self.server_address)

    def upload_monitor_info(self, omega, speed, current, time):
        """
        upload monitor info
        """
        monitor_data = {"type": TYPE_MONITOR, KEY_CLIENT_ID: self.client_id, KEY_OMEGA: omega,
                        KEY_SPEED: speed, KEY_CURRENT: current, KEY_TIME: time}

        pkt = json.dumps(monitor_data)
        self.client_sock.sendto(pkt.encode(), self.server_address)

    def stop(self):
        """
        stop
        """
        print("stopping ...")
        stop_msg = {"type": "stop", KEY_CLIENT_ID: self.client_id}
        pkt = json.dumps(stop_msg).encode()
        self.client_sock.sendto(pkt, self.server_address)
        self.client_sock.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument('--id', default="001")
    parser.add_argument('--target_speed', type=int, default=4000)
    parser.add_argument('--mark', default="default")
    parser.add_argument('--interval', default=0.01, type=float)

    args = parser.parse_args()

    motorClient = MotorClient(args.id, args.target_speed, args.mark, args.interval)
    motorClient.register()
    motorClient.start()
    sys.exit()

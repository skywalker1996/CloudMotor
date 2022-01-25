# coding: utf-8

import socket
from configs.configLoader import configLoader
from threading import Lock, Thread
import json
import time
from utils import *
from simple_pid import PID


class MotorServer:

    def __init__(self):

        self.config_loader = configLoader()

        self.server_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server_sock.bind(self.config_loader.get_server_address())

        self.client_info = {}
        self.records = {}

        self.control_thread = Thread(target=self.control_service, args=())

        self.client_address = self.config_loader.get_client_address()

        self._exit_flag = False

    def start(self):

        self.control_thread.setDaemon(True)
        self.control_thread.start()

    def control_service(self):
        print("start control service")
        start_client_data = json.dumps({"type": TYPE_START}).encode()
        self.server_sock.sendto(start_client_data, self.client_address)
        while True:
            data = self.server_sock.recv(500).decode()
            try:
                data = json.loads(data)
                if KEY_TYPE not in data:
                    continue
                if data[KEY_TYPE] == TYPE_REGISTER:
                    client_id = data["client_id"]
                    client_address = data["address"]
                    target_rpm = data["target_rpm"]
                    target_omega = data["target_omega"]
                    controller = PID(1, 0.1, 0.05, setpoint=target_omega)
                    controller.output_limits = (0, 1)

                    self.client_info[client_id] = {"address": tuple(client_address), "target_rpm": target_rpm,
                                                   "target_omega": target_omega, "controller": controller}

                    self.records[client_id] = {"sum": 0.0, "count": 0}
                    print(f"Motor client {client_id} from {client_address} connected, target_omega: {target_omega}")
                elif data[KEY_TYPE] == TYPE_MONITOR:
                    client_id = data[KEY_CLIENT_ID]
                    state_omega = data[KEY_OMEGA]
                    state_speed = data[KEY_SPEED]
                    if client_id in self.client_info:
                        action = round(self.client_info[client_id]["controller"](state_omega))
                        self.send_control_pkt(client_id, action)

                        omega_err_abs = abs(state_omega - self.client_info[client_id]["target_omega"])
                        self.records[client_id]["sum"] += omega_err_abs / self.client_info[client_id]["target_omega"]
                        self.records[client_id]["count"] += 1
                    else:
                        print("motorClient 信息未注册！")

                elif data[KEY_TYPE] == TYPE_STOP:
                    client_id = data[KEY_CLIENT_ID]
                    qoe = round(self.records[client_id]["sum"] / self.records[client_id]["count"], 4)
                    print(f"Motor Client {client_id} finished, 平均控制误差率 = {qoe * 100}%")

                    del self.client_info[client_id]
                    del self.records[client_id]
                    self._exit_flag = True
                    break

            except Exception as e:
                print("monitor 数据包解析出错 ：", e)

    def send_control_pkt(self, client_id, action):

        client_address = self.client_info[client_id]["address"]

        control_data = {"type": TYPE_CONTROL, "action": action}
        pkt = json.dumps(control_data).encode()

        self.server_sock.sendto(pkt, client_address)

    def get_exit_flag(self):
        return self._exit_flag


motor_server = MotorServer()
motor_server.start()
while not motor_server.get_exit_flag():
    time.sleep(1)

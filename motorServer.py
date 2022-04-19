# coding: utf-8

import socket
import traceback

from configs.configLoader import configLoader
from threading import Lock, Thread
import json
import time
from utils.utils import *
from simple_pid import PID
import os
import pandas as pd
import redis

class MotorServer:
    """
    MotorServer
    """
    def __init__(self):

        self.config_loader = configLoader()
        self.time_mark = str(time.strftime('%Y_%m_%d_%H_%M_%S', time.localtime(time.time())))
        self.server_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        print("bind ", self.config_loader.get_server_address())
        self.server_sock.bind(self.config_loader.get_server_address())

        redis_addr =  self.config_loader.get_redis_address()
        self.redis_client = redis.StrictRedis(host=redis_addr[0], port=redis_addr[1], db=0, decode_responses=True)
    
        self.client_info = {}
        self.records = {}
        self.logs = {}

        self.control_thread = Thread(target=self.control_service, args=())

        self.client_address = self.config_loader.get_client_address()

        self._exit_flag = False

        self.throughput = 0
        self.THROUGHPUT_PERIOD = 1  # 1s

        self.server_log = {}
        self.server_log["throughput"] = []

    def start(self):
        """
        start runnning
        """
        self.control_thread.setDaemon(True)
        self.control_thread.start()

    def control_service(self):
        """
        control service
        """
        print("start control service")
        start_client_data = json.dumps({"type": TYPE_START}).encode()
        self.server_sock.sendto(start_client_data, self.client_address)
        start_time = time.time()
        control_data_total = 0
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
                    controller = PID(1, 0.5, 0.05, setpoint=target_omega)
                    controller.output_limits = (0, 1)

                    self.client_info[client_id] = {"address": tuple(client_address), "target_rpm": target_rpm,
                                                   "target_omega": target_omega, "controller": controller}

                    self.records[client_id] = {"sum": 0.0, "count": 0}
                    self.logs[client_id] = {"time": [], "speed": [], "current":[]}
                    print(f"Motor client {client_id} from {client_address} connected, target_omega: {target_omega}")
                elif data[KEY_TYPE] == TYPE_MONITOR:
                    client_id = data[KEY_CLIENT_ID]
                    state_omega = data[KEY_OMEGA]
                    state_speed = data[KEY_SPEED]
                    state_current = data[KEY_CURRENT]
                    timestamp = data[KEY_TIME]
                    if client_id in self.client_info:
                        # action = round(self.client_info[client_id]["controller"](state_omega))
                        action = self.client_info[client_id]["controller"](state_omega)
                        data_size = self.send_control_pkt(client_id, [action])
                        control_data_total+=data_size
                        if(time.time()-start_time >= self.THROUGHPUT_PERIOD):
                            self.throughput = control_data_total
                            self.server_log["throughput"].append(self.throughput)
                            start_time = time.time()
                            control_data_total = 0
                            print(f"throughput:{self.throughput}")

                        omega_err_abs = abs(state_omega - self.client_info[client_id]["target_omega"])
                        self.records[client_id]["sum"] += omega_err_abs / self.client_info[client_id]["target_omega"]
                        self.records[client_id]["count"] += 1
                        self.logs[client_id]["time"].append(timestamp)
                        self.logs[client_id]["speed"].append(state_speed)
                        self.logs[client_id]["current"].append(state_current)
                    else:
                        print("motorClient 信息未注册！")


                elif data[KEY_TYPE] == TYPE_STOP:
                    client_id = data[KEY_CLIENT_ID]
                    avg_err = round(self.records[client_id]["sum"] / self.records[client_id]["count"], 4)
                    self.avg_precision = 100-avg_err*100
                    self.redis_client.set("result", self.avg_precision)
                    print(f"Motor Client {client_id} finished, 平均控制精度 = {self.avg_precision}%")
                    self.save_logs(client_id)
                    del self.client_info[client_id]
                    del self.records[client_id]
                    self._exit_flag = True
                    break

            except Exception as e:
                print(traceback.print_exc())

    def send_control_pkt(self, client_id, action):
        """
        send control packets
        """
        client_address = self.client_info[client_id]["address"]

        control_data = {"type": TYPE_CONTROL, "action": action}
        pkt = json.dumps(control_data).encode()

        self.server_sock.sendto(pkt, client_address)
        return len(pkt)

    def get_exit_flag(self):
        """
        get exit flag
        """
        return self._exit_flag

    def save_logs(self, client_id):
        """
        save logs
        """
        save_dir = f"./logs/{self.time_mark}/{client_id}"
        current_log_dir = f"./logs/current_log"
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
        if not os.path.exists(current_log_dir):
            os.makedirs(current_log_dir)

        record_file = f"motor_{client_id}.csv"
        server_log_file = f"server_log.csv"
        record_dataframe = pd.DataFrame.from_dict(self.logs[client_id])
        # save log in time marked folder
        record_dataframe.to_csv(os.path.join(save_dir, record_file))

        # save log in current_log folder (keep updated)
        record_dataframe.to_csv(os.path.join(current_log_dir, record_file))

        server_log_dataframe = pd.DataFrame.from_dict(self.server_log)
        server_log_dataframe.to_csv(os.path.join(current_log_dir, server_log_file))

        print("************* save logs in file: ", os.path.join(save_dir, record_file))


motor_server = MotorServer()
motor_server.start()
while not motor_server.get_exit_flag():
    time.sleep(1)

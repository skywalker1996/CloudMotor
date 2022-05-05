# coding: utf-8

from curses import delay_output
from netrc import netrc
import socket
import traceback

from configs.configLoader import configLoader
from threading import Lock, Thread
import json
import time
from utils.utils import *
from utils.networkSim import NetworkSim
from simple_pid import PID
import os
import pandas as pd
import redis
import multiprocessing
import numpy as np
import queue
import random
import argparse


class MotorServer:
    """
    MotorServer
    """
    def __init__(self, delay_mean, loss_mean, name):

        self.config_loader = configLoader()
        self.experiment_name = name 
        self.delay_mean = delay_mean
        self.loss_mean = loss_mean

        self.server_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # print("bind ", self.config_loader.get_server_address())
        self.server_sock.bind(self.config_loader.get_server_address())
        redis_addr =  self.config_loader.get_redis_address()
        self.redis_client = redis.StrictRedis(host=redis_addr[0], port=redis_addr[1], db=0, decode_responses=True)
    
        self.client_info = {}
        self.records = {}
        self.logs = {}

        self.client_address = self.config_loader.get_client_address()

        self.use_trace = self.config_loader.get_use_trace()

        self._exit_flag = False

        self.throughput = 0
        self.THROUGHPUT_PERIOD = 1  # 1s

        self.server_log = {}
        self.server_log[KEY_THROUGHPUT] = []

        self.networkSim = NetworkSim(delay_mean, loss_mean, update_freq = 5)

        self.host_name = socket.gethostname()
        self.redis_result_key = ':'.join(["motor",self.host_name,"result"])

        self.send_queue = queue.Queue()
        self.recv_queue = queue.Queue()

        self.control_thread = Thread(target=self.control_service, args=())
        self.recv_thread = Thread(target=self.recv_service, args=())
        self.pacer_thread = Thread(target=self.pacer, args=())

    def start(self):
        """
        start runnning
        """
        self.control_thread.daemon = True
        self.control_thread.start()

        self.recv_thread.daemon = True
        self.recv_thread.start()
        
        if not self.use_trace:
            self.pacer_thread.daemon = True
            self.pacer_thread.start()
            
        self.control_thread.join()

    def recv_service(self):
        while True:
            data = self.server_sock.recv(500).decode()
            self.recv_queue.put(data)

    def control_service(self):
        """
        control service
        """
        # print("start control service")
        start_client_data = json.dumps({"type": TYPE_START}).encode()
        self.server_sock.sendto(start_client_data, self.client_address)
        start_time = time.time()
        control_data_total = 0
        while True:
            data = self.recv_queue.get()
            try:
                data = json.loads(data)
                if KEY_TYPE not in data:
                    continue
                if data[KEY_TYPE] == TYPE_REGISTER:
                    client_id = data[KEY_CLIENT_ID]
                    client_address = data[KEY_ADDRESS]
                    target_rpm = data[KEY_TARGET_RPM]
                    target_omega = data[KEY_TARGET_OMEGA]
                    controller = PID(8, 1, 1, setpoint=target_omega)
                    controller.output_limits = (0, 1)

                    self.client_info[client_id] = {KEY_ADDRESS: tuple(client_address), KEY_TARGET_RPM: target_rpm,
                                                   KEY_TARGET_OMEGA: target_omega, KEY_CONTROLLER: controller}
                        
                    
                    self.records[client_id] = {"sum": 0.0, "omega_err": [], "count": 0}
                    self.logs[client_id] = {KEY_TIME: [], KEY_SPEED: [], KEY_OMEGA: [], KEY_CURRENT: [], KEY_OMEGA_ERR: []}
                    print(f"Motor client {client_id} from {client_address} connected, target_omega: {target_omega}")
                    
                elif data[KEY_TYPE] == TYPE_MONITOR:
                    client_id = data[KEY_CLIENT_ID]
                    state_omega = data[KEY_OMEGA]
                    state_speed = data[KEY_SPEED]
                    state_current = data[KEY_CURRENT]
                    timestamp = data[KEY_TIME]
                    if client_id in self.client_info:
                        # action = round(self.client_info[client_id]["controller"](state_omega))
                        action = self.client_info[client_id][KEY_CONTROLLER](state_omega)
                        data_size = self.send_control_pkt(client_id, [action])
                        control_data_total+=data_size
                        if(time.time()-start_time >= self.THROUGHPUT_PERIOD):
                            self.throughput = control_data_total
                            self.server_log[KEY_THROUGHPUT].append(self.throughput)
                            start_time = time.time()
                            control_data_total = 0
                            # print(f"throughput:{self.throughput}")

                        omega_err_abs = abs(state_omega - self.client_info[client_id][KEY_TARGET_OMEGA])
                        if(timestamp >= 1):
                            self.records[client_id]["sum"] += omega_err_abs / self.client_info[client_id][KEY_TARGET_OMEGA]
                            self.records[client_id]["count"] += 1
                            self.records[client_id]["omega_err"].append(omega_err_abs)
                            

                        self.logs[client_id][KEY_TIME].append(timestamp)
                        self.logs[client_id][KEY_SPEED].append(state_speed)
                        self.logs[client_id][KEY_OMEGA].append(state_omega)
                        self.logs[client_id][KEY_OMEGA_ERR].append(omega_err_abs)
                        self.logs[client_id][KEY_CURRENT].append(state_current)
                        
                    else:
                        print("motorClient 信息未注册！")

                elif data[KEY_TYPE] == TYPE_STOP:
                    client_id = data[KEY_CLIENT_ID]

                    avg_err = round(self.records[client_id]["sum"] / self.records[client_id]["count"], 4)
                    self.avg_precision = 100-avg_err*100
                    self.precision_sla = self.sla_comp(self.records[client_id]["omega_err"], self.client_info[client_id][KEY_TARGET_OMEGA])
                    self.precision_sla.append(self.avg_precision)
                    self.redis_client.set(self.redis_result_key, str(self.precision_sla))
                    print(f"Motor Client {client_id} finished, 平均控制精度 = {self.avg_precision}%")
                    self.save_logs(client_id)
                    del self.client_info[client_id]
                    del self.records[client_id]
                    self._exit_flag = True
                    self.send_queue.put(None)
                    break

            except Exception as e:
                print(traceback.print_exc())

    def sla_comp(self, omega_err_seq, target_omega):
        
        sorted_seq = sorted(omega_err_seq)
        total_count = len(sorted_seq)
        results = []

        for p in range(90,100):
            index = int(total_count * (p/100.0))
            omega_err_abs = sorted_seq[index]
            err_rate = omega_err_abs / target_omega
            # print(f"index = {index} and omega_err_abs = {omega_err_abs} and err_rate = {err_rate} ")
            precision = 100-err_rate*100
            results.append(precision)
        
        return results

            


    def send_control_pkt(self, client_id, action):
        """
        send control packets
        """
        client_address = self.client_info[client_id]["address"]
        control_data = {"type": TYPE_CONTROL, "action": action}
        pkt = json.dumps(control_data).encode()

        next_delay = self.networkSim.get_next_delay()
        next_loss = self.networkSim.packet_loss()

        if self.use_trace:
            self.server_sock.sendto(pkt, client_address)
        else:
            data = {}
            data["address"] = client_address
            data["send_time"] = time.time()*1000 + next_delay
            data["packet_loss"] = next_loss
            data['pkt'] = pkt
            self.send_queue.put(data)

        return len(pkt)

    def pacer(self): 
        while(True):
            data = self.send_queue.get()
            if(not data):
                break
            address = data["address"]
            send_time = data["send_time"]
            packet_loss = data["packet_loss"]
            pkt = data["pkt"]
            while(time.time()*1000<send_time):
                time.sleep(0.0001)
                continue
            if packet_loss:
                continue
            else:
                self.server_sock.sendto(pkt, address)

        
    def get_exit_flag(self):
        """
        get exit flag
        """
        return self._exit_flag

    def save_logs(self, client_id):
        """
        save records
        """
        record_dir = f"./logs/{self.experiment_name}"
        current_record_dir = f"./logs/current_record"

        if not os.path.exists(record_dir):
            os.makedirs(record_dir)
        if not os.path.exists(current_record_dir):
            os.makedirs(current_record_dir)
        
        record_file = f"{self.delay_mean}_{self.loss_mean}_record.csv"
        current_record_file = f"motor_{client_id}.csv"

        record_dataframe = pd.DataFrame.from_dict(self.logs[client_id])
        # save record in time marked folder
        record_dataframe.to_csv(os.path.join(record_dir, record_file))
        # save record in current_record folder (keep updated)
        record_dataframe.to_csv(os.path.join(current_record_dir, current_record_file))

        print("************* save records in file: ", os.path.join(record_dir, record_file))

if __name__ == '__main__':

    parser = argparse.ArgumentParser()

    parser.add_argument('--delay_mean', type=float, default=0)
    parser.add_argument('--loss_mean', type=float, default=0)
    parser.add_argument('--name', type=str, default="default")

    args = parser.parse_args()

    motor_server = MotorServer(delay_mean = args.delay_mean, loss_mean = args.loss_mean, name = args.name)
    motor_server.start()
    # while not motor_server.get_exit_flag():
    #     time.sleep(1)

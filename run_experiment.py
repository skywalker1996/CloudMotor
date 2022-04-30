from subprocess import Popen,PIPE

import time
import socket 
from attr import field
from matplotlib.pyplot import pause
import numpy as np
import tempfile
import os
from configs.configLoader import configLoader
import pandas as pd
import redis
import csv


def run_experiment(delay_mean, loss_mean, control_interval):
    """
    run experiment function
    """

    config_loader = configLoader()
    use_trace = config_loader.get_use_trace()
    trace_file = config_loader.get_trace_path()
    base_delay = config_loader.get_base_delay()

    # kill existing programs
    print("starting ...")
    # Popen("kill -9 $(ps -aux | grep mm-delay | awk '{print $2}')", shell=True)
    Popen("sh ./kill.sh", shell=True, stdout=PIPE, stderr=PIPE)
    time.sleep(2)

    server_comds = f'python3 motorServer.py --delay_mean {delay_mean} --loss_mean {loss_mean}'
    client_comds = f'python3 motorClient.py --id 001 --target_speed 3000 --interval {control_interval}'

    if use_trace:
        # start monax client and serve
        start_server = ['mm-delay', str(base_delay),
                        'mm-link', trace_file, trace_file,
                        '--uplink-queue=droptail --uplink-queue-args=packets=2048',
                        '-- sh -c ', f"'{server_comds}'"]

        start_server = ' '.join(start_server)
    else:
        start_server = server_comds

    start_client = client_comds
    # print(start_server)
    # print(start_client)

    client = Popen(start_client, shell=True)
    time.sleep(3)
    server = Popen(start_server, shell=True)

    print("experiment start success")

    server.wait()
    client.kill()

    print('experiment finish!')
    # Popen("kill -9 $(ps -aux | grep Motor | awk '{print $2}')", shell=True)

    return


if __name__ == '__main__':

    config_loader = configLoader()

    host_name = socket.gethostname()
    redis_result_key = ':'.join(["motor",host_name,"result"])

    BATCH_TEST = True

    if(BATCH_TEST):
        record_file = "./results/dataset_03.csv"
        redis_addr = config_loader.get_redis_address()
        redis_client = redis.StrictRedis(host=redis_addr[0], port=redis_addr[1], db=0, decode_responses=True)

        headers = ["delay_mean", "loss_mean", "control_interval", "result"]
        if(not os.path.exists(record_file)):
            with open(record_file,"a+") as f:
                writer = csv.writer(f)
                writer.writerow(headers)

        # 批量实验参数
        delay_mean_set = [10,20,30,40,50]
        loss_mean_set = [0.1,0.2,0.3,0.4,0.5]
        control_interval_set = [10]
        epoch = 2
        
        count = 0
        for delay_mean in delay_mean_set:
            for loss_mean in loss_mean_set:
                for control_interval in control_interval_set:
                    print(f"\n===> experimrnt {count} | delay_mean: {delay_mean}ms | loss_mean: {loss_mean} | control_interval: {control_interval}ms")
                    for i in range(epoch):
                        print(f"\n=> epoch {i}")
                        run_experiment(delay_mean, loss_mean, control_interval)
                        result = float(redis_client.get(redis_result_key))
                        fields = [delay_mean, loss_mean, control_interval, result]
                        with open(record_file,"a+") as f:
                            writer = csv.writer(f)
                            writer.writerow(fields)
                    count += 1
    else:
        delay_mean = 50
        loss_mean = 0.1
        control_interval = 10
        run_experiment(delay_mean, loss_mean, control_interval)
                    


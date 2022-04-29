from subprocess import Popen
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


def run_experiment(base_delay, use_trace, trace_file, control_interval):
    """
    run experiment function
    """

    # kill existing programs
    print("starting ...")
    # Popen("kill -9 $(ps -aux | grep mm-delay | awk '{print $2}')", shell=True)
    Popen("sh ./kill.sh", shell=True)
    time.sleep(2)

    server_comds = 'python3 motorServer.py'
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
    base_delay = config_loader.get_base_delay()
    control_interval = config_loader.get_control_interval()
    use_trace = config_loader.get_use_trace()
    trace_file = config_loader.get_trace_path()

    host_name = socket.gethostname()
    redis_result_key = ':'.join(["motor",host_name,"result"])

    BATCH_TEST = False

    if(BATCH_TEST):
        record_file = "./results/dataset_03.csv"
        redis_addr = config_loader.get_redis_address()
        redis_client = redis.StrictRedis(host=redis_addr[0], port=redis_addr[1], db=0, decode_responses=True)

        results = []

        headers = ["base_delay", "base_loss", "control_interval", "result"]
        if(not os.path.exists(record_file)):
            with open(record_file,"a+") as f:
                writer = csv.writer(f)
                writer.writerow(headers)
        
        pause_flag = False
        if(redis_client.exists("base_delay")):
            base_delay_start = int(redis_client.get("base_delay"))
            control_interval_start = int(redis_client.get("control_interval"))
            print(f">>>> {base_delay_start} - {control_interval_start}")
            pause_flag = True
        else:
            base_delay_start = 1
            control_interval_start = 1
        

        # base_delay_set = list(range(1,51))
        # control_interval_set = list(range(1,21))
        
        base_delay_set = [10,20,30,40,50]
        control_interval_set = [1,10]
        epoch = 10
        
        base_loss = 0

        for base_delay in base_delay_set:
            redis_client.set("base_delay",base_delay)
            for control_interval in control_interval_set:
                redis_client.set("control_interval",control_interval)
                print(f"base_delay: {base_delay}ms and control_interval: {control_interval}ms")
                for i in range(epoch):
                    run_experiment(base_delay, use_trace, trace_file, control_interval)
                    result = float(redis_client.get(redis_result_key))
                    fields = [base_delay, base_loss, control_interval, result]
                    with open(record_file,"a+") as f:
                        writer = csv.writer(f)
                        writer.writerow(fields)
                    if(pause_flag):
                        control_interval_start = 1
    else:
        run_experiment(base_delay, use_trace, trace_file, control_interval)
                    


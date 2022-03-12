from subprocess import Popen
import time
import socket
import numpy as np
import tempfile
import os
from configs.configLoader import configLoader
import pandas as pd


def run_experiment():
    """
    run experiment function
    """
    config_loader = configLoader()
    # kill existing monax programs
    print("starting ...")
    # Popen("kill -9 $(ps -aux | grep Motor | awk '{print $2}')", shell=True)
    time.sleep(2)

    server_comds = 'python3 motorServer.py'
    client_comds = 'python3 motorClient.py --id 001 --target_speed 3000'

    base_delay = config_loader.get_base_delay()
    use_trace = config_loader.get_use_trace()
    trace_file = config_loader.get_trace_path()

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
    print(start_server)
    print(start_client)

    client = Popen(start_client, shell=True)
    time.sleep(3)
    server = Popen(start_server, shell=True)

    print("experiment start success")

    server.wait()
    client.kill()

    print('experiment finish!')
    Popen("kill -9 $(ps -aux | grep Motor | awk '{print $2}')", shell=True)

    return


if __name__ == '__main__':

    results = []

    EPOCH = 1
    for i in range(EPOCH):
        print(f"epoch: {i}")
        run_experiment()

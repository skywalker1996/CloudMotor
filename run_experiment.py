from subprocess import Popen
import time
import socket

import numpy as np
import tempfile
# import pandas as pd
import os
from configs.configLoader import ConfigLoader

def run_experiment():

    config_loader = ConfigLoader()
    ### kill existing monax programs
    print("starting ...")
    Popen("kill -9 $(ps -aux | grep Motor | awk '{print $2}')", shell=True)
    time.sleep(2)


    server_comds = 'python3 motorServer.py'
    client_comds = 'python3 MotorClient.py'

    base_delay = config_loader.get_base_delay()
    use_trace = config_loader.get_use_trace()
    trace_file = config_loader.get_trace_path()

    if use_trace:
        ### start monax client and serve
        start_server = ['mm-delay', str(base_delay),
                        'mm-link', trace_file, trace_file,
                        '--uplink-queue=droptail --uplink-queue-args=packets=2048',
                        '-- sh -c ', server_comds]

        start_server = ' '.join(start_server)
    else:
        start_server = server_comds

    start_client = client_comds
    # 	client = Popen(start_client, stdout=fileno, stderr=fileno, shell=True)
    # 	server = Popen(start_server, stdout=fileno, stderr=fileno, shell=True)
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


    #### compute avg results

    # dataframe = pd.DataFrame({'RTT_average': [r['RTT_average'] for r in results],
    #                           'queue_delay_average': [r['queue_delay_average'] for r in results],
    #                           'end2end_average': [r['end2end_average'] for r in results],
    #                           'send_rate_average': [r['send_rate_average'] for r in results],
    #                           'delivery_rate_average': [r['delivery_rate_average'] for r in results]})
    #
    # file_path = "./results/data/pcc-allegro.csv"
    # dataframe.to_csv(file_path, sep=',', mode='w+')
    # print("========= Experiment finish ==========")

# 	print('============ Results ============')
# 	print('***** 平均RTT = {} ms'.format(round(RTT_average,4)))
# 	print('***** 平均排队时延 = {} ms'.format(round(queue_delay_average,4)))
# 	print('***** 平均端到端时延 = {} ms'.format(round(end2end_average,4)))
# 	print('***** 平均 send rate = {} Mbps'.format(round(send_rate_average,4)))
# 	print('***** 平均 delivery rate = {} Mbps'.format(round(delivery_rate_average,4)))

# 	print('***** 平均带宽 = {} Mbps'.format(round(bw_average,4)))





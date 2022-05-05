import pandas
import os 
import math
import csv

def sla_comp(omega_err_seq, target_omega):

    sorted_seq = sorted(omega_err_seq)
    total_count = len(sorted_seq)
    results = []

    for p in range(90,100):
        index = int(total_count * (p/100.0))
        omega_err_abs = sorted_seq[index]
        err_rate = omega_err_abs / target_omega
        precision = 100-err_rate*100
        results.append(precision)

    return results

records_dir = "../logs/001"
file_list = os.listdir(records_dir)
file_list = sorted(file_list)

result_file = "./datasets/test_01.csv"

TIME_START = 1
TIME_END = 120

TARGET_SPEED = 3000
TARGET_OMEGA = round((TARGET_SPEED * 2 * math.pi) / 60, 2)
CONTROL_INTERVAL = 10

headers = ["delay_mean", "loss_mean", "control_interval"]
headers.extend([f"sla({i}%)" for i in range(90,100)])
headers.append("avg_precision")
if(not os.path.exists(result_file)):
    with open(result_file,"a+") as f:
        writer = csv.writer(f)
        writer.writerow(headers)


for file in file_list:
    if(file[-3:] != "csv"):
        continue
    buf = file.split('_')
    delay_mean = float(buf[0])
    loss_mean = float(buf[1])
    # print(f"delay_mean:{delay_mean} | loss_mean:{loss_mean}")
    
    df = pandas.read_csv(os.path.join(records_dir, file))
    selected_data = df.loc[(df['time'] >= TIME_START) & (df['time'] <= TIME_END)]
    omega_errs = selected_data["omega_errs"]
    
    sla_res = sla_comp(omega_errs, TARGET_OMEGA)
    
    err_sum = 0.0
    count = 0
    for omega_err in omega_errs:
        err_sum += omega_err / TARGET_OMEGA
        count += 1
    avg_err = round(err_sum / count, 4)
    avg_precision = 100-avg_err*100
    
    results = []
    results.extend(sla_res)
    results.append(avg_precision)
    
    fields = [delay_mean, loss_mean, CONTROL_INTERVAL]
    fields.extend(results)

    with open(result_file,"a+") as f:
        writer = csv.writer(f)
        writer.writerow(fields)
        
print("analysis finished!")


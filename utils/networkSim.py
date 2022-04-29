import os
import sys

sys.path.append(os.path.abspath(os.path.dirname(__file__)))
import numpy as np
import matplotlib.pyplot as plt
import time
from gilbert.gilbert_elliott import GilbertElliott


class NetworkSim:
    """
    NetworkSim
    """
    def __init__(self, delay_mean, loss_mean, update_freq):

        shape = 5
        scale = delay_mean/shape
        self.delay_seq = np.random.gamma(shape,scale,10000)

        p = 0.5
        r = 0.5
        k = 0.99
        h = 2-k-2*loss_mean
        self.loss_model = GilbertElliott([p,r,h,k])

        self.delay_seq = [round(abs(delay),2) for delay in self.delay_seq]
        self.delay_max = 1000
        self.delay_index = -1
        self.update_freq = update_freq
        self.delay_start_time = time.time()*1000

    def get_next_delay(self):
        
        if time.time()*1000 - self.delay_start_time > self.update_freq:
            if self.delay_index < len(self.delay_seq)-1:
                self.delay_index += 1
            else:
                self.delay_index = 0
            self.delay_start_time = time.time()*1000

        return min(self.delay_seq[self.delay_index], self.delay_max)

    def packet_loss(self):
        return int(self.loss_model.packet_loss())

    def plot_delay(self):
        plt.figure(figsize=(8,6)) 
        plt.xlabel("Delay (ms)")   
        plt.ylabel("Prob")    
        plt.title("Example")   
        res = plt.hist(self.delay_seq, 50, density=1, stacked=True)
        plt.plot(res[1][:-1], res[0], linewidth=3)
        # plt.plot(list(range(len(self.delay_seq))), self.delay_seq)  
        plt.savefig("./analysis/network/delay_seq.jpg")

    
if __name__ == '__main__':

    networkSim = NetworkSim(50,0.09, 10)
    loss_record = []
    for i in range(10000):
        packet_loss = networkSim.packet_loss()
        # print(packet_loss)
        loss_record.append(packet_loss)
    
    print(sum(loss_record)/len(loss_record))

    
    
    

    

    






        
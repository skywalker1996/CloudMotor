import numpy as np
import matplotlib.pyplot as plt


class NetworkSim:
    """
    NetworkSim
    """
    def __init__(self, delay_mean, delay_var, loss_mean, loss_var):
        self.delay_seq = np.random.normal(0, delay_var, 10000) + delay_mean
        self.loss_seq = np.random.normal(0, loss_var, 10000) + loss_mean

        self.delay_seq = [round(abs(delay),2) for delay in self.delay_seq]
        self.loss_seq = [round(abs(loss), 4) for loss in self.loss_seq]

        self.delay_max = 50
        self.loss_max = 0.05

        self.delay_index = -1
        self.loss_index = -1

    def get_next_delay(self):

        if self.delay_index < len(self.delay_seq)-1:
            self.delay_index += 1
        else:
            self.delay_index = 0

        return min(self.delay_seq[self.delay_index], self.delay_max)

    def get_next_loss(self):
        
        if self.loss_index < len(self.loss_seq)-1:
            self.loss_index += 1
        else:
            self.loss_index = 0
        
        return min(self.loss_seq[self.loss_index], self.loss_max)

    def plot_delay(self):
        plt.figure(figsize=(8,6)) 
        plt.xlabel("Delay (ms)")   
        plt.ylabel("Prob")    
        plt.title("Example")   
        res = plt.hist(self.delay_seq, 50, density=1, stacked=True)
        plt.plot(res[1][:-1], res[0], linewidth=3)
        # plt.plot(list(range(len(self.delay_seq))), self.delay_seq)  
        plt.savefig("./analysis/network/delay_seq.jpg")

    def plot_loss(self):
        plt.figure(figsize=(8,6)) 
        plt.xlabel("Loss")   
        plt.ylabel("Prob")    
        plt.title("Example")   
        res = plt.hist(self.loss_seq, 50, density=1, stacked=True)
        plt.plot(res[1][:-1], res[0], linewidth=3)
        # plt.plot(list(range(len(self.delay_seq))), self.delay_seq)  
        plt.savefig("./analysis/network/loss_seq.jpg")

    


if __name__ == '__main__':

    networkSim = NetworkSim(10,10,0.01,0.01)
    networkSim.plot_delay()
    networkSim.plot_loss()
    
    
    

    

    






        
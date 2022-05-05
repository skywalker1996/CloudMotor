import yaml
import os
import sys

path = os.path.dirname(os.path.abspath(__file__))

class configLoader:

    def __init__(self):
        self.global_config = yaml.load(open(path+'/global.yaml'), Loader=yaml.FullLoader)

        self.address_config_file = self.global_config["address_config"]

        self.address_config = yaml.load(open(path+'/'+self.address_config_file), Loader=yaml.FullLoader)

    def get_server_address(self):
        address = self.address_config["server"]["address"]
        if(self.global_config["experiment"]["use_mahimahi"]):
            return address["ip"], address["port"]
        else:
            return address["local_ip"], address["port"]

    def get_client_address(self):
        address = self.address_config["client"]["address"]
        if (self.global_config["experiment"]["use_mahimahi"]):
            return address["ip"], address["port"]
        else:
            return address["local_ip"], address["port"]


    def get_register_address(self):
        address = self.address_config["register"]["address"]
        return address["ip"], address["port"]

    def get_client_ip(self):
        ip, port = self.get_client_address()
        return ip

    def get_trace_path(self):
        return self.global_config["mahimahi"]["trace"]

    def get_base_delay(self):
        return self.global_config["mahimahi"]["base_delay"]

    def get_use_mahimahi(self):
        return self.global_config["experiment"]["use_mahimahi"]

    def get_control_interval(self):
        return self.global_config["experiment"]["control_interval"]

    def get_running_time(self):
        return self.global_config["experiment"]["running_time"]

    def get_batch_experiment(self):
        return self.global_config["experiment"]["batch_experiment"]

    def get_redis_address(self):
        address = self.address_config["redis"]["address"]
        return address["ip"], address["port"]

    def get_delay_mean_set(self):
        delay_range = self.global_config["batch_experiment_params"]["delay_mean"]
        delay_mean_set = list(range(delay_range[0], delay_range[1]+1, delay_range[2]))
        return delay_mean_set

    def get_loss_mean_set(self):
        loss_range = self.global_config["batch_experiment_params"]["loss_mean"]
        loss_mean_set = [i/100.0 for i in list(range(loss_range[0],loss_range[1]+1,loss_range[2]))]
        return loss_mean_set

    def get_control_interval_set(self):
        interval_range = self.global_config["batch_experiment_params"]["control_interval"]
        control_interval_set = list(range(interval_range[0], interval_range[1]+1, interval_range[2]))
        return control_interval_set
    
    def get_epoch(self):
        return self.global_config["batch_experiment_params"]["epoch"]

    def get_experiment_name(self):
        return self.global_config["experiment"]["name"]



if __name__ == "__main__":

    config_loader = configLoader()
    # print(config_loader.get_server_address())
    # print(config_loader.get_use_trace())
    print(config_loader.global_config["experiment"]["use_mahimahi"])






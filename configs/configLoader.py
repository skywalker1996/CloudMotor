import yaml
import os
import sys

path = os.path.dirname(os.path.abspath(__file__))

class configLoader:

    def __init__(self):
        self.global_config = yaml.load(open(path+'/global.yaml'), Loader=yaml.FullLoader)

        self.config_file = self.global_config["configs"]

        self.configs = yaml.load(open(path+'/'+self.config_file), Loader=yaml.FullLoader)

    def get_server_address(self):
        address = self.configs["server"]["address"]
        return address["ip"], address["port"]

    def get_client_address(self):
        address = self.configs["client"]["address"]
        return address["ip"], address["port"]

    def get_register_address(self):
        address = self.configs["register"]["address"]
        return address["ip"], address["port"]

    def get_client_ip(self):
        return self.configs["client"]["address"]["ip"]

    def get_trace_path(self):
        return self.global_config["experiment"]["trace"]

    def get_base_delay(self):
        return self.global_config["experiment"]["base_delay"]

    def get_use_trace(self):
        return True if self.global_config["experiment"]["use_trace"]==1 else False

    def get_control_interval(self):
        return self.global_config["experiment"]["control_interval"]

    def get_running_time(self):
        return self.global_config["experiment"]["running_time"]


if __name__ == "__main__":

    config_loader = configLoader()
    print(config_loader.get_server_address())
    print(config_loader.get_use_trace())







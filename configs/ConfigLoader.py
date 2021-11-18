import yaml
import os
import sys

path = os.path.dirname(os.path.abspath(__file__))

class ConfigLoader:

    def __init__(self):
        self.global_config = yaml.load(open(path+'/global.yaml'), Loader=yaml.FullLoader)

    def get_server_address(self):
        address = self.global_config["server"]["address"]
        return address["ip"], address["port"]

    def get_client_address(self):
        address = self.global_config["client"]["address"]
        return address["ip"], address["port"]

    def get_register_address(self):
        address = self.global_config["register"]["address"]
        return address["ip"], address["port"]

    def get_client_ip(self):
        return self.global_config["client"]["address"]["ip"]




if __name__ == "__main__":

    config_loader = ConfigLoader()
    print(config_loader.get_server_address())







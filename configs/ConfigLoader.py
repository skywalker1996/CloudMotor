import yaml
import os
import sys

path = os.path.dirname(os.path.abspath(__file__))

class ConfigLoader:

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




if __name__ == "__main__":

    config_loader = ConfigLoader()
    print(config_loader.get_server_address())







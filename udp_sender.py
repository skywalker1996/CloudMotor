import socket
import json

register_data = {"type": "register", "client_id": "001", "address": ("192.168.31.165", 8888),
                 "target_rpm": 4000}
pkt = json.dumps(register_data)

client_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
client_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
client_sock.bind(("192.168.31.165", 8888))

client_sock.sendto(pkt.encode(), ("192.168.31.165", 9991))


import socket

server_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_sock.bind(("192.168.31.165", 9991))

data = server_sock.recv(500)
print(data)

import socket
from response_controller import ResponseController





if __name__ == "__main__":

    port = 53
    ip = '127.0.0.1'

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((ip, port))

    print('Работаем')
    while True:
        data, addr = sock.recvfrom(512)
        response = ResponseController.make_response(data)
        sock.sendto(response, addr)

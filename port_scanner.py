import argparse
import re
import socket
from threading import Thread, Lock
from queue import Queue

N_THREADS = 50
q = Queue()
print_lock = Lock()


def convert_to_ip(host):
    regex = re.search(r"^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$", host)
    if not regex is None and regex.group(0) == host:
        return host
    else:
        return socket.gethostbyname(host)


def port_scan(host, port):
    try:
        sock = socket.socket()
        sock.settimeout(0.2)
        sock.connect((host, port))
    except:
        pass
    else:
        with print_lock:
            print(f"{host:15}:{port:5} is open")
    finally:
        sock.close()


def scan_thread(host):
    global q
    while True:
        worker = q.get()
        port_scan(host, worker)
        q.task_done()


def main(host, left, right):
    global q
    for thread in range(N_THREADS):
        thread = Thread(target=scan_thread, args=[host])
        thread.daemon = True
        thread.start()
    for worker in range(left, right + 1):
        q.put(worker)
    q.join()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Port scanner")
    parser.add_argument("host", help="Host to scan.")
    parser.add_argument("left", help="left ports limit")
    parser.add_argument("right", help="left ports limit")
    args = parser.parse_args()
    usr_host, left, right = convert_to_ip(args.host), int(args.left), int(args.right)
    main(usr_host, left, right)

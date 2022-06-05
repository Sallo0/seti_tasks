
def make_ipv4_from_bytes(data):
    ip = ''
    for byte in data:
        ip += str(byte) + '.'
    return ip.rstrip('.')

def dns_flags_to_bytes(*args):
    string = ''
    for arg in args:
        string += arg
    return int(string, 2).to_bytes(1, byteorder='big')


def build_dns_question(domain, qtype):
    question = b''

    for part in domain:
        length = len(part)
        question += bytes([length])

        for char in part:
            question += ord(char).to_bytes(1, byteorder='big')

    if qtype == 'a':
        question += (1).to_bytes(2, byteorder='big')
    if qtype == 'ns':
        question += (2).to_bytes(2, byteorder='big')

    question += (1).to_bytes(2, byteorder='big')  # класс интернет
    return question

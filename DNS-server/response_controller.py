from msg_controller import MSGController
from server_request_controller import ServerRequestController
import tools


class ResponseController:

    @staticmethod
    def record_to_bytes(rec_type, ttl, value):
        record = b'\xc0\x0c'

        if rec_type == 'a':
            record += bytes([0]) + bytes([1])
        if rec_type == 'ns':
            record += bytes([0]) + bytes([2])

        record += bytes([0]) + bytes([1])  # класс интернет
        record += int(ttl).to_bytes(4, byteorder='big')

        if rec_type == 'a':
            record += bytes([0]) + bytes([4])

            for part in value.split('.'):
                record += bytes([int(part)])
        if rec_type == 'ns':
            byte_value = bytes(bytearray.fromhex(value))
            record += bytes([0]) + bytes([len(byte_value)])
            record += byte_value
        return record

    @staticmethod
    def build_response_flags(flags):
        first_byte = flags[:1]
        var = flags[1:2]
        QR = '1'
        OPCODE = ''
        for bit in range(1, 5):
            OPCODE += str(ord(first_byte) & (1 << bit))

        AA = '1'
        TC = '0'
        RD = '1'
        RA = '1'
        Z = '000'
        RCODE = '0000'
        first_byte_str = QR + OPCODE + AA + TC + RD
        second_byte_str = RA + Z + RCODE

        return tools.dns_flags_to_bytes(first_byte_str) + tools.dns_flags_to_bytes(second_byte_str)

    @staticmethod
    def build_response(data):
        ID = data[0:2]
        FLAGS = ResponseController.build_response_flags(data[2:4])
        QDCOUNT = b'\x00\x01'
        records_data = ServerRequestController.get_domain_records(data[12:])
        ANCOUNT = len(records_data[0]).to_bytes(2, byteorder='big')
        NSCOUNT = (0).to_bytes(2, byteorder='big')
        ARSCOUNT = (0).to_bytes(2, byteorder='big')
        header = ID + FLAGS + QDCOUNT + ANCOUNT + NSCOUNT + ARSCOUNT
        body = b''
        records, rec_type, domain = records_data
        question = tools.build_dns_question(domain, rec_type)
        for record in records:
            body += ResponseController.record_to_bytes(rec_type, record['ttl'], record['value'])
        print(f'Ответ на запрос типа "{rec_type}" по "{".".join(domain)}" отправлен.')
        return header + question + body

    @staticmethod
    def make_response(data):
        request_info = MSGController.parse_incoming_request(data)
        resp = b''
        req_type = request_info['question']['QTYPE']
        if req_type == 'a' or req_type == 'ns':
            print(f'Получен запрос типа "{req_type}". Разрешаю запрос...')
            resp = ResponseController.build_response(data)

        return resp

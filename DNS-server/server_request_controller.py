import datetime
import socket
from storage_controller import StorageController
from msg_controller import MSGController
import tools

CACHE = StorageController.load_cache()
GOOGLE_NS = '8.8.8.8', 53


class ServerRequestController:

    @staticmethod
    def get_domain_records(data):
        domain, question_type = MSGController.get_user_request(data)
        QT = ''
        if question_type == b'\x00\x01':
            QT = 'a'
        if question_type == (12).to_bytes(2, byteorder='big'):
            QT = 'ptr'
        if question_type == (2).to_bytes(2, byteorder='big'):
            QT = 'ns'

        recs = None
        if QT == 'a' or QT == 'ns':
            info = ServerRequestController.get_domain_data(domain, CACHE, QT)
            recs = info['data'][QT]

        return recs, QT, domain

    @staticmethod
    def get_domain_data(domain, cache, qtype):
        domain_name = '.'.join(domain)
        if domain_name in cache:
            print(f'Данные {domain_name} найдены в кэше.')
            domain_cache = cache[domain_name]
            if qtype in domain_cache['data']:
                time = datetime.datetime.fromisoformat(domain_cache['time'])
                ttl = domain_cache['ttl']
                current_time = datetime.datetime.now()
                if (current_time - time).seconds > ttl:
                    print(f'Данные "{domain_name}" устарели. Обращаюсь к старшему ДНС серверу.')
                    return ServerRequestController.request_new_data(domain, qtype)
            else:
                print(f'Данные по "{qtype}" запросу не найдены. Обращаюсь к старшему ДНС серверу.')
                return ServerRequestController.request_new_data(domain, qtype)
        else:
            print(f'В кэше нет данных по "{domain_name}". Обращаюсь к старшему ДНС серверу.')
            return ServerRequestController.request_new_data(domain, qtype)
        return domain_cache

    @staticmethod
    def request_new_data(domain, qtype):
        request = ServerRequestController.build_request(domain, qtype)
        temp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            temp_sock.sendto(request, GOOGLE_NS)
            data, _ = temp_sock.recvfrom(512)
        finally:
            temp_sock.close()
        return ServerRequestController.info_from_dns_response(data, domain, qtype)

    @staticmethod
    def build_request(domain, qtype):
        ID = b'\xAA\xAA'
        FLAGS = b'\x01\x00'
        QDCOUNT = b'\x00\x01'
        ANCOUNT = (0).to_bytes(2, byteorder='big')
        NSCOUNT = (0).to_bytes(2, byteorder='big')
        ARSCOUNT = (0).to_bytes(2, byteorder='big')
        header = ID + FLAGS + QDCOUNT + ANCOUNT + NSCOUNT + ARSCOUNT
        question = tools.build_dns_question(domain, qtype)
        return header + question

    @staticmethod
    def info_from_dns_response(data, domain, qtype):
        question = tools.build_dns_question(domain, qtype)
        ANCOUNT = int.from_bytes(data[6:8], 'big')
        answer = data[12 + len(question):]
        records = ServerRequestController.get_records_from_answer(answer, ANCOUNT)
        origin = '.'.join(domain)
        time = str(datetime.datetime.now())
        new_cache_entry = {'origin': origin, 'time': time, 'data': records, 'ttl': 360}
        CACHE[origin] = new_cache_entry
        StorageController.save_info_data(new_cache_entry)
        return new_cache_entry

    @staticmethod
    def get_records_from_answer(answer, count):
        ptr = 0
        records = {}
        for _ in range(count):
            record = {}
            rec_type = int.from_bytes(answer[ptr + 2: ptr + 4], 'big')
            ttl = int.from_bytes(answer[ptr + 6:ptr + 10], 'big')
            rd_length = int.from_bytes(answer[ptr + 10: ptr + 12], 'big')
            rd_data = ''
            if rec_type == 1:
                rd_data = tools.make_ipv4_from_bytes(answer[ptr + 12:ptr + 12 + rd_length])
            if rec_type == 2:
                rd_data = answer[ptr + 12:ptr + 12 + rd_length].hex()
            ptr += 12 + rd_length
            rec_type = MSGController.make_type_from_number(rec_type)
            record['ttl'] = ttl
            record['value'] = rd_data
            if rec_type in records:
                records[rec_type].append(record)
            else:
                records[rec_type] = [record]
        return records



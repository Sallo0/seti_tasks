import glob
import json


class StorageController:

    @staticmethod
    def load_cache():
        json_info = {}
        info_files = glob.glob('infos/*.info')
        print('Загрузка кэша.')

        for zone in info_files:
            with open(zone) as file:
                data = json.load(file)
                origin = data['origin']
                json_info[origin] = data
        print(f'Загрузка из кэша завершена. Загружено {len(json_info)} объектов.')
        return json_info

    @staticmethod
    def save_info_data(data):
        with open(f'infos/{data["origin"]}.info', 'w+') as file:
            json.dump(data, file)

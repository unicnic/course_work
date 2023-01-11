import requests
import json
import time
from progress.bar import IncrementalBar
from datetime import datetime
#from settings import TOKEN
#from settings import TOKEN_YA


class YaUploader:
    host = 'https://cloud-api.yandex.net'
    def __init__(self, token: str):
        self.token = token

    def get_headers(self):
        return {
            'Content-Type': 'application/json',
            'Authorization': f'OAuth {self.token}'
        }

    def create_folder(self, user_id):
        uri = '/v1/disk/resources/'
        url = self.host + uri
        params = {'path': f'VK_id_{user_id}'}
        requests.put(url, headers=self.get_headers(), params=params)

    def upload_photos(self, photos_dict, user_id):
        uri = '/v1/disk/resources/upload/'
        url = self.host + uri
        for file_name, href_size in photos_dict.items():
            params = {'path': f'VK_id_{user_id}/{file_name}.jpg', 'url' : f'{href_size[0]}'}
            requests.post(url, headers=self.get_headers(), params=params)
            self.loging(user_id, file_name, href_size[1])
            self.pragress_bar()

    def loging(self, user_id, file_name, size):
        data = {
            "file_name": f"{file_name}.jpg",
            "size": size
        }
        with open(f"log_{user_id}.json", 'a', encoding='utf8') as f:
            json.dump(data, f, indent=4)

    def pragress_bar(self):
        bar.next()
        time.sleep(1)

if __name__ == '__main__':
    photos_dict = {}
    size_dict = {'s': 1, 'm': 2, 'o': 3, 'p': 4, 'q': 5, 'r': 6, 'x': 7, 'y': 8, 'z': 9, 'w': 10}
    user_id = input('Введите id пользователя vk: ')
    TOKEN_YA = input('Введите token Полигона Яндекс.Диска: ')
    uploader = YaUploader(TOKEN_YA)
    uploader.create_folder(user_id)
    url = 'https://api.vk.com/method/photos.getAll'
    params = {
        'owner_id' : user_id,
        'access_token' : TOKEN,
        'v' : '5.131',
        'count' : 5,
        'extended' : '1',
        'photo_sizes' : '1'
    }
    bar = IncrementalBar('Countdown', max=params['count'])
    response = requests.get(url, params=params)
    photos_json = response.json()
    for items in photos_json['response']['items']:
        if items['likes']['count'] not in photos_dict.keys():
            file_url = max(items['sizes'], key = lambda x: size_dict[x["type"]])
            photos_dict[items['likes']['count']] = [file_url['url'], file_url['type']]
        else:
            photos_dict[f"{items['likes']['count']}_{datetime.fromtimestamp(items['date']).date()}"] = [file_url['url'], file_url['type']]
    uploader.upload_photos(photos_dict, user_id)
    bar.finish()

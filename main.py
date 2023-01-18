import requests
import json
import time
from progress.bar import IncrementalBar
from datetime import datetime
from settings import TOKEN


class YaUploader:
    host = 'https://cloud-api.yandex.net'
    def __init__(self, token:str):
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


class VKLoad:
    host = 'https://api.vk.com/method/'

    def __init__(self, token:str):
        self.token = token
        self.params = {
            'access_token' : token,
            'v' : '5.131',
        }

    def get_all_foto_dict(self, user_id, count_img=5):
        url = self.host + 'photos.getAll'
        self.params['owner_id'] = user_id
        self.params['count'] = count_img
        self.params['extended'] = '1'
        self.params['photo_sizes'] = '1'
        response = requests.get(url, params=self.params)

        return response.json()

    def find_max_img(self, photos_json):
        photos_dict = {}
        size_dict = {'s': 1, 'm': 2, 'o': 3, 'p': 4, 'q': 5, 'r': 6, 'x': 7, 'y': 8, 'z': 9, 'w': 10}
        for items in photos_json['response']['items']:
            if items['likes']['count'] not in photos_dict.keys():
                file_url = max(items['sizes'], key=lambda x: size_dict[x["type"]])
                photos_dict[items['likes']['count']] = [file_url['url'], file_url['type']]
            else:
                photos_dict[f"{items['likes']['count']}_{datetime.fromtimestamp(items['date']).date()}"] = [
                    file_url['url'], file_url['type']]

        return photos_dict

    def get_user_id(self, screen_name):
        url = self.host + 'utils.resolveScreenName'
        self.params['screen_name'] = screen_name
        response = requests.get(url, params=self.params)

        return response.json()['response']['object_id']


def input_data():
    user = input('Введите пользователя vk (id или screen_name): ')
    try:
        user_id = int(user)
    except ValueError:
        user_id = vk_loader.get_user_id(user)

    count_img = input('Введите количество фото для скачивания (5 по умолчанию): ')
    try:
        count_img = int(count_img)
    except ValueError:
        count_img = 5

    TOKEN_YA = input('Введите token Полигона Яндекс.Диска: ')

    return [user, user_id, count_img, TOKEN_YA]


if __name__ == '__main__':
    vk_loader = VKLoad(TOKEN)
    data = input_data()
    uploader = YaUploader(data[3])
    uploader.create_folder(data[0])
    bar = IncrementalBar('Countdown', max=data[2])
    uploader.upload_photos(vk_loader.find_max_img(vk_loader.get_all_foto_dict(data[1], data[2])), data[0])
    bar.finish()

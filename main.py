import requests
import time
from tqdm import tqdm
from config import VK_TOKEN, YA_TOKEN


class VKAPIPhotoClient:
    """
    Класс VKAPIPhotoClient
    поля класса:
    константа API_BASE_URL - адрес API VK
    access_token - токен API
    access_token - актуальная версия API
    id - id пользователя
    :params - параметры, передаваемые URL
    """
    API_BASE_URL = 'https://api.vk.com/method'

    def __init__(self, access_token: str, id: str, version='5.199') -> None:
        self.access_token = access_token
        self.version = version
        self.id = id
        self.params = {
            'access_token': self.access_token,
            'v': self.version
        }

    def get_photos(self, count='5') -> list:
        """
        Метод класса получает фото из ВК указанного id пользователя
        Имя файла определеяется количеством лайков,
        если количество одинковое, вместо лайка подставляется дата
        :param - параметры, передаваемые URL (id-пользователя,
                                              album_id - из кого альбома брать фото
                                              extended - количество лайков
                                              count - количнство скачиваемых фото
        :return: список из словарей 'name': имя файла, 'link': ссылка на файл
        """
        params = {**self.params}
        params.update({
            'user_id': self.id,
            'album_id': 'profile',
            'extended': 'likes',
            'count': count
        })
        list_links = []
        response = requests.get(f'{self.API_BASE_URL}/photos.get', params=params)
        for item in response.json()['response']['items']:
            dict_link = {}
            for photo in item['sizes']:
                if photo['type'] == 'z':
                    dict_link['date'] = item['date']
                    dict_link['likes'] = item['likes']['count']
                    dict_link['link'] = photo['url']
                    list_links.append(dict_link)

        print('Загрузка фото из вк')
        for photo in tqdm(list_links):
            time.sleep(1)
            current_file_name = photo['likes']
            file_name = 0
            if current_file_name == photo['likes'] and current_file_name != file_name:
                file_name = current_file_name
                photo['name'] = f'{file_name}.png'
                del (photo['likes'], photo['date'])
            else:
                current_file_name = photo['date']
                photo['name'] = f'{current_file_name}.png'
                del (photo['likes'], photo['date'])

        return list_links


class YADiskClient:
    """
    Класс YADiskClient
    Поля класса:
    token - токен API Yandex disc
    """
    def __init__(self, token):
        self.token = token

    def make_dir(self) -> None:
        """
        Метод класса создает на яндекс диске папку для хранения фото
        """
        DIR_URL = 'https://cloud-api.yandex.net/v1/disk/resources'
        self.headers = {
            'Authorization': self.token
        }

        self.params = {
            'path': '/Image'
        }

        response = requests.put(DIR_URL, params=self.params, headers=self.headers)

    def upload_photo(self, photots) -> None:
        """
        Метод класса получает список фотографий, состоящий из названий фалов и ссылок,
        загружает их на яндекс диск в ранее созданную папку
        """
        UPLOAR_URL = 'https://cloud-api.yandex.net/v1/disk/resources/upload'

        self.headers = {
            'Authorization': self.token
        }

        for photo in tqdm(photots):
            print('Запись фото на Яндекс-диск')
            time.sleep(1)
            params = {
                'path': f"/Image/{photo['name']}",
                'url': photo['link']
            }

            response = requests.post(UPLOAR_URL, params=params, headers=self.headers)


if __name__ == '__main__':

    vk_client = VKAPIPhotoClient(VK_TOKEN, 442679694)
    path_to_img = './Image'

    ya_client = YADiskClient(YA_TOKEN)
    ya_client.make_dir()
    ya_client.upload_photo(vk_client.get_photos())

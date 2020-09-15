import requests
import json
import random
import time
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

DOMAIN_URL = 'api.vk.com'
API_V = '5.103'


class VkConnector:

    def __init__(self, owner_id, group_number):
        config = json.loads(open('scripts/config.json', 'r').read())
        self.access_token = config['secrets']['api_vk_token']
        self.owner_id = owner_id,
        self.from_group = group_number
        self.domain_url = f'https://{DOMAIN_URL}/'
        self.version_api = API_V
        self.session = requests.Session()
        retries = Retry(total=10,
                        backoff_factor=0.5,
                        method_whitelist=['POST'],
                        status_forcelist=[422, 429, 500, 502, 503, 504])
        self.session.mount('https://', HTTPAdapter(max_retries=retries))

    def request(self, method, url, headers=None, files=None, params=None, data=None):
        response = self.session.request(method=method,
                                        url=url,
                                        params=params,
                                        headers=headers,
                                        files=files,
                                        data=data)
        return response

    def create_post(self, text=None, attachment=None):
        """
        :param text:
        :param attachment: - ID фотографии из альбома группы в формате GROUP-ID_PHOTO-ID
        """
        params = {
            'owner_id': self.owner_id,
            'from_group': self.from_group,
            'access_token': self.access_token,
            'v': self.version_api
        }
        if attachment is not None:
            params['attachments'] = attachment
        if text is not None:
            params['message'] = text

        self.request('POST', f'{self.domain_url}/method/wall.post', params=params)
        time.sleep(random.randrange(1, 15))

    def upload_images(self, list_images):
        """
        Загрузка изображений в группу вк. Состоит из трёх этапов:
        - Получение линка для загрузки
        - Сама загрузка в альбом группы
        - Сохранение результата после загрузки в альбом
        :param list_images: - названия изображений, которые будут загруженны в группу
        :return: - ID изображений в альбоме группы
        """
        upload_data = self.request('POST', f'{self.domain_url}/method/photos.getWallUploadServer',
                                        params={
                                            'owner_id': self.owner_id,
                                            'from_group': self.from_group,
                                            'access_token': self.access_token,
                                            'v': self.version_api
                                        }).json()
        upload_images = {'file' + str(index + 1): open(r'/home/ubuntu/vk_scripts/scripts/images/' + filename, 'rb')
                         for index, filename in enumerate(list_images) if index <= 5}
        upload_response = self.request('POST', upload_data['response']['upload_url'], files=upload_images).json()

        apply_upload = self.request('POST', f'{self.domain_url}/method/photos.save',
                                         data={
                                             'access_token': self.access_token,
                                             'v': self.version_api,
                                             'album_id': upload_data['response']['album_id'],
                                             'server': upload_response['server'],
                                             'hash': upload_response['hash'],
                                             'photos_list': upload_response['photo']
                                         }).json()
        return [f'photo{photo["owner_id"]}_{photo["id"]}' for photo in apply_upload['response']]

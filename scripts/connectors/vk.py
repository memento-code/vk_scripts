import requests
from requests.adapters import HTTPAdapter
from urllib3.util import Retry

DOMAIN_URL = 'api.vk.com'
API_V = '5.103'


class VkConnector:
    """Класс для подключения к API VK
    Args:
        owner_id(str) - Идентификатор пользователя или группы
        from_group(bool) - признак совершения действия от лица группы
        token(int) - токен для подключения к API VK

    Examples:
        >>> vk_connector = VkConnector(
            owner_id={owner_id},
            from_group=True,
            token={token}
        )
        >>> vk_connector.upload_images(['SF3r32ffD.png', 'CnOijfE29g.png'])
        >>> ['photo1234612_3215123123', 'photo6234236_245124123']
        >>> vk_connector.create_post(text="Text of post")
        >>> 200
    """

    def __init__(self, owner_id, from_group, token):
        self.access_token = token
        self.owner_id = owner_id,
        self.from_group = from_group
        self.base_url = f'https://{DOMAIN_URL}/'
        self.version_api = API_V

    @staticmethod
    def request(method, url, files=None, params=None, data=None):
        session = requests.Session()
        retries = Retry(total=10,
                        backoff_factor=0.5,
                        method_whitelist=['POST'],
                        status_forcelist=[422, 429, 500, 502, 503, 504])
        session.mount('https://', HTTPAdapter(max_retries=retries))

        return session.request(method=method,
                               url=url,
                               params=params,
                               files=files,
                               data=data)

    def create_post(self, text=None, attachment=None):
        """
        :param text: - Текст поста
        :param attachment: - ID фотографии из альбома группы в формате GROUP-ID_PHOTO-ID
        """
        if text is None and attachment is None:
            raise ValueError("Empty data for post")
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

        result = self.request('POST', f'{self.base_url}/method/wall.post', params=params)
        return result.status_code

    def upload_images(self, list_images):
        """
        Загрузка изображений в группу вк. Состоит из трёх этапов:
        - Получение линка для загрузки
        - Сама загрузка в альбом группы
        - Сохранение результата после загрузки в альбом
        :param list_images: - названия изображений, которые будут загруженны в группу
        :return: - ID изображений в альбоме группы
        """
        upload_data = self.request('POST', f'{self.base_url}/method/photos.getWallUploadServer',
                                   params={
                                       'owner_id': self.owner_id,
                                       'from_group': self.from_group,
                                       'access_token': self.access_token,
                                       'v': self.version_api
                                   }).json()
        upload_images = {'file' + str(index + 1): open(r'/home/ubuntu/vk_scripts/scripts/images/' + filename, 'rb')
                         for index, filename in enumerate(list_images) if index <= 5}
        upload_response = self.request('POST', upload_data['response']['upload_url'], files=upload_images).json()

        apply_upload = self.request('POST', f'{self.base_url}/method/photos.save',
                                    data={
                                        'access_token': self.access_token,
                                        'v': self.version_api,
                                        'album_id': upload_data['response']['album_id'],
                                        'server': upload_response['server'],
                                        'hash': upload_response['hash'],
                                        'photos_list': upload_response['photo']
                                    }).json()
        return [f'photo{photo["owner_id"]}_{photo["id"]}' for photo in apply_upload['response']]

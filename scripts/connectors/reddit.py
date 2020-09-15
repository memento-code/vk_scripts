import requests
import json
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

API_V = 'v1'
DOMAIN_URL = 'reddit.com'


class RedditConnector:

    def __init__(self, client_id):
        config = json.loads(open('scripts/config.json', 'r').read())
        self.reddit_secret = config['secrets']['reddit_secret']
        self.refresh_token = config['secrets']['reddit_refresh_token'],
        self.client_id = client_id,
        self.headers = {'Authorization': f'bearer {self.reddit_secret}',
                        "User-Agent": "ChangeMeClient/0.1 by ad_meliorem"}
        self.url = f'https://www.{DOMAIN_URL}/api/{API_V}'
        self.session = requests.Session()
        retries = Retry(total=10,
                        backoff_factor=0.5,
                        method_whitelist=['POST'],
                        status_forcelist=[422, 429, 500, 502, 503, 504])
        self.session.mount('https://', HTTPAdapter(max_retries=retries))
        self.session.auth = (self.client_id, self.reddit_secret)
        self.reddit_secret = self.get_reddit_token()

    def request(self, method, url, headers=None, files=None, params=None):
        response = self.session.request(method=method,
                                        url=url,
                                        params=params,
                                        headers=headers,
                                        files=files)
        return response

    def get_reddit_token(self):
        """
        :return: - временный токен для доступа к API Reddit
        """

        url_token = f'{self.url}/access_token'
        token = self.request('POST', url_token, params={
            'refresh_token': self.refresh_token,
            'grant_type': 'refresh_token'
        }).json()

        return token['access_token']

    def download_images_from_reddit(self, subreddit_id, count_images):
        """
        :param subreddit_id: - ID сабберида (https://www.reddit.com/r/{subreddit_id}/
        :param count_images: - кол-во изображений для скачивания
        :return: - список с названиями скаченных изображений
        """
        url_images = f'https://oauth.{DOMAIN_URL}/r/{subreddit_id}/hot'
        results = self.request('GET', url_images, headers=self.headers).json()
        count_download = 0
        filenames = []
        exist_images = os.listdir('/home/ubuntu/vk_scripts/scripts/images')

        for post in results['data']['children']:
            url_post = post['data']['url']
            if len(re.findall(r'(\.png)|(\.jpg)|(\.jpeg)|(\.gif)', url_post)) > 0:
                file = self.request('GET', url_post)
                filename = url_post.split('/')[len(url_post.split('/')) - 1]
                if filename in exist_images:
                    continue

                filenames.append(filename)
                open('/home/ubuntu/vk_scripts/images/' + filename, 'wb').write(file.content)
                count_download += 1
                if count_download >= count_images:
                    break

        return filenames

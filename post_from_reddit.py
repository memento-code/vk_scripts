import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
import re
import os
import random
import time
import json


def get_reddit_token(refresh_token):
    url = 'https://www.reddit.com/api/v1/access_token?grant_type=refresh_token&refresh_token=' + refresh_token
    session = requests.Session()
    retries = Retry(total=10,
                    backoff_factor=0.5,
                    method_whitelist=['POST'],
                    status_forcelist=[422, 429, 500, 502, 503, 504])
    session.mount('https://', HTTPAdapter(max_retries=retries))
    session.mount('http://', HTTPAdapter(max_retries=retries))
    session.auth = (CLIENT_ID, 'WvZO1sdBty3iTDxXZKCZEZs8ezw')
    token = session.post(url)
    token = token.json()

    return token['access_token']


def download_images_from_reddit(session, subreddit, count_images):
    URL_REDDIT = 'https://oauth.reddit.com/r/{}/hot'.format(subreddit)
    response = session.get(URL_REDDIT, headers=HEADERS)
    results = response.json()
    count_download = 0
    filenames = []

    for post in results['data']['children']:
        data_post = post['data']
        url_post = data_post['url']
        if len(re.findall(r'(\.png)|(\.jpg)|(\.jpeg)|(\.gif)', url_post)) > 0:
            file = session.get(url_post)
            filename = url_post.split('/')[len(url_post.split('/')) - 1]
            if filename in EXIST_IMAGES:
                continue

            filenames.append(filename)
            open('/home/ubuntu/vk_scripts/images/' + filename, 'wb').write(file.content)
            count_download += 1
            if count_download >= count_images:
                break
    return filenames


def upload_vk_photo(images):
    # Вк имеет отвратительную систему загрузки файлов, в которой нужно сначала получить урл для загрузки,
    # затем по этому урлу загрузить файл, дёрнуть ручку для сохранения и лишь потом можно прикрепить файл к посту
    url = 'https://api.vk.com/method/wall.post?access_token={token}&v=5.103&' \
          'owner_id=-188359976&' \
          'from_group=1&'.format(token=API_VK_TOKEN)
    retry = Retry(
        total=10,
        read=10,
        connect=10,
        backoff_factor=10,
        status_forcelist=(500, 501, 502, 503, 504, 505, 429),
    )
    session = requests.Session()
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('https://', adapter)
    session.post(url)

    url_get_uploader = 'https://api.vk.com/method/photos.getWallUploadServer?access_token={token}&' \
                       'owner_id=-188359976&v=5.103'.format(token=API_VK_TOKEN)
    result = session.post(url_get_uploader).json()

    url_upload = result['response']['upload_url']
    files = {'file' + str(index + 1): open(r'/home/ubuntu/vk_scripts/images/' + filename, 'rb')
             for index, filename in enumerate(images) if index <= 5}
    upload_response = requests.post(url_upload, files=files).json()
    url_upload = 'https://api.vk.com/method/photos.save?access_token={token}&v=5.103&' \
                 'album_id={album}&' \
                 'hash={hash}&' \
                 'server={server}&' \
                 'photos_list={photos_list}'.format(token=API_VK_TOKEN,
                                                    album=result['response']['album_id'],
                                                    server=upload_response['server'],
                                                    hash=upload_response['hash'],
                                                    photos_list=upload_response['photo'])
    upload_response = requests.post(url_upload).json()
    ids_images = ['photo{owner_id}_{media_id}'.format(owner_id=photo['owner_id'], media_id=photo['id'])
           for photo in upload_response['response']]

    for id_image in ids_images:
        url_post_wall = 'https://api.vk.com/method/wall.post?access_token={token}&attachments={attachments}&v=5.103&' \
                        'owner_id=-188359976&' \
                        'from_group=1&'.format(token=API_VK_TOKEN, attachments=id_image)
        session.post(url_post_wall)
        time.sleep(random.randrange(3, 25))


CONFIG = json.loads(open('/home/ubuntu/vk_scripts/config.json', 'r').read())
CLIENT_ID = 'BUTNbP_0z_j5Pg'
SECRET_REDDIT = get_reddit_token(CONFIG['secrets']['reddit_refresh_token'])
API_VK_TOKEN = CONFIG['secrets']['api_vk_token']
HEADERS = {'Authorization': 'bearer ' + SECRET_REDDIT, "User-Agent": "ChangeMeClient/0.1 by ad_meliorem"}
SUBREDDITS = ['anime', 'Animemes']
EXIST_IMAGES = os.listdir('/home/ubuntu/vk_scripts/images')
retry = Retry(
    total=10,
    read=10,
    connect=10,
    backoff_factor=10,
    status_forcelist=(500, 501, 502, 503, 504, 505, 429),
)
session = requests.Session()
adapter = HTTPAdapter(max_retries=retry)
session.mount('https://', adapter)
session.headers = HEADERS

images = []
for sub in SUBREDDITS:
    images += download_images_from_reddit(session, sub, 2)

upload_vk_photo(images)

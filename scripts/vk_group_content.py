import requests
import re
import os
import random
import time
import json
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from connectors.reddit import RedditConnector
from connectors.vk import VkConnector

REDDIT_CLIENT_ID = 'BUTNbP_0z_j5Pg'
SUBREDDITS_IDS = ['anime', 'Animemes']
VK_OWNER_ID = '-188359976'


def main():
    images = []
    reddit_connector = RedditConnector(REDDIT_CLIENT_ID)
    for subreddit_id in SUBREDDITS_IDS:
        images.append(reddit_connector.download_images_from_reddit(subreddit_id, 2))
    print(images)

    vk_connector = VkConnector(VK_OWNER_ID, 1)
    ids_photo = vk_connector.upload_images(images)
    for id_photo in ids_photo:
        vk_connector.create_post(attachment=id_photo)


if __name__ == "__main__":
    main()

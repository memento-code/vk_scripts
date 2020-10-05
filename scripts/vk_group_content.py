import json
from connectors.reddit import RedditConnector
from connectors.vk import VkConnector

SUBREDDIT_IDS = ['anime', 'Animemes']


def main():
    config = json.loads(open('scripts/config.json', 'r').read())
    reddit_config = config.get('reddit')
    reddit_connector = RedditConnector(
        client_id=reddit_config.get('client_id'),
        secret=reddit_config.get('secret'),
        refresh_token=reddit_config.get('refresh_token')
    )

    images = []
    for subreddit_id in SUBREDDIT_IDS:
        images + reddit_connector.download_images_from_reddit(subreddit_id, 2)

    vk_config = config.get('vk')
    vk_connector = VkConnector(
        owner_id=vk_config.get('owner_id'),
        from_group=True,
        token=vk_config.get('token')
    )

    ids_photo = vk_connector.upload_images(images)
    for id_photo in ids_photo:
        vk_connector.create_post(attachment=id_photo)


if __name__ == "__main__":
    main()

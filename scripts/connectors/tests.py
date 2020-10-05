import json
import pytest
from vk import VkConnector


def test_connector_vk():
    config = json.loads(open('/home/ubuntu/vk_scripts/scripts/config.json', 'r').read()).get('vk')
    connector = VkConnector(
        owner_id=config.get('owner_id'),
        from_group=True,
        token=config.get('token')
    )
    response = connector.request('GET', f'{connector.base_url}/method/account.getProfileInfo', params={
                          'access_token': connector.access_token,
                          'v': connector.version_api})
    upload_image = connector.upload_images(['test.jpg'])

    assert response.status_code == 200
    assert response.json()['response']['last_name'] == 'Vivere'
    for image in upload_image:
        assert 'photo' in image

    with pytest.raises(ValueError):
        connector.create_post()

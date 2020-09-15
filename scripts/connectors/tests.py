from vk import VkConnector


def test_connector_vk():
    connector = VkConnector('-188359976', 1)
    response = connector.request('GET', f'{connector.domain_url}/method/account.getProfileInfo', params={
                          'access_token': connector.access_token,
                          'v': connector.version_api})
    upload_image = connector.upload_images(['test.jpg'])

    assert response.status_code == 200
    assert response.json()['response']['last_name'] == 'Vivere'
    for image in upload_image:
        assert 'photo' in image

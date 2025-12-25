from ninja.testing import TestClient
from base.api.add_webpage import router_add_webpage
import pytest
from base.api.tests.conftest import DefaultTestValues

client = TestClient(router_add_webpage)

path = '/add_webpage'
method = 'POST'


@pytest.mark.django_db
def test_get_webpage_auth():
    """
    Test that unauthenticated users cannot access the endpoint
    """

    json_body = {'url': DefaultTestValues.url, 'interval': DefaultTestValues.interval}

    response = client.request(method=method, path=path, json=json_body)
    assert response.status_code == 401


@pytest.mark.django_db
@pytest.mark.parametrize(
    'url,status_code,expected_json',
    [
        (
            DefaultTestValues.url,
            201,
            {'message': 'Webpage tracked successfully'},
        ),
        (
            'invalid-url',
            422,
            {
                'detail': [
                    {
                        'ctx': {'error': 'relative URL without a base'},
                        'loc': ['body', 'data', 'url'],
                        'msg': 'Input should be a valid URL, relative URL without a base',
                        'type': 'url_parsing',
                    },
                ],
            },
        ),
    ],
)
def test_get_webpage(get_user, url, status_code, expected_json):
    json_body = {'url': url, 'interval': DefaultTestValues.interval}

    response = client.request(method=method, path=path, json=json_body, user=get_user)
    assert response.status_code == status_code
    assert response.json() == expected_json

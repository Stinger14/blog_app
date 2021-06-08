import json
import pathlib

import pytest
from jsonschema import validate, RefResolver

from blog.app import app
from blog.models import Article


@pytest.fixture
def client():
    app.config['TESTING'] = True

    with app.test_client() as client:
        yield client


def validate_payload(payload, schema_name):
    """
    Validate payload with selected schema
    """
    schemas_dir = str(
        f'{pathlib.Path(__file__).parent.absolute()}/schemas'
    )
    schema = json.loads(pathlib.Path(f'{schemas_dir}/{schema_name}').read_text())
    validate(
        payload,
        schema,
        resolver=RefResolver(
            'file://' + str(pathlib.Path(f'{schemas_dir}/{schema_name}').absolute()),
            schema  # it's used to resolve file: inside schemas correctly
        )
    )

@pytest.mark.parametrize(
    'data',
    [
        {
            'author': 'Maxly Garcia',
            'title': 'New Article',
            'content': 'Some extra awesome content'
        },
        {
            'author': 'John Doe',
            'title': 'New Article',
        },
        {
            'author': 'Maxly Garcia',
            'title': None,
            'content': 'Some extra awesome content'
        }
    ]
)
def test_create_article_bad_request(client, data):
    """
    GIVEN request data with invalid values or missing attributes
    WHEN endpoint /create-article/ is called
    THEN it should return status 400 and JSON body
    """
    response = client.post(
        '/create-article/',
        data=json.dumps(
            data
        ),
        content_type='application/json',
    )

    assert response.status_code == 400
    assert response.json is not None



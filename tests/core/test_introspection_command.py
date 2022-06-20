from json import JSONDecodeError
import requests_mock
from pytest import raises

from qenerate.core.introspection_command import IntrospectionCommand


TEST_URL = "http://my-url.zzzzz"


def test_valid_response(requests_mock):
    requests_mock.post(TEST_URL, json={})
    IntrospectionCommand.introspection_query(TEST_URL)


def test_does_not_return_json(requests_mock):
    requests_mock.post(TEST_URL, text="Not a json")

    with raises(JSONDecodeError):
        IntrospectionCommand.introspection_query(TEST_URL)

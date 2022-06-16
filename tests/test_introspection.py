from json import JSONDecodeError
import requests_mock
from pytest import raises

from qenerate.introspection import query_schema


TEST_URL = "http://my-url.zzzzz"


def test_valid_response(requests_mock):
    requests_mock.post(TEST_URL, json={})
    query_schema(TEST_URL)


def test_does_not_return_json(requests_mock):
    requests_mock.post(TEST_URL, text="Not a json")

    with raises(JSONDecodeError):
        query_schema(TEST_URL)

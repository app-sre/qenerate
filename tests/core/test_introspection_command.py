from json import JSONDecodeError

import pytest
import requests_mock

from qenerate.core.introspection_command import IntrospectionCommand

TEST_URL = "http://my-url.zzzzz"


def test_valid_response(requests_mock: requests_mock.Mocker) -> None:
    requests_mock.post(TEST_URL, json={})
    IntrospectionCommand.introspection_query(TEST_URL)


def test_does_not_return_json(requests_mock: requests_mock.Mocker) -> None:
    requests_mock.post(TEST_URL, text="Not a json")

    with pytest.raises(JSONDecodeError):
        IntrospectionCommand.introspection_query(TEST_URL)

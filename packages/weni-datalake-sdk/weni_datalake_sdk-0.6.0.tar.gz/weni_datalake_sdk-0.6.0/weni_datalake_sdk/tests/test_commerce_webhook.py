from unittest import mock

import pytest

from weni_datalake_sdk.clients.client import send_commerce_webhook_data
from weni_datalake_sdk.paths.commerce_webhook import CommerceWebhookPath

"""
Tests for send_commerce_webhook_data, covering all field combinations and edge cases.
"""


def make_event_data_all_fields():
    from datetime import datetime

    return {
        "status": 1,
        "template": "template",
        "template_variables": {"foo": "bar"},
        "contact_urn": "whatsapp:+55123456789",
        "error": {"msg": "error"},
        "data": {"foo": "bar"},
        "date": datetime.now().isoformat(),
        "project": "f9568d93-4984-496b-afd7-1dee458f12bc",
        "request": {"req": "value"},
        "response": {"res": "value"},
        "agent": "some-uuid",
    }


def make_event_data_minimal():
    return {"data": {"foo": "bar"}}


def make_event_data_structs_empty():
    return {
        "data": {},
        "template_variables": {},
        "error": {},
        "request": {},
        "response": {},
    }


def make_event_data_none_fields():
    return {
        "data": None,
        "template_variables": None,
        "error": None,
        "request": None,
        "response": None,
    }


def make_event_data_minimal_with_date():
    from datetime import datetime

    return {"data": {"test": "test"}, "date": datetime.now().isoformat()}


@pytest.mark.parametrize(
    "event_data_func",
    [
        make_event_data_all_fields,
        make_event_data_minimal,
        make_event_data_structs_empty,
        make_event_data_none_fields,
        make_event_data_minimal_with_date,
    ],
)
def test_send_commerce_webhook_data_variations(event_data_func):
    event_data = event_data_func()
    with mock.patch(
        "weni_datalake_sdk.clients.client.commerce_webhook_pb2_grpc.CommerceWebhookServiceStub"
    ) as mock_stub, mock.patch(
        "weni_datalake_sdk.clients.client.grpc.insecure_channel"
    ) as mock_channel:
        mock_instance = mock.Mock()
        mock_instance.InsertCommerceWebhookData.return_value.status = "ok"
        mock_stub.return_value = mock_instance
        mock_channel.return_value = mock.Mock()  # Prevents real channel creation
        result = send_commerce_webhook_data(CommerceWebhookPath, event_data)
        assert result == "ok"

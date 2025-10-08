from unittest import mock

import pytest

from weni_datalake_sdk.clients.client import (
    send_data,
    send_event_data,
    send_message_template_data,
    send_message_template_status_data,
    send_trace_data,
)
from weni_datalake_sdk.clients.dl_manager_client import DLManagerClient
from weni_datalake_sdk.paths.events_path import EventPath
from weni_datalake_sdk.paths.message_template_path import MessageTemplatePath
from weni_datalake_sdk.paths.message_template_status_path import (
    MessageTemplateStatusPath,
)
from weni_datalake_sdk.paths.msg_path import MsgPath
from weni_datalake_sdk.paths.trace_path import TracePath

BASE_URL = "https://dl-manager.example.com/api"


@pytest.fixture
def client():
    return DLManagerClient(base_url=BASE_URL)


@pytest.fixture
def mock_grpc_stub_msgs():
    with mock.patch(
        "weni_datalake_sdk.clients.msgs_pb2_grpc.DatalakeManagerServiceStub"
    ) as mock_stub:
        yield mock_stub


@pytest.fixture
def mock_grpc_stub_traces():
    with mock.patch(
        "weni_datalake_sdk.clients.traces_pb2_grpc.DatalakeManagerServiceStub"
    ) as mock_stub:
        yield mock_stub


@pytest.fixture
def mock_grpc_stub_events():
    with mock.patch(
        "weni_datalake_sdk.clients.events_pb2_grpc.DatalakeManagerServiceStub"
    ) as mock_stub:
        yield mock_stub


@pytest.fixture
def mock_grpc_stub_message_templates():
    with mock.patch(
        "weni_datalake_sdk.clients.message_templates_pb2_grpc.DatalakeManagerServiceStub"
    ) as mock_stub:
        yield mock_stub


@pytest.fixture
def mock_grpc_channel():
    with mock.patch("grpc.insecure_channel") as mock_channel:
        yield mock_channel


class TestSendData:
    def test_send_data_success(self, mock_grpc_stub_msgs, mock_grpc_channel):
        mock_stub_instance = mock_grpc_stub_msgs.return_value
        mock_stub_instance.InsertData.return_value.status = "success"

        msg_instance = dict(
            project_uuid="68c84e84-2d7d-4dc7-8193-50d0e2321b2e", text="Oi!"
        )

        send_data(MsgPath, msg_instance)

        mock_stub_instance.InsertData.assert_called_once()


class TestSendTraceData:
    def test_send_trace_data_success(self, mock_grpc_stub_traces, mock_grpc_channel):
        mock_stub_instance = mock_grpc_stub_traces.return_value
        mock_stub_instance.InsertTraceData.return_value.status = "success"

        trace_instance = dict(
            project_uuid="68c84e84-2d7d-4dc7-8193-50d0e2321b2e", receive="Wow!"
        )

        send_trace_data(TracePath, trace_instance)

        mock_stub_instance.InsertTraceData.assert_called_once()


class TestSendMessageTemplateData:
    def test_send_message_template_data_success(
        self, mock_grpc_stub_message_templates, mock_grpc_channel
    ):
        mock_stub_instance = mock_grpc_stub_message_templates.return_value
        mock_stub_instance.InsertMessageTemplateData.return_value.status = "success"

        template_instance = dict(template_id="template123", content="Olá!")

        send_message_template_data(MessageTemplatePath, template_instance)

        mock_stub_instance.InsertMessageTemplateData.assert_called_once()


class TestSendMessageTemplateStatusData:
    def test_send_message_template_status_data_success(
        self, mock_grpc_stub_message_templates, mock_grpc_channel
    ):
        mock_stub_instance = mock_grpc_stub_message_templates.return_value
        mock_stub_instance.InsertMessageTemplateStatusData.return_value.status = (
            "success"
        )

        status_instance = dict(template_id="template123", status="approved")

        send_message_template_status_data(MessageTemplateStatusPath, status_instance)

        mock_stub_instance.InsertMessageTemplateStatusData.assert_called_once()


class TestSendEventData:
    def test_send_event_data_success(self, mock_grpc_stub_events, mock_grpc_channel):
        mock_stub_instance = mock_grpc_stub_events.return_value
        mock_stub_instance.InsertEventData.return_value.status = "success"

        event_instance = dict(
            event_name="event1",
            key="key1",
            date="2024-01-01T00:00:00Z",
            project="proj1",
            contact_urn="urn1",
            value="val1",
            value_type="string",
            metadata={"meta": "data"},
        )

        send_event_data(EventPath, event_instance)

        mock_stub_instance.InsertEventData.assert_called_once()

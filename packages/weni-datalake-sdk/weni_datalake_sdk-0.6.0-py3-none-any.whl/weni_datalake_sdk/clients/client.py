import os
from concurrent.futures import ThreadPoolExecutor

import grpc
from google.protobuf import struct_pb2, timestamp_pb2

from weni_datalake_sdk.clients import (
    commerce_webhook_pb2,
    commerce_webhook_pb2_grpc,
    events_pb2,
    events_pb2_grpc,
    message_templates_pb2,
    message_templates_pb2_grpc,
    msgs_pb2,
    msgs_pb2_grpc,
    traces_pb2,
    traces_pb2_grpc,
)
from weni_datalake_sdk.paths.validator import validate_path

SERVER_ADDRESS = os.environ.get("DATALAKE_SERVER_ADDRESS")


def send_data(path, data):
    channel = grpc.insecure_channel(target=SERVER_ADDRESS)
    stub = msgs_pb2_grpc.DatalakeManagerServiceStub(channel)

    if isinstance(path, type):
        path = path()

    validate_path(path)

    request = msgs_pb2.InsertRequest(path=path.get_table_name(), data=data)

    response = stub.InsertData(request)
    print("Server response:", response.status)


def send_trace_data(path_class, data):
    validate_path(path_class)

    channel = grpc.insecure_channel(SERVER_ADDRESS)
    stub = traces_pb2_grpc.DatalakeManagerServiceStub(channel)

    request = traces_pb2.InsertTraceRequest(path=path_class.get_table_name(), data=data)

    response = stub.InsertTraceData(request)
    return response.status


def send_message_template_data(path_class, data):
    validate_path(path_class)

    channel = grpc.insecure_channel(SERVER_ADDRESS)
    stub = message_templates_pb2_grpc.DatalakeManagerServiceStub(channel)

    request = message_templates_pb2.InsertMessageTemplateRequest(data=data)

    response = stub.InsertMessageTemplateData(request)
    return response.status


DATALAKE_MAXIMUN_WORKERS = os.environ.get("DATALAKE_MAXIMUN_WORKERS", 5)
MESSAGE_TEMPLATE_EXECUTOR = ThreadPoolExecutor(max_workers=DATALAKE_MAXIMUN_WORKERS)


def send_message_template_data_async(path_class, data):
    """
    Send message template data in parallel using the global executor.
    Returns a Future.
    """
    return MESSAGE_TEMPLATE_EXECUTOR.submit(
        send_message_template_data, path_class, data
    )


def send_message_template_status_data(path_class, data):
    validate_path(path_class)

    channel = grpc.insecure_channel(SERVER_ADDRESS)
    stub = message_templates_pb2_grpc.DatalakeManagerServiceStub(channel)

    request = message_templates_pb2.InsertMessageTemplateStatusRequest(data=data)

    response = stub.InsertMessageTemplateStatusData(request)
    return response.status


MESSAGE_TEMPLATE_STATUS_EXECUTOR = ThreadPoolExecutor(
    max_workers=DATALAKE_MAXIMUN_WORKERS
)


def send_message_template_status_data_async(path_class, data):
    """
    Send event data in parallel using the global executor.
    Returns a Future.
    """
    return MESSAGE_TEMPLATE_STATUS_EXECUTOR.submit(
        send_message_template_status_data, path_class, data
    )


def send_event_data(path_class, data):
    validate_path(path_class)

    from datetime import datetime

    from google.protobuf import struct_pb2, timestamp_pb2

    channel = grpc.insecure_channel(SERVER_ADDRESS)
    stub = events_pb2_grpc.DatalakeManagerServiceStub(channel)

    # Convert date to Timestamp
    timestamp = timestamp_pb2.Timestamp()
    if data.get("date"):
        try:
            dt = datetime.fromisoformat(data["date"].replace("Z", "+00:00"))
            timestamp.FromDatetime(dt)
        except Exception:
            timestamp.GetCurrentTime()
    else:
        timestamp.GetCurrentTime()

    # Create ValueData for the value
    value_data = events_pb2.ValueData()
    value_data.string_value = str(data.get("value", ""))

    # Create metadata struct
    metadata = None
    if data.get("metadata"):
        metadata = struct_pb2.Struct()
        metadata.update(data["metadata"])

    VALUE_TYPE_MAP = {
        "string": events_pb2.VALUE_TYPE_STRING,
        "int": events_pb2.VALUE_TYPE_INT,
        "list": events_pb2.VALUE_TYPE_LIST,
        "bool": events_pb2.VALUE_TYPE_BOOL,
    }

    value_type_str = data.get("value_type", "string").lower()
    value_type = VALUE_TYPE_MAP.get(value_type_str, events_pb2.VALUE_TYPE_STRING)

    # Create request with individual fields as defined in proto
    request = events_pb2.InsertEventRequest(
        event_name=data.get("event_name", ""),
        key=data.get("key", ""),
        date=timestamp,
        project=data.get("project", ""),
        contact_urn=data.get("contact_urn", ""),
        value_type=value_type,
        value=value_data,
        metadata=metadata,
    )

    response = stub.InsertEventData(request)
    return response.status


EVENT_EXECUTOR = ThreadPoolExecutor(max_workers=DATALAKE_MAXIMUN_WORKERS)


def send_event_data_async(path_class, data):
    """
    Send event data in parallel using the global executor.
    Returns a Future.
    """
    return EVENT_EXECUTOR.submit(send_event_data, path_class, data)


def send_commerce_webhook_data(path_class, data):
    validate_path(path_class)

    channel = grpc.insecure_channel(SERVER_ADDRESS)
    stub = commerce_webhook_pb2_grpc.CommerceWebhookServiceStub(channel)

    def to_struct(val):
        if isinstance(val, dict):
            s = struct_pb2.Struct()
            s.update(val)
            return s
        return val

    date = None
    if data.get("date"):
        try:
            from datetime import datetime

            ts = timestamp_pb2.Timestamp()
            dt = datetime.fromisoformat(data["date"].replace("Z", "+00:00"))
            ts.FromDatetime(dt)
            date = ts
        except Exception:
            pass

    request = commerce_webhook_pb2.InsertCommerceWebhookRequest(
        status=data.get("status"),
        template=data.get("template"),
        template_variables=to_struct(data.get("template_variables"))
        if data.get("template_variables") is not None
        else None,
        contact_urn=data.get("contact_urn"),
        error=to_struct(data.get("error")) if data.get("error") is not None else None,
        data=to_struct(data.get("data")) if data.get("data") is not None else None,
        date=date,
        project=data.get("project"),
        request=to_struct(data.get("request"))
        if data.get("request") is not None
        else None,
        response=to_struct(data.get("response"))
        if data.get("response") is not None
        else None,
        agent=data.get("agent"),
    )

    response = stub.InsertCommerceWebhookData(request)
    return response.status

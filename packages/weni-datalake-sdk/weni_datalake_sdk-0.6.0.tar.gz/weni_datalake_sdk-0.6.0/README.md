# Weni Data Lake SDK

The Weni Data Lake SDK is a Python library that provides an interface to interact with Weni's data lake services. It supports operations for sending data, managing message templates, and handling traces.

## Installation

```bash
pip install weni-datalake-sdk
In case you are using poetry, you can add the package to your project with the following command:
poetry add weni-datalake-sdk
```

## Environment Variables

To insert data into the data lake, you need to set the following environment variables:

```bash
DATALAKE_SERVER_ADDRESS=your_server_address
```

To get data from the data lake, you need to set the following environment variables:

```bash
REDSHIFT_QUERY_BASE_URL=your_redshift_url
REDSHIFT_SECRET=your_secret
REDSHIFT_ROLE_ARN=your_role_arn
MESSAGE_TEMPLATES_METRIC_NAME=your_metric_name (if you want to get message templates)
TRACES_METRIC_NAME=your_trace_metric_name (if you want to get traces)
EVENTS_METRIC_NAME=your_event_metric_name (if you want to get events)
```

Although you will need some AWS credentials to get data from the data lake, you can use the following environment variables:

```bash
AWS_ACCESS_KEY_ID=your_access_key_id
AWS_SECRET_ACCESS_KEY=your_secret_access_key
AWS_DEFAULT_REGION=your_region
```

This is important that we will use assumed role to get data from the data lake.

## Usage Examples

### 1. Sending Data

```python
from weni_datalake_sdk.clients.client import send_data
from weni_datalake_sdk.paths.your_path import YourPath

# Prepare your data
data = {
    "field1": "value1",
    "field2": "value2"
}

# Send data using a path class
send_data(YourPath, data)

# Or using an instantiated path
path = YourPath()
send_data(path, data)
```

### 2. Send Event Data

```python
from weni_datalake_sdk.clients.client import send_event_data
from weni_datalake_sdk.paths.events_path import EventPath

# Prepare your data
data = {
    "event_name": "event_name",
    "key": "key",
    "value": "value",
    "value_type": "value_type",
    "date": "2021-01-01",
    "project": "project_uuid",
    "contact_urn": "contact_urn",
    "metadata": {
        "field1": "value1",
        "field2": "value2"
    }
}
```

### 3. Send Commerce Webhook Data

```python
from weni_datalake_sdk.clients.client import send_commerce_webhook_data
from weni_datalake_sdk.paths.commerce_webhook import CommerceWebhookPath
from datetime import datetime

# Prepare your data (all fields are optional)
data = {
    "status": 1,
    "template": "template_name",
    "template_variables": {"foo": "bar"},
    "contact_urn": "whatsapp:+55123456789",
    "error": {"msg": "error"},
    "data": {"foo": "bar"},
    "date": datetime.now().isoformat(),
    "project": "your-project-uuid",
    "request": {"req": "value"},
    "response": {"res": "value"},
    "agent": "some-uuid"
}

# Send commerce webhook data
send_commerce_webhook_data(CommerceWebhookPath, data)
```

All fields are optional. For Struct fields, use dicts. For date, use an ISO string. If you don't want to send a field, omit it or set it to None.

### 4. Get Message Templates

```python
from weni_datalake_sdk.clients.redshift.message_templates import get_message_templates

# Get templates with specific parameters
result = get_message_templates(
    contact_urn="contact123",
    template_uuid="template_uuid"
)

```

### 5. Get Traces

```python
from weni_datalake_sdk.clients.redshift.traces import get_traces

# Get traces with query parameters
result = get_traces(
    query_params={
        "message_uuid": "123e4567-e89b-12d3-a456-426614174000"
    }
)
```

### 6. Get Events

```python
from weni_datalake_sdk.clients.redshift.events import get_events    

# Get events with query parameters
result = get_events(
    query_params={
        "date_start": "2021-01-01", # date_start is required
        "date_end": "2021-01-01", # date_end is required
        "project": "project_uuid", # project is optional
        "event_type": "event_type", # event_type is optional
        "contact_urn": "contact_urn", # contact_urn is optional
        "event_name": "event_name", # event_name is optional
        "key": "key", # key is optional
        "value": "value", # value is optional
        "value_type": "value_type" # value_type is optional
    }
)
```

### 5. Get Events Count

```python
from weni_datalake_sdk.clients.redshift.events import get_events_count

# Get events count with required and optional parameters
result = get_events_count(
    project="your_project_uuid", # project is required
    date_start="2025-06-03T00:00:00Z", # date_start is required
    date_end="2025-07-30T23:59:59Z", # date_end is required
    event_type="event_type", # event_type is optional
    event_name="event_name", # event_name is optional
    key="topics",  # key is optional
    value="value", # value is optional
    value_type="value_type", # value_type is optional
    contact_urn="contact_urn", # contact_urn is optional
)
print(result)
```

### 6. Get Events Count By Group

```python
from weni_datalake_sdk.clients.redshift.events import get_events_count_by_group

# Get events count grouped by a metadata key
result = get_events_count_by_group(
    project="your_project_uuid", # project is required
    date_start="2025-06-03T00:00:00Z", # date_start is required
    date_end="2025-07-30T23:59:59Z", # date_end is required
    metadata_key="topic_uuid", # metadata_key is required
    event_type="event_type", # event_type is optional
    event_name="event_name", # event_name is optional
    key="topics",  # key is optional
    value="value", # value is optional
    value_type="value_type", # value_type is optional
    contact_urn="contact_urn", # contact_urn is optional
    group_by="subtopic_uuid",  # group_by is optional
    metadata_value="uuid" # metadata_value is optional
)
print(result)
```

If you don't pass group_by value, the result will be aggregated by value.

### 7. Get Events from silver tables

```python
from weni_datalake_sdk.clients.redshift.events import get_events_silver

# Get events count grouped by a metadata key
result = get_events_silver(
    project="your_project_uuid", # project is required
    date_start="2025-06-03T00:00:00Z", # date_start is required
    date_end="2025-07-30T23:59:59Z", # date_end is required
    table="topics", # table is required
    ... # other parameters are optional
)
print(result)
```

### 8. Get Events Count from silver tables

```python
from weni_datalake_sdk.clients.redshift.events import get_events_silver_count
```

# Get events count grouped by a metadata key
result = get_events_silver_count(
    project="your_project_uuid", # project is required
    date_start="2025-06-03T00:00:00Z", # date_start is required
    date_end="2025-07-30T23:59:59Z", # date_end is required
    table="topics", # table is required
    ... # other parameters are optional
)
print(result)
```

### 9. Get Events Count from silver tables by group

```python
from weni_datalake_sdk.clients.redshift.events import get_events_silver_count_by_group
```

# Get events count grouped by a metadata key
result = get_events_silver_count_by_group(
    project="your_project_uuid", # project is required
    date_start="2025-06-03T00:00:00Z", # date_start is required
    date_end="2025-07-30T23:59:59Z", # date_end is required
    table="topics", # table is required
    ... # other parameters are optional
)
print(result)
```

The valid tables are: "topics", "weni_csat", "weni_nps", "conversation_classification".
This function is used to get events from silver tables. You can use the same parameters as the get_events function.

Don't forget to set in your enviroment the following variables to get silver data:

EVENTS_SILVER_METRIC_NAME
EVENTS_SILVER_COUNT_METRIC_NAME
EVENTS_SILVER_COUNT_BY_GROUP_METRIC_NAME

## Error Handling

The SDK includes proper error handling. Always wrap your calls in try-except blocks:

```python
try:
    result = get_message_templates(template_id="template123")
except Exception as e:
    print(f"Error: {e}")
```

## Best Practices

1. **Environment Variables**: Always ensure all required environment variables are set before using the SDK.
2. **Path Validation**: Use proper path classes instead of raw strings.
3. **Error Handling**: Implement proper error handling in your code.
4. **Data Types**: Ensure you're passing the correct data types for each parameter.
5. **Security**: Never hardcode sensitive information like tokens or credentials.

## Common Issues and Solutions

1. **Connection Issues**
   - Ensure `DATALAKE_SERVER_ADDRESS` is correct and accessible
   - Check your network connectivity

2. **Authentication Errors**
   - Verify your AWS credentials are properly configured
   - Check if `REDSHIFT_SECRET` and `REDSHIFT_ROLE_ARN` are correct

3. **Missing Environment Variables**
   - Double-check all required environment variables are set
   - Use a `.env` file for local development

## Contributing

For contributing to this SDK, please follow these steps:

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

import os

from weni_datalake_sdk.clients.redshift.redshift_client import query_dc_api

valid_tables = ["topics", "weni_csat", "weni_nps", "conversation_classification"]


def clean_quotes(obj):
    if isinstance(obj, dict):
        return {k: clean_quotes(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [clean_quotes(item) for item in obj]
    elif isinstance(obj, str):
        if obj.startswith('"') and obj.endswith('"'):
            return obj[1:-1]
        return obj
    else:
        return obj


def get_events(**kwargs) -> dict:
    metric = os.environ.get("EVENTS_METRIC_NAME")

    if not kwargs.get("project"):
        raise Exception("Project is required")

    if not kwargs.get("date_start"):
        raise Exception("Date start is required")

    if not kwargs.get("date_end"):
        raise Exception("Date end is required")

    try:
        result = query_dc_api(metric=metric, query_params=kwargs)
        data = result.json()
        return clean_quotes(data)

    except Exception as e:
        raise Exception(f"Error querying events: {e}")


def get_events_count(**kwargs) -> dict:
    metric = os.environ.get("EVENTS_COUNT_METRIC_NAME")

    if not kwargs.get("project"):
        raise Exception("Project is required")

    if not kwargs.get("date_start"):
        raise Exception("Date start is required")

    if not kwargs.get("date_end"):
        raise Exception("Date end is required")

    try:
        result = query_dc_api(metric=metric, query_params=kwargs)
        data = result.json()
        return data

    except Exception as e:
        raise Exception(f"Error querying events count: {e}")


def get_events_count_by_group(**kwargs) -> dict:
    metric = os.environ.get("EVENTS_COUNT_BY_GROUP_METRIC_NAME")

    if not kwargs.get("project"):
        raise Exception("Project is required")

    if not kwargs.get("date_start"):
        raise Exception("Date start is required")

    if not kwargs.get("date_end"):
        raise Exception("Date end is required")

    if not kwargs.get("metadata_key"):
        raise Exception("metadata_key is required")

    try:
        result = query_dc_api(metric=metric, query_params=kwargs)
        data = result.json()
        return clean_quotes(data)

    except Exception as e:
        raise Exception(f"Error querying events count: {e}")


def get_events_silver(**kwargs) -> dict:
    metric = os.environ.get("EVENTS_SILVER_METRIC_NAME")
    table = kwargs.get("table")

    if not kwargs.get("project"):
        raise Exception("Project is required")

    if not kwargs.get("date_start"):
        raise Exception("Date start is required")

    if not kwargs.get("date_end"):
        raise Exception("Date end is required")

    if not table:
        raise Exception("Table is required")

    if table not in valid_tables:
        raise Exception("Table is not valid")

    try:
        result = query_dc_api(metric=metric, query_params=kwargs)
        data = result.json()
        return clean_quotes(data)
    except Exception as e:
        raise Exception(f"Error querying events silver: {e}")


def get_events_silver_count(**kwargs) -> dict:
    metric = os.environ.get("EVENTS_SILVER_COUNT_METRIC_NAME")
    table = kwargs.get("table")

    if not kwargs.get("project"):
        raise Exception("Project is required")

    if not kwargs.get("date_start"):
        raise Exception("Date start is required")

    if not kwargs.get("date_end"):
        raise Exception("Date end is required")

    if not table:
        raise Exception("Table is required")

    if table not in valid_tables:
        raise Exception("Table is not valid")

    try:
        result = query_dc_api(metric=metric, query_params=kwargs)
        data = result.json()
        return clean_quotes(data)
    except Exception as e:
        raise Exception(f"Error querying events silver: {e}")


def get_events_silver_count_by_group(**kwargs) -> dict:
    metric = os.environ.get("EVENTS_SILVER_COUNT_BY_GROUP_METRIC_NAME")
    table = kwargs.get("table")

    if not kwargs.get("project"):
        raise Exception("Project is required")

    if not kwargs.get("date_start"):
        raise Exception("Date start is required")

    if not kwargs.get("date_end"):
        raise Exception("Date end is required")

    if not kwargs.get("metadata_key"):
        raise Exception("metadata_key is required")

    if not table:
        raise Exception("Table is required")

    if table not in valid_tables:
        raise Exception("Table is not valid")

    try:
        result = query_dc_api(metric=metric, query_params=kwargs)
        data = result.json()
        return clean_quotes(data)

    except Exception as e:
        raise Exception(f"Error querying events count: {e}")

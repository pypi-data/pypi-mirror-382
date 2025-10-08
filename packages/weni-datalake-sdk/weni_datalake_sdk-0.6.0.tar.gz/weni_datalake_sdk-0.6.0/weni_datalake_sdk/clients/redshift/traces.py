import os

from weni_datalake_sdk.clients.redshift.redshift_client import query_dc_api


def get_traces(query_params: dict = None) -> dict:
    metric = os.environ.get("TRACES_METRIC_NAME")
    try:
        result = query_dc_api(metric=metric, query_params=query_params)
        return result

    except Exception as e:
        raise Exception(f"Error querying traces: {e}")

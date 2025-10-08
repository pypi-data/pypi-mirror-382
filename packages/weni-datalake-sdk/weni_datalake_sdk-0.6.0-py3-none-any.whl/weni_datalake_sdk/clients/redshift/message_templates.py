import os

from weni_datalake_sdk.clients.redshift.redshift_client import query_dc_api


def get_message_templates(
    contact_urn: str = None, template_uuid: str = None, query_params: dict = None
) -> dict:
    metric = os.environ.get("MESSAGE_TEMPLATES_METRIC_NAME")

    final_params = query_params.copy() if query_params else {}

    if contact_urn:
        final_params["contact_urn"] = contact_urn
    if template_uuid:
        final_params["template_uuid"] = template_uuid

    try:
        result = query_dc_api(metric=metric, query_params=final_params)
        return result

    except Exception as e:
        raise Exception(f"Error querying message templates: {e}")

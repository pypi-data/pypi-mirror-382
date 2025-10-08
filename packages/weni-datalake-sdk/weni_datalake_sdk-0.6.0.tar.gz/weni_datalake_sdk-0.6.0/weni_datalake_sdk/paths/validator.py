from weni_datalake_sdk.paths.commerce_webhook import CommerceWebhookPath
from weni_datalake_sdk.paths.events_path import EventPath
from weni_datalake_sdk.paths.message_template_path import MessageTemplatePath
from weni_datalake_sdk.paths.message_template_status_path import (
    MessageTemplateStatusPath,
)
from weni_datalake_sdk.paths.msg_path import MsgPath
from weni_datalake_sdk.paths.trace_path import TracePath
from weni_datalake_sdk.utils.exceptions import ValidationError

VALID_CONTRACTS = {
    "messages": MsgPath,
    "traces": TracePath,
    "message_templates": MessageTemplatePath,
    "message_template_status": MessageTemplateStatusPath,
    "events": EventPath,
    "commerce_webhook": CommerceWebhookPath,
}


def validate_path(path_class):
    """
    Validated if path is correct.
    """
    table_name = path_class.get_table_name()

    if table_name not in VALID_CONTRACTS:
        raise ValidationError(f"Path '{table_name}' is not valid.")

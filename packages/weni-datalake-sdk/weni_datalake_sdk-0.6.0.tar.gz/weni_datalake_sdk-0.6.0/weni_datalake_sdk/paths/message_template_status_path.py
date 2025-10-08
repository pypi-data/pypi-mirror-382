from weni_datalake_sdk.paths.base_path import BasePath


class MessageTemplateStatusPath(BasePath):
    TABLE_NAME = "message_template_status"

    @classmethod
    def get_table_name(cls):
        return cls.TABLE_NAME

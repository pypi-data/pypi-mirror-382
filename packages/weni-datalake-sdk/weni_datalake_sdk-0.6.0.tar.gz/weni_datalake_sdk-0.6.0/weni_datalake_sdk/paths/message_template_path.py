from weni_datalake_sdk.paths.base_path import BasePath


class MessageTemplatePath(BasePath):
    TABLE_NAME = "message_templates"

    @classmethod
    def get_table_name(cls):
        return cls.TABLE_NAME

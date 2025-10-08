from weni_datalake_sdk.paths.base_path import BasePath


class MsgPath(BasePath):
    TABLE_NAME = "messages"

    @classmethod
    def get_table_name(cls):
        return cls.TABLE_NAME

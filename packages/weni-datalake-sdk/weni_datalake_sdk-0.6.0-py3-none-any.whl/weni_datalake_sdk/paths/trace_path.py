from weni_datalake_sdk.paths.base_path import BasePath


class TracePath(BasePath):
    TABLE_NAME = "traces"

    @classmethod
    def get_table_name(cls):
        return cls.TABLE_NAME

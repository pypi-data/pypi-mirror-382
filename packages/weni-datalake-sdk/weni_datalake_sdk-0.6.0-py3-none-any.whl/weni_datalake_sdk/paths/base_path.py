class BasePath:
    """Class to define the base path for the project"""

    @classmethod
    def get_table_name(cls):
        raise NotImplementedError("Subclasses should implement get_table_name")

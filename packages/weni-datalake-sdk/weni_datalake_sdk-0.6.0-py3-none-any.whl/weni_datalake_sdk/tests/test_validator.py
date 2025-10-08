import pytest

from weni_datalake_sdk.paths.msg_path import MsgPath
from weni_datalake_sdk.paths.validator import validate_path
from weni_datalake_sdk.utils.exceptions import ValidationError


class FakePath:
    @staticmethod
    def get_table_name():
        return "invalid_table"


def test_validate_path_success():
    try:
        validate_path(MsgPath)
    except ValidationError:
        pytest.fail("validate_path got a error!")


def test_validate_path_fail():
    with pytest.raises(ValidationError, match="Path 'invalid_table' is not valid."):
        validate_path(FakePath)

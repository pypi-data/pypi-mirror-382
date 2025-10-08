from weni_datalake_sdk.paths.msg_path import MsgPath


def test_paths():
    assert MsgPath.get_table_name() == "messages"

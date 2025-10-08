from weni.clients.dl_manager_client import DLManagerClient


def insert(path_class, data):
    client = DLManagerClient()
    return client.insert(path_class, data)

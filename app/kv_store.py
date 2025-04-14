from app.utilities import create_file_if_not_exists, get_json, write_json


class JsonKvStore:
    def __init__(self, file_path, initial_data="{}"):
        self.file_path = file_path
        create_file_if_not_exists(file_path, initial_data)
        self.store = get_json(self.file_path)

    def remove(self, key):
        if key in self.store:
            del self.store[key]

    def add(self, key, value):
        self.store[key] = value

    def has(self, key):
        return key in self.store

    def equal(self, key, value):
        return self.store[key] == value

    def get_all(self):
        return self.store.copy()

    def get_by_key(self, key):
        return self.store.get(key, None)

    def save(self):
        write_json(self.file_path, self.store)

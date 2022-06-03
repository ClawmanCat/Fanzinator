import json
import os


class serialized_dict:
    def __init__(self, file):
        self.file    = file
        self.storage = dict()
        self.read()

    def read(self):
        if os.path.exists(self.file):
            with open(self.file, 'r') as handle:
                self.storage = json.load(handle)

    def write(self):
        with open(self.file, 'w') as handle:
            json.dump(self.storage, handle, indent = 4)

    def insert(self, k, v):
        self.storage[k] = v
        self.write()

    def get(self, k):
        return self.storage[k]

    def contains(self, k):
        return k in self.storage

    def size(self):
        return len(self.storage)
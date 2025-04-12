from nano_vectordb import NanoVectorDB


class NanoVectorStorage:
    def __init__(self, storage_file, dimensions):
        self.storage_file = storage_file
        self.dimensions = dimensions
        self.db = NanoVectorDB(self.dimensions, storage_file=storage_file)

    def upsert(self, rows):
        self.db.upsert(rows)

    def delete(self, ids):
        self.db.delete(ids)

    def query(self, query, top_k=10, better_than_threshold=0.02):
        return self.db.query(query=query, top_k=top_k, better_than_threshold=better_than_threshold)

    def save(self):
        self.db.save()

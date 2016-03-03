import leveldb


class SSTable(object):
    def __init__(self, table_path):
        self.table_path = table_path
        self.table = leveldb.LevelDB(self.table_path)

    def put(self, key, value):
        self.table.Put(key, value)

    def get(self, key):
        try:
            return self.table.Get(key)
        except KeyError:
            return None

    def delete(self, key):
        self.table.Delete(key)

    def write_documents(self, documents):
        batch = leveldb.WriteBatch()
        for doc in documents:
            batch.Put(doc.doc_id, doc.SerializeToString())
        self.table.Write(batch, sync=True)

    def __iter__(self):
        return self.table.RangeIter()

    def revserse(self):
        return self.table.RangeIter(reverse=True)

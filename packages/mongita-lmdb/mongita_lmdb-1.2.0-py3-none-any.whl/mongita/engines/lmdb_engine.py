import os
import threading
import shutil

from ..common import MetaStorageObject
from .engine_common import Engine
from .lmdb_backend import LmdbStorage, ShardedLmdbStorage

LMDB_ENGINE_INCUMBENTS = {}


class LmdbEngine(Engine):
    """
    """

    def __init__(self, path, use_shards=False, **kwargs):
        self.path = path
        self.use_shards = use_shards
        self.kwargs = kwargs
        self.lock = threading.RLock()
        self.base_storage_path = path
        if use_shards:
            self.storage = ShardedLmdbStorage(path, **kwargs)
        else:
            self.storage = LmdbStorage(path, **kwargs)

    @classmethod
    def create(cls, path, use_shards=False, **kwargs):
        if path in LMDB_ENGINE_INCUMBENTS:
            LMDB_ENGINE_INCUMBENTS[path].close()
        engine = cls(path, use_shards, **kwargs)
        LMDB_ENGINE_INCUMBENTS[path] = engine
        return engine

    def _get_key(self, collection, doc_id):
        return os.path.join(collection, str(doc_id))

    def close(self):
        self.storage.close()
        if self.path in LMDB_ENGINE_INCUMBENTS:
            del LMDB_ENGINE_INCUMBENTS[self.path]

    def put_doc(self, collection, doc, no_overwrite=False):
        if no_overwrite and self.doc_exists(collection, doc['_id']):
            return False
        key = self._get_key(collection, doc['_id'])
        self.storage.store_data([doc], [key])
        return True

    def get_doc(self, collection, doc_id):
        key = self._get_key(collection, doc_id)
        docs = self.storage.get_data([key])
        return docs[0] if docs else None

    def doc_exists(self, collection, doc_id):
        return self.get_doc(collection, doc_id) is not None

    def list_ids(self, collection, limit=None):
        prefix = os.path.join(collection, '')
        all_keys = self.storage.list_ids()
        ids = []
        for key in all_keys:
            if key.startswith(prefix):
                rest = key[len(prefix):]
                if '/' not in rest and '$.metadata' not in rest:
                    ids.append(rest)
        if limit:
            return ids[:limit]
        return ids

    def delete_doc(self, collection, doc_id):
        key = self._get_key(collection, doc_id)
        self.storage.delete_data([key])
        return True

    def delete_dir(self, collection):
        prefix = os.path.join(collection, '')
        all_keys = self.storage.list_ids()
        keys_to_delete = [key for key in all_keys if key.startswith(prefix)]
        self.storage.delete_data(keys_to_delete)
        # also delete metadata
        metadata_key = os.path.join(collection, "$.metadata")
        self.storage.delete_data([metadata_key])
        return True

    def create_path(self, collection):
        # Not needed for lmdb
        return True

    def put_metadata(self, collection, doc):
        key = os.path.join(collection, "$.metadata")
        self.storage.store_data([doc.to_storage(as_bson=True)], [key])
        return True

    def get_metadata(self, collection):
        key = os.path.join(collection, "$.metadata")
        data = self.storage.get_data([key])
        if not data or data[0] is None:
            return None
        return MetaStorageObject.from_storage(data[0], from_bson=True)

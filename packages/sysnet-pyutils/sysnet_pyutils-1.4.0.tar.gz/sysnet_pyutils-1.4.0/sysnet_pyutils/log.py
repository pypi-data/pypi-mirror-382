from datetime import datetime

import logging
import pymongo

from utils import local_datetime, local_now


class MongoHandler(logging.Handler):
    """
    A logging handler that will record messages to a (optionally capped)
    MongoDB collection.
    >>> client = pymongo.MongoClient()
    >>> collection = client['logging']['utils']
    >>> logger = logging.getLogger("mongotest")
    >>> logger.addHandler(MongoHandler(drop=True))
    >>> logger.error("Hello, world!")
    >>> collection.find_one()['message']
    u'Hello, world!'
    """

    def __init__(
            self, level=logging.NOTSET, host="localhost", port=27017, username=None, password=None,
            database='logging', collection='utils', capped=True, size=100000, drop=False):
        logging.Handler.__init__(self, level)
        self.client = pymongo.MongoClient(host=host, port=port, username=username, password=password)
        self.database = self.client[database]

        if collection in self.database.list_collection_names():
            if drop:
                self.database.drop_collection(collection)
                self.collection = self.database.create_collection(
                    collection, capped=capped, size=size)
            else:
                self.collection = self.database[collection]
        else:
            self.collection = self.database.create_collection(
                collection, capped=capped, size=size)

    def emit(self, record):
        document = {
            'when': local_now(),
            'created': local_datetime(datetime.fromtimestamp(record.created)),
            'levelno': record.levelno,
            'levelname': record.levelname,
            'message': record.msg,
            'name': record.name,
            'module': record.module,
            'func_name': record.funcName,
            'filename': record.filename,
            'lineno': record.lineno,
            'process': record.process,
            'process_name': record.processName,
            'thread': record.thread,
            'thread_name': record.threadName,
            'stack_info': record.stack_info,
        }
        self.collection.insert_one(document)

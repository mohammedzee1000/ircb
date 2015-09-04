import asyncio
from uuid import uuid1

from ircb.lib.dispatcher import dispatcher


class BaseStore(object):
    CREATE_SIGNAL = None
    CREATED_SIGNAL = None
    UPDATE_SIGNAL = None
    UPDATED_SIGNAL = None
    DELETE_SIGNAL = None
    DELETED_SIGNAL = None

    @classmethod
    def create(cls, data, async=False, timeout=10):
        result = yield from cls._create(data, async)
        return result

    @classmethod
    def update(cls, data):
        result = yield from cls._update(data)
        return result

    @classmethod
    def delete(cls, id):
        raise NotImplementedError

    @classmethod
    def _create(cls, data, async=False):
        task_id = cls.get_task_id(data)
        fut = asyncio.Future()

        def callback(signal, data, taskid=None):
            if taskid == task_id:
                fut.set_result(data)

        dispatcher.register(callback, signal=cls.CREATED_SIGNAL)
        dispatcher.send(cls.CREATE_SIGNAL, data, taskid=task_id)

        result = yield from fut
        return fut.result()

    @classmethod
    def _update(cls, data):
        task_id = cls.get_task_id(data)
        future = asyncio.Future()

        def callback(signal, data, taskid=None):
            if taskid == task_id:
                future.set_result(data)
        dispatcher.register(callback, signal=cls.UPDATED_SIGNAL)
        dispatcher.send(cls.UPDATE_SIGNAL, data, taskid=task_id)

        result = yield from future
        return result

    @classmethod
    def get_task_id(self, data):
        return str(uuid1())
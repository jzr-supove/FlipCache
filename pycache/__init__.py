import json
import redis
from pycache import types
from pycache.types import DataType
from typing import Any, Union
from collections import OrderedDict


class PyCache:
    def __init__(self,
                 name: str = None,
                 local_max: int = 100,
                 expire_time: int = None,
                 key_type: type = str,
                 value_type: DataType = DataType.STRING,
                 value_default: Any = None,
                 redis_protocol: redis.Redis = None,
                 refresh_expire_time_on_get: bool = False):

        assert key_type == int or key_type == str, "Invalid key_type, must be int or str"

        self.__data = OrderedDict()
        self._redis = None

        if isinstance(redis_protocol, redis.Redis):
            kwargs = redis_protocol.get_connection_kwargs()
            assert kwargs.get("decode_responses", False), "Redis protocol with decode_responses=True must be passed"
            self._redis = redis_protocol

        if not self._redis:
            self._redis = redis.Redis(decode_responses=True)

        self.local_max = local_max
        self.et = expire_time
        self.kp = name
        self.value_default = value_default
        self.refresh_et = refresh_expire_time_on_get

        self.key_type = key_type

        if value_type == DataType.JSON:
            self.encoder = json.dumps
            self.decoder = json.loads

        elif value_type == DataType.INTEGER:
            self.encoder = None
            self.decoder = int

        elif value_type == DataType.STRING:
            self.encoder = None
            self.decoder = None

    def _key(self, name):
        return f"{self.kp}:{name}"

    def __getitem__(self, key):
        if key in self.__data:
            return self.__data[key]
        else:
            data = self._redis.get(self._key(key))

            if data:
                if self.decoder:
                    data = self.decoder(data)

                self.__data[key] = data

                if self.et and self.refresh_et:
                    self._redis.expire(self._key(key), self.et)

                return data
            else:
                if self.value_default is not None:
                    self.__setitem__(key, self.value_default)
                return self.value_default

    def __setitem__(self, key: Union[int, str], data: Any):
        self.__data[key] = data
        if self.encoder:
            data = self.encoder(data)
        self._redis.set(self._key(key), data, ex=self.et)
        self._check_size_limit()

    def __delitem__(self, key):
        if key in self.__data:
            del self.__data[key]
        self._redis.delete(self._key(key))

    def __contains__(self, key):
        return key in self.__data

    def __iter__(self):
        for key in self._redis.scan_iter(match=f"{self.kp}:*"):
            yield self.key_type(key[key.find(":") + 1:])

    def __repr__(self):
        return str([(k, v) for k, v in self.__data.items()])

    @property
    def local(self):
        return self.__data

    def _check_size_limit(self):
        if len(self.__data) > self.local_max:
            oldest_key = next(iter(self.__data))
            del self.__data[oldest_key]

    def refresh(self, key: Union[str, int]):
        data = self.__data.get(key)
        if data:
            self.__data.move_to_end(1, last=True)

            if self.encoder:
                data = self.encoder(data)
            self._redis.set(self._key(key), data, ex=self.et)

            self._check_size_limit()

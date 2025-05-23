import json
import redis
from typing import Any, Union, Optional, Literal, Callable, Iterator
from collections import OrderedDict


STRINT = Union[str, int]
KEY_TYPES = {"str", "int"}
VALUE_TYPES = {"str", "int", "json", "custom"}


class FlipCache:
    def __init__(
        self,
        name: str,
        *,
        local_max: int = 100,
        expire_time: Optional[int] = None,
        key_type: Literal["str", "int"] = "str",
        value_type: Literal["str", "int", "json", "custom"] = "str",
        value_default: Any = None,
        value_encoder: Optional[Callable] = None,
        value_decoder: Optional[Callable] = None,
        redis_protocol: redis.Redis = None,
        refresh_expire_time_on_get: bool = False,
    ) -> None:
        """
        FlipCache class

        :param name: Name of the cache, key prefix for redis
            If not specified keys will be used with redis without prefixes.
        :param local_max: Max number of elements to store in Python memory for fast retrieval.
            If not specified it will be 100 by default.
        :param expire_time: Expire time of a redis key.
            If not specified it will disable expiring keys.
        :param key_type: Data type of key, can be 'str' or 'int'. Defaults to 'str'
        :param value_type: Data type of value to be stored. Defaults to 'str'
            Possible options are 'str', 'int', 'json' or 'custom'
            When 'custom' is set, :param value_encoder and :param value_decoder must be passed
        :param value_encoder: Custom function used to encode the value before passing it to redis
        :param value_decoder: Custom function used to decode the value coming from redis
            Note: Getting stored value from redis, results in string data type, make sure to handle it properly
        :param value_default: Default value to be saved or returned if key not exists.
            Defaults to None
        :param redis_protocol: custom redis.Redis instance to be passed. Should have decode_responses=True
            If not specified new redis.Redis() instance will be created implicitly
        :raise AssertionError when:
            - specified key_type is not int or str
            - redis_protocol instance doesn't have decode_responses=True connection argument set
        """

        assert key_type in KEY_TYPES, "Invalid key_type, must be 'int' or 'str'"
        assert value_type in VALUE_TYPES, (
            "Invalid value_type, must be 'str', 'int', 'json' or 'custom'"
        )
        assert local_max is not None, "local_max cannot be None"

        if value_type == "custom":
            assert value_encoder and value_decoder, (
                "value_encoder and value_decoder must be passed when value_type "
                "set to 'custom'"
            )
            assert callable(value_encoder), "value_encoder must be a function"
            assert callable(value_decoder), "value_decoder must be a function"

        if isinstance(redis_protocol, redis.Redis):
            kwargs = redis_protocol.get_connection_kwargs()
            if value_type != "custom":
                assert kwargs.get("decode_responses", False), (
                    "Redis protocol with decode_responses=True must be passed when using non-custom value_type"
                )
            self._redis = redis_protocol
        else:
            self._redis = redis.Redis(decode_responses=True)

        self.__data = OrderedDict()
        self._lmax = local_max
        self._et = expire_time
        self._kp = name
        self._default = value_default
        self._refresh_et = refresh_expire_time_on_get

        self._kt = str
        if key_type == "int":
            self._kt = int

        self._encoder = str
        self._decoder = None

        if value_type == "json":
            self._encoder = json.dumps
            self._decoder = json.loads

        elif value_type == "int":
            self._encoder = None
            self._decoder = int

        elif value_type == "custom":
            self._encoder = value_encoder
            self._decoder = value_decoder

    def _key(self, name: STRINT) -> str:
        return f"{self._kp}:{name}"

    def __getitem__(self, key: STRINT) -> Any:
        if type(key) is not self._kt:
            key = self._kt(key)

        if key in self.__data:
            return self.__data[key]
        else:
            data = self._redis.get(self._key(key))

            if data:
                if self._decoder:
                    data = self._decoder(data)

                if len(self.__data) >= self._lmax:
                    self.__data[key] = data
                    self.__data.popitem(last=False)
                else:
                    self.__data[key] = data

                if self._et and self._refresh_et:
                    self._redis.expire(self._key(key), self._et)

                return data
            else:
                if self._default is not None:
                    self.__setitem__(key, self._default)
                return self._default

    def __setitem__(self, key: STRINT, data: Any) -> None:
        if type(key) is not self._kt:
            key = self._kt(key)

        self.__data[key] = data

        if self._encoder:
            data = self._encoder(data)
        self._redis.set(self._key(key), data, ex=self._et)
        self._check_size_limit()

    def __delitem__(self, key: STRINT) -> None:
        if type(key) is not self._kt:
            key = self._kt(key)

        if key in self.__data:
            del self.__data[key]
        self._redis.delete(self._key(key))

    def __contains__(self, key: STRINT) -> bool:
        if type(key) is not self._kt:
            key = self._kt(key)
        return key in self.__data or self._redis.exists(self._key(key))

    def __iter__(self) -> Iterator[STRINT]:
        for key in self._redis.scan_iter(match=f"{self._kp}:*"):
            yield self._kt(key[key.find(":") + 1 :])

    def __len__(self) -> int:
        count = 0
        cursor = 0
        while True:
            cursor, data = self._redis.scan(
                cursor=cursor, match=f"{self._kp}:*", count=100
            )
            count += len(data)
            if cursor == 0:
                break
        return count

    def __repr__(self) -> str:
        return (
            f"FlipCache<{self._kp}>("
            + str([(k, v) for k, v in self.__data.items()])
            + ")"
        )

    @property
    def local(self) -> OrderedDict:
        return self.__data

    def _check_size_limit(self) -> None:
        if len(self.__data) > self._lmax:
            self.__data.popitem(last=False)

    def refresh(self, key: STRINT) -> None:
        if key in self.__data:
            self.__data.move_to_end(key)

        if self._et:
            self._redis.expire(self._key(key), time=self._et)

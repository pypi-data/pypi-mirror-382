from __future__ import annotations
from typing import Any, Iterable, List, Mapping, Optional, TypeVar, Callable
import orjson
from redis.asyncio import Redis

T = TypeVar("T")

def _dumps(x: T) -> bytes:
    return orjson.dumps(x, option=orjson.OPT_NON_STR_KEYS)

def _loads(b: bytes) -> T:
    return orjson.loads(b)

class RedisKVTxn:
    def __init__(self, client: Redis):
        self.client = client
        self.pipe = None

    async def begin(self):
        self.pipe = self.client.pipeline(transaction=True)

    async def commit(self):
        if self.pipe is not None:
            await self.pipe.execute()
            self.pipe = None

    async def rollback(self):
        if self.pipe is not None:
            await self.pipe.reset()
            self.pipe = None

class RedisKV:
    """
    Async KV поверх Redis.
    - Хранит значения как JSON (orjson).
    - При наличии UoW можно работать через Redis pipeline (атомарно).
    """
    def __init__(self, redis: Redis, key_prefix: str = ""):
        self.r = redis
        self.key_prefix = key_prefix.rstrip(":")

    def _k(self, k: str) -> str:
        return f"{self.key_prefix}:{k}" if self.key_prefix else k

    async def get(self, key: str) -> Optional[T]:
        v = await self.r.get(self._k(key))
        return _loads(v) if v is not None else None

    async def mget(self, keys: Iterable[str]) -> List[Optional[T]]:
        ks = [self._k(k) for k in keys]
        vals = await self.r.mget(ks)
        return [_loads(v) if v is not None else None for v in vals]

    async def set(self, key: str, value: T, ttl_sec: Optional[int] = None, *, pipe: Optional[Redis] = None) -> None:
        client = pipe or self.r
        await client.set(self._k(key), _dumps(value), ex=ttl_sec)

    async def mset(self, items: Mapping[str, T], ttl_sec: Optional[int] = None, *, pipe: Optional[Redis] = None) -> None:
        client = pipe or self.r
        if ttl_sec is None:
            payload = {self._k(k): _dumps(v) for k, v in items.items()}
            await client.mset(payload)
        else:
            p = client.pipeline(transaction=False)
            for k, v in items.items():
                p.set(self._k(k), _dumps(v), ex=ttl_sec)
            await p.execute()

    async def delete(self, key: str, *, pipe: Optional[Redis] = None) -> None:
        client = pipe or self.r
        await client.delete(self._k(key))

    async def delete_many(self, keys: Iterable[str], *, pipe: Optional[Redis] = None) -> None:
        client = pipe or self.r
        ks = [self._k(k) for k in keys]
        if ks:
            await client.delete(*ks)

    async def all_keys(self, prefix: Optional[str] = None) -> List[str]:
        patt = self._k(prefix + "*") if prefix else (self._k("*") if self.key_prefix else "*")
        cursor = 0
        found: List[str] = []
        while True:
            cursor, batch = await self.r.scan(cursor=cursor, match=patt, count=1000)
            if not batch:
                if cursor == 0: break
                continue
            for k in batch:
                s = k.decode()
                if self.key_prefix and s.startswith(self.key_prefix + ":"):
                    s = s[len(self.key_prefix) + 1 :]
                found.append(s)
            if cursor == 0:
                break
        return found

    async def exists(self, key: str) -> bool:
        return (await self.r.exists(self._k(key))) == 1

    async def filter_new_keys(self, keys: Iterable[str]) -> List[str]:
        ks = list(keys)
        if not ks: return []
        p = self.r.pipeline(transaction=False)
        for k in ks:
            await p.exists(self._k(k))
        vals = await p.execute()
        return [k for k, ex in zip(ks, vals) if ex == 0]

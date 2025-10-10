from __future__ import annotations

import json
from typing import Optional, Any, List

from ._base import StateProvider

try:
    import redis.asyncio as redis
except ImportError:
    redis = None

# only acquire the lock if it is not held by another client
# if it is held by the same client, renew the lock
# keys[1] = lock key
# argv[1] = client_id
# argv[2] = timeout (secs)
ACQUIRE_LOCK_SCRIPT = """
if redis.call("set", KEYS[1], ARGV[1], "NX", "EX", ARGV[2]) then
    return 1
end
if redis.call("get", KEYS[1]) == ARGV[1] then
    return redis.call("expire", KEYS[1], ARGV[2])
else
    return 0
end"""

# only release the lock if it is held by the same client
# keys[1] = lock key
# argv[1] = client_id
RELEASE_LOCK_SCRIPT = """
if redis.call("get", KEYS[1]) == ARGV[1] then
    return redis.call("del", KEYS[1])
else
    return 0
end"""

# return the number of keys matching the given pattern
# argv[1] = pattern
COUNT_KEYS_SCRIPT = """
local keys = redis.call("keys", ARGV[1])
return #keys"""

# return the keys matching the given pattern that has a value greater than or equal to the threshold
# argv[1] = pattern
# argv[2] = threshold
KEYS_VALUE_GTE_SCRIPT = """
local result = {}
local pattern = ARGV[1]
local threshold = tonumber(ARGV[2])
for _, k in ipairs(redis.call("KEYS", pattern)) do
  local v = tonumber(redis.call("GET", k))
  if v and v >= threshold then
    table.insert(result, k)
  end
end
return res"""

# delete all keys matching the given pattern
# argv[1] = pattern
DELETE_KEYS_SCRIPT = """
local keys = redis.call("keys", ARGV[1])
for _, key in ipairs(keys) do
    redis.call("del", key)
end
return #keys"""


class RedisStateProvider(StateProvider):
    def __init__(self, connection: dict, prefix: str):
        if redis is None:
            raise ImportError("redis client library is not installed")

        self._client = None
        self._client_connection_params = connection
        self.prefix = prefix
        if self.prefix:
            self.prefix += ':'
        self.session_expiry = 600

    async def _get_client(self) -> redis.StrictRedis:
        if self._client is None:
            self._client = redis.StrictRedis(**self._client_connection_params)
        return self._client

    async def acquire_lock(self, lock_name: str, client_id: str, timeout: int = 10) -> bool:
        client = await self._get_client()
        key = self._lock_key(lock_name)
        return bool(await client.eval(ACQUIRE_LOCK_SCRIPT, 1, key, client_id, str(timeout)))

    async def release_lock(self, lock_name: str, client_id: str):
        client = await self._get_client()
        key = self._lock_key(lock_name)
        await client.eval(RELEASE_LOCK_SCRIPT, 1, key, client_id)

    async def allocate_container(self, container_id: str, session_id: str):
        client = await self._get_client()
        key = self._container_allocation_key(container_id, session_id)
        await client.set(key, 1, ex=self.session_expiry)
        key = self._container_uses_key(container_id)
        await client.incr(key)

    async def renew_container(self, container_id: str, session_id: str):
        client = await self._get_client()
        key = self._container_allocation_key(container_id, session_id)
        await client.expire(key, self.session_expiry)

    async def container_is_allocated(self, container_id: str) -> bool:
        return await self.container_current_uses(container_id) > 0

    async def container_current_uses(self, container_id: str) -> int:
        client = await self._get_client()
        key_prefix = self._container_allocation_key_prefix(container_id)
        return int(await client.eval(COUNT_KEYS_SCRIPT, 0, f'{key_prefix}*'))

    async def container_total_uses(self, container_id: str) -> int:
        client = await self._get_client()
        key = self._container_uses_key(container_id)
        return int(await client.get(key) or 0)

    async def containers_total_uses_gte(self, threshold: int) -> List[str]:
        client = await self._get_client()
        key_pattern = self._container_uses_key('*')
        return [
            key.split(':')[-2]
            for key in await client.eval(KEYS_VALUE_GTE_SCRIPT, 0, key_pattern, str(threshold))
        ]

    async def release_container(self, container_id: str, session_id: str):
        client = await self._get_client()
        key = self._container_allocation_key(container_id, session_id)
        await client.delete(key)

    async def remove_container(self, container_id: str):
        client = await self._get_client()
        key_prefix = self._container_key_prefix(container_id)
        await client.eval(DELETE_KEYS_SCRIPT, 0, f'{key_prefix}*')

    async def store_session(self, session_id: str, data: Any):
        client = await self._get_client()
        await client.set(self._session_key(session_id), json.dumps(data), ex=self.session_expiry)

    async def get_session(self, session_id: str) -> Optional[Any]:
        client = await self._get_client()
        try:
            return json.loads(await client.get(self._session_key(session_id)))
        except:
            return None

    async def renew_session(self, session_id: str):
        client = await self._get_client()
        await client.expire(self._session_key(session_id), self.session_expiry)

    async def delete_session(self, session_id: str):
        client = await self._get_client()
        await client.delete(self._session_key(session_id))

    def _lock_key(self, lock_name: str) -> str:
        return f'{self.prefix}lock:{lock_name}'

    def _container_key_prefix(self, container_id: str) -> str:
        return f'{self.prefix}container:{container_id}:'

    def _container_allocation_key_prefix(self, container_id: str) -> str:
        return f'{self._container_key_prefix(container_id)}allocation:'

    def _container_allocation_key(self, container_id: str, session_id: str) -> str:
        return f'{self._container_allocation_key_prefix(container_id)}{session_id}'

    def _container_uses_key(self, container_id: str) -> str:
        return f'{self._container_key_prefix(container_id)}uses'

    def _session_key(self, session_id: str) -> str:
        return f'{self.prefix}session:{session_id}'

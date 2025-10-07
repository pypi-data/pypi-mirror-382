import logging
import threading
from functools import cached_property
from pathlib import Path
from typing import Literal, ClassVar

from redis import Redis
from redis.commands.core import Script

from .._path import PACKAGE_DIR

logger = logging.getLogger("circuit.redis")


class LuaScriptError(Exception): ...


class RedisClient:
    _clients: ClassVar[dict[tuple[str, float | None], Redis]] = {}
    _lock: ClassVar[threading.Lock] = threading.Lock()

    @classmethod
    def get_client(cls, redis_url: str, socket_timeout: float | None = 2.0) -> Redis:
        key = (redis_url, socket_timeout)
        with cls._lock:
            client = cls._clients.get(key)
            if client is None:
                client = Redis.from_url(
                    redis_url,
                    decode_responses=True,
                    socket_timeout=socket_timeout,
                    retry_on_timeout=True,
                )
                cls._clients[key] = client
            return client

    @classmethod
    def close_client(cls, redis_url: str, socket_timeout: float | None = 2.0) -> None:
        key = (redis_url, socket_timeout)
        with cls._lock:
            client = cls._clients.pop(key, None)
        if client:
            try:
                client.close()
            except Exception:
                logger.exception("Failed to close Redis client.")

    @classmethod
    def close_all(cls) -> None:
        with cls._lock:
            clients = list(cls._clients.values())
            cls._clients.clear()
        for c in clients:
            try:
                c.close()
            except Exception:
                logger.exception("Failed to close Redis client.")


class LuaScriptLoader:
    def __init__(self, redis: Redis | None = None):
        self._redis = redis
        self._sha_cache: dict[str, str] = {}
        self._sha_size_cache: dict[str, int] = {}

    def attach_redis(self, redis: Redis) -> None:
        self._redis = redis

    def load(
        self, script_name: str, retval: Literal["sha", "contents"] = "contents"
    ) -> Script | str:
        if retval == "contents":
            return self._load_from_disk(script_name)

        if not isinstance(self._redis, Redis):
            raise LuaScriptError(
                f"Cannot return SHA for {script_name!r}: loader has no attached Redis client."
            )

        lua_file = self._lua_file_path(script_name)
        try:
            size = lua_file.stat().st_size
        except Exception as exc:
            raise LuaScriptError(
                f"Failed to stat LUA script {str(lua_file)!r}: {exc}"
            ) from exc

        cached_sha = self._sha_cache.get(script_name)

        cached_size = self._sha_size_cache.get(script_name)

        if cached_sha is not None and cached_size == size:
            return cached_sha

        try:
            contents = lua_file.read_text(encoding="utf-8")
        except Exception as exc:
            raise LuaScriptError(
                f"Failed to read LUA script {str(lua_file)!r}: {exc}"
            ) from exc

        try:
            sha = self._redis.script_load(contents)
            self._sha_cache[script_name] = sha  # type: ignore
            self._sha_size_cache[script_name] = size
            return sha  # type: ignore
        except Exception as exc:
            raise LuaScriptError(
                f"Failed to load script {script_name!r} into Redis: {exc}"
            ) from exc

    def _load_from_disk(self, script_name: str) -> str:
        lua_file = self._lua_file_path(script_name)
        try:
            return lua_file.read_text(encoding="utf-8")
        except Exception as exc:
            raise LuaScriptError(
                f"Failed to read LUA script {str(lua_file)!r}: {exc}"
            ) from exc

    def _lua_file_path(self, script_name: str) -> Path:
        if not script_name.lower().endswith(".lua"):
            script_name = f"{script_name}.lua"

        lua_file = self._lua_dir.joinpath(script_name)

        if not lua_file.exists():
            raise LuaScriptError(f"LUA script file {str(lua_file)!r} does not exist.")

        return lua_file

    @cached_property
    def _lua_dir(self) -> Path:
        return PACKAGE_DIR.joinpath("storage", "lua")

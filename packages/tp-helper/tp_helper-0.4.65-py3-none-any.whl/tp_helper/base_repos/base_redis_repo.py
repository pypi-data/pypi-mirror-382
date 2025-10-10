from __future__ import annotations

from typing import Any, TypeVar

from pydantic import BaseModel, TypeAdapter

T = TypeVar("T", bound=BaseModel)


class BaseRedisRepo:
    def __init__(self, redis):
        self.redis = redis

    async def get(self, key: str) -> str | None:
        val = await self.redis.get(key)
        if val is None:
            return None
        if isinstance(val, bytes):
            return val.decode("utf-8")
        return str(val)

    async def set(self, key: str, value: str, *, ex: int | None = None) -> None:
        await self.redis.set(key, value, ex=ex)

    async def set_model(self, key: str, model: T, *, ex: int | None = None) -> None:
        await self.set(key, model.model_dump_json(), ex=ex)

    async def get_model(self, key: str, schema: type[T]) -> T | None:
        raw = await self.get(key)
        if raw is None:
            return None
        return TypeAdapter(schema).validate_json(raw)

    async def set_models(
        self, key: str, models: list[T], *, ex: int | None = None
    ) -> None:
        payload = "[" + ",".join(m.model_dump_json() for m in models) + "]"
        await self.set(key, payload, ex=ex)

    async def get_models(self, key: str, schema: type[T]) -> list[T] | None:
        raw = await self.get(key)
        if raw is None:
            return None
        adapter = TypeAdapter(list[schema])
        return adapter.validate_json(raw)

    async def get_all_data(
        self,
        pattern: str = "*", # Паттерн для ключа (* - что угодно)
        count: int = 200,  # сколько ключей за один SCAN-чанк
        max_keys: (
            int | None
        ) = None,  # общий лимит по количеству ключей
        list_limit: int = 100,  # сколько элементов читать из списка/стрима
        zset_limit: int = 100,  # сколько элементов читать из сорт. множества
        set_limit: int = 100,  # сколько элементов читать из множества
        hash_limit: int = 200,  # сколько пар читать из хэша
    ) -> dict[str, dict[str, Any]]:
        """
        Возвращает словарь:
        {
          "<key>": {
             "type": "<string|list|set|zset|hash|stream|none>",
             "value": <значение или сэмпл значения>,
             "truncated": bool  # обрезано ли по лимиту
          },
          ...
        }
        """
        result: dict[str, dict[str, Any]] = {}
        cursor = 0
        fetched = 0

        while True:
            cursor, batch = await self.redis.scan(
                cursor=cursor, match=pattern, count=count
            )

            for key in batch:
                key_str = (
                    key.decode("utf-8")
                    if isinstance(key, bytes | bytearray)
                    else str(key)
                )

                try:
                    ktype = await self.redis.type(
                        key_str
                    )
                    ktype = (
                        ktype.decode()
                        if isinstance(ktype, bytes | bytearray)
                        else str(ktype)
                    )
                except Exception as e:
                    result[key_str] = {
                        "type": "unknown",
                        "value": f"<type error: {e}>",
                        "truncated": False,
                    }
                    continue

                try:
                    if ktype == "string":
                        val = await self.get(key_str)
                        result[key_str] = {
                            "type": "string",
                            "value": val,
                            "truncated": False,
                        }

                    elif ktype == "list":
                        items = await self.redis.lrange(key_str, 0, list_limit - 1)
                        items = [
                            i.decode() if isinstance(i, bytes | bytearray) else i
                            for i in items
                        ]
                        size = await self.redis.llen(key_str)
                        result[key_str] = {
                            "type": "list",
                            "value": items,
                            "truncated": size > len(items),
                        }

                    elif ktype == "set":
                        members = await self.redis.smembers(key_str)
                        members = [
                            m.decode() if isinstance(m, bytes | bytearray) else m
                            for m in list(members)[:set_limit]
                        ]
                        truncated = len(members) >= set_limit
                        result[key_str] = {
                            "type": "set",
                            "value": members,
                            "truncated": truncated,
                        }

                    elif ktype == "zset":
                        items = await self.redis.zrange(
                            key_str, 0, zset_limit - 1, withscores=True
                        )
                        norm = []
                        for member, score in items:
                            member = (
                                member.decode()
                                if isinstance(member, bytes | bytearray)
                                else member
                            )
                            norm.append({"member": member, "score": score})
                        total = await self.redis.zcard(key_str)
                        result[key_str] = {
                            "type": "zset",
                            "value": norm,
                            "truncated": total > len(norm),
                        }

                    elif ktype == "hash":
                        hcursor = 0
                        collected = {}
                        truncated = False
                        while True:
                            hcursor, hbatch = await self.redis.hscan(
                                key_str, cursor=hcursor, count=hash_limit
                            )
                            for field, val in hbatch.items():
                                fs = (
                                    field.decode()
                                    if isinstance(field, bytes | bytearray)
                                    else str(field)
                                )
                                vs = (
                                    val.decode()
                                    if isinstance(val, bytes | bytearray)
                                    else val
                                )
                                collected[fs] = vs
                                if len(collected) >= hash_limit:
                                    truncated = True
                                    break
                            if hcursor == 0 or truncated:
                                break
                        result[key_str] = {
                            "type": "hash",
                            "value": collected,
                            "truncated": truncated,
                        }

                    elif ktype == "stream":
                        entries = await self.redis.xrange(
                            key_str, min="-", max="+", count=list_limit
                        )
                        norm_entries = []
                        for entry_id, data in entries:
                            entry_id = (
                                entry_id.decode()
                                if isinstance(entry_id, bytes | bytearray)
                                else entry_id
                            )
                            norm = {}
                            for f, v in data.items():
                                fs = (
                                    f.decode()
                                    if isinstance(f, bytes | bytearray)
                                    else f
                                )
                                vs = (
                                    v.decode()
                                    if isinstance(v, bytes | bytearray)
                                    else v
                                )
                                norm[fs] = vs
                            norm_entries.append({"id": entry_id, "data": norm})
                        truncated = len(norm_entries) >= list_limit
                        result[key_str] = {
                            "type": "stream",
                            "value": norm_entries,
                            "truncated": truncated,
                        }

                    elif ktype == "none":
                        result[key_str] = {
                            "type": "none",
                            "value": None,
                            "truncated": False,
                        }

                    else:
                        result[key_str] = {
                            "type": ktype,
                            "value": "<unsupported type>",
                            "truncated": False,
                        }

                except Exception as e:
                    result[key_str] = {
                        "type": ktype,
                        "value": f"<read error: {e}>",
                        "truncated": False,
                    }

                fetched += 1
                if max_keys is not None and fetched >= max_keys:
                    return result

            if cursor == 0:
                break

        return result

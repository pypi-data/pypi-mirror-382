from redis.asyncio import Redis

# Для LIFO (первым пришел, последним ушел) можно оставаться с LPUSH + BRPOP.
# Для FIFO (первым пришел, первым ушел) предпочтительнее использовать RPUSH + BLPOP,


class BaseQueueRepo:
    # Имя очереди в Redis (ключ). Должно быть переопределено в наследниках.
    QUEUE_NAME = ""

    def __init__(self, redis_client: Redis):
        # Клиент Redis для работы с очередью
        self.redis_client = redis_client

    async def count(self) -> int:
        """
        Возвращает количество элементов в очереди (LLEN).
        """
        return await self.redis_client.llen(self.QUEUE_NAME)

    async def delete(self) -> int:
        """
        Полностью удаляет ключ очереди (DEL).
        Возвращает количество удалённых ключей (0 или 1).
        """
        return await self.redis_client.delete(self.QUEUE_NAME)

    async def unlink(self) -> int:
        """
        Асинхронно удаляет ключ очереди (UNLINK).
        В отличие от DEL, не блокирует Redis при больших ключах.
        Возвращает количество удалённых ключей (0 или 1).
        """
        return await self.redis_client.unlink(self.QUEUE_NAME)

    async def unlink_by_pattern(self, pattern: str) -> int:
        """
        Удаляет все ключи в Redis, подходящие под шаблон.
        Например: pattern="tasks*" или "routes:*".
        Возвращает количество удалённых ключей.
        """
        deleted = 0
        async for key in self.redis_client.scan_iter(match=pattern):
            deleted += await self.redis_client.unlink(key)
        return deleted

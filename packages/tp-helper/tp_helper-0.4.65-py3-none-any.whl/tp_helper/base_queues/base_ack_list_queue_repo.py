from typing import Type, TypeVar, Generic
from pydantic import BaseModel
from redis.asyncio import Redis
from tp_helper.base_queues.base_queue_repo import BaseQueueRepo

messageType = TypeVar("messageType", bound=BaseModel)

class BaseAckListQueueRepo(Generic[messageType], BaseQueueRepo):
    """
    Универсальный репозиторий очереди с поддержкой подтверждения (ack) для Redis.

    Хранит данные в виде JSON-строк и обеспечивает:
    - Защиту от дублирующих записей
    - Временное извлечение элемента (до ack)
    - Явное подтверждение обработки через метод ack()

    Примеры применения:
        Гарантированная доставка сообщений между сервисами.

        Обработка критичных задач, где потеря недопустима.

        Очереди с подтверждением выполнения (ack) после успешной обработки.

        Интеграция с внешними системами, где требуется надёжная доставка.

        Механизм повторной обработки задач при сбое.

        Использование в микросервисной архитектуре, где важна точная доставка и согласованность.

    :param redis_client: Экземпляр асинхронного Redis-клиента.
    :param message_type: Класс сообщения, которое будет сериализовано и проверено.
    """

    def __init__(self, redis_client: Redis, message_type: Type[messageType]):
        super().__init__(redis_client)
        self.redis_client = redis_client
        self.message_type = message_type

    async def add_bulk(self, messages: list[messageType], queue: str = None) -> None:
        """
        Добавляет несколько объектов в очередь разом, исключая уже существующие.
        """
        queue_name = queue or self.QUEUE_NAME
        json_items = [message.model_dump_json() for message in messages]  # Используем model_dump_json() для сериализации

        in_queue = await self.redis_client.lrange(queue_name, 0, -1)
        json_items = [item for item in json_items if item not in in_queue]

        await self.redis_client.rpush(queue_name, *json_items)

    async def add(self, message: messageType, queue: str = None) -> None:
        """
        Добавляет объект в очередь, если такого ещё нет (по JSON-сравнению).
        """
        queue_name = queue or self.QUEUE_NAME
        json_item = message.model_dump_json()  # Используем model_dump_json() для сериализации

        in_queue = await self.redis_client.lrange(queue_name, 0, -1)
        if json_item in in_queue:
            return
        await self.redis_client.rpush(queue_name, json_item)

    async def pop(self, timeout: int = 0, queue: str = None) -> messageType | None:
        """
        Блокирующе извлекает первый элемент из очереди и возвращает его обратно в очередь.

        Используется совместно с ack(): pop() временно извлекает, ack() — подтверждает.
        """
        queue_name = queue or self.QUEUE_NAME
        result = await self.redis_client.blpop([queue_name], timeout=timeout)

        if result is None:
            return None
        _, raw = result
        await self.redis_client.lpush(queue_name, raw)
        return self._validate(raw)

    async def ack(self, queue: str = None) -> None:
        """
        Подтверждает получение элемента, удаляя его окончательно из очереди.
        """
        queue_name = queue or self.QUEUE_NAME
        await self.redis_client.lpop(queue_name)

    async def delete(self, queue: str = None) -> None:
        """
        Удаляет всю очередь для конкретного task_id.
        """
        queue_name = queue or self.QUEUE_NAME
        await self.redis_client.delete(queue_name)

    async def unlink(self, queue: str = None) -> None:
        """
        Этот метод удаляет ключ синхронно, что может привести к блокировке других операций,
        если ключ имеет большие данные. Используется для немедленного удаления ключа.
        """
        queue_name = queue or self.QUEUE_NAME
        await self.redis_client.unlink(queue_name)

    def _validate(self, raw: str) -> messageType:
        """
        Метод освобождает память асинхронно, не блокируя выполнение других команд Redis. Это полезно,
        когда необходимо удалить большие данные или ключи, не влияя на производительность других операций.
        """
        return self.message_type.model_validate_json(raw)

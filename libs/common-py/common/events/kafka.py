# libs/common-py/common/events/kafka.py
# Stubs de productor/consumidor; se implementarán luego.
class EventPublisher:
    async def publish(self, topic: str, payload: dict): ...

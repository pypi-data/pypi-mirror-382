import json
import logging
from asyncio import Lock
from typing import AsyncIterable, Dict, List, Optional, Tuple

from aiokafka import AIOKafkaConsumer, AIOKafkaProducer, ConsumerRebalanceListener
from aiokafka.coordinator.assignors.sticky.sticky_assignor import StickyPartitionAssignor
from aiokafka.errors import CommitFailedError

from .channel import Channel

__all__ = ["KafkaChannel"]

logger = logging.getLogger(__name__)


class RebalanceListener(ConsumerRebalanceListener):
    def __init__(self, topic: str, rebalance_lock: Lock):
        super().__init__()
        self._topic = topic
        self._rebalance_lock = rebalance_lock

    async def on_partitions_revoked(self, revoked: List) -> None:
        # keeps kafka from rebalancing while we are processing a message
        logger.info(
            f"Finish processing current message on topic {self._topic} before partitions are "
            f"revoked..."
        )
        async with self._rebalance_lock:
            pass
        logger.info(
            f"Message on topic {self._topic} was processed and partitions can be revoked now."
        )

    async def on_partitions_assigned(self, assigned: List) -> None:
        pass


class KafkaChannel(Channel):
    def __init__(self, broker_url: str) -> None:
        super().__init__()
        self._broker_url = broker_url
        self._consumers: Dict[Tuple[str, str], AIOKafkaConsumer] = {}
        self._kafka_lock = Lock()
        self._rebalance_locks: Dict[Tuple[str, str], Lock] = {}

    async def _start(self) -> None:
        self._producer = AIOKafkaProducer(
            bootstrap_servers=[self._broker_url],
        )
        logger.info(f"Connecting to Kafka broker {self._broker_url} and starting a producer...")
        await self._producer.start()

        for consumer in self._consumers.values():
            await consumer.start()

    async def _stop(self) -> None:
        logger.info("Waiting for all consumers to finish...")
        for _, rebalance_lock in self._rebalance_locks.items():
            async with rebalance_lock:
                pass

        logger.info("Stopping all consumers...")
        for consumer in self._consumers.values():
            await consumer.stop()

        await self._producer.stop()

    async def _iter_messages(
        self, topic: str, consumer_group: str, batch_size: int = 1
    ) -> AsyncIterable[List[Tuple[Optional[tuple], Optional[dict]]]]:
        consumer_key = (topic, consumer_group)

        if consumer_key not in self._rebalance_locks:
            self._rebalance_locks[consumer_key] = Lock()
        rebalance_lock = self._rebalance_locks[consumer_key]

        if consumer_key not in self._consumers:
            # make sure that only one consumer is created at a time
            async with self._kafka_lock:
                # create consumer
                consumer = AIOKafkaConsumer(
                    bootstrap_servers=[self._broker_url],
                    auto_offset_reset="earliest",
                    group_id=consumer_group,
                    enable_auto_commit=False,
                    # consume only one message at a time
                    max_poll_records=batch_size,
                    # max_poll_interval_ms: Time between polls (in milliseconds) before the consumer
                    # is considered dead. Prediction tasks can take a long time, so we set this to 1
                    # hour.
                    max_poll_interval_ms=60 * 60 * 1000,
                    # session_timeout_ms: The timeout used to detect failures when using Kafka's
                    # group management. We set this to 1 minute.
                    session_timeout_ms=60_000,
                    # heartbeat_interval_ms: The expected time between heartbeats to the consumer
                    # coordinator when using Kafka's group management facilities. The recommended
                    # value is 1/3 of session_timeout_ms, so we set this to 20 seconds.
                    heartbeat_interval_ms=20_000,
                    # use cooperative sticky assignor to avoid being kicked out of the group during
                    # rebalances (-> decreases probability to interrupt long-running tasks)
                    partition_assignment_strategy=(StickyPartitionAssignor,),
                )

                consumer.subscribe(
                    [topic],
                    listener=RebalanceListener(topic, rebalance_lock),
                )

                logger.info(
                    f"Connecting to Kafka broker {self._broker_url} and starting a consumer on "
                    f"topic {topic}."
                )
                await consumer.start()
                self._consumers[consumer_key] = consumer
                logger.info(f"Consumer started on topic {topic}.")

        consumer = self._consumers[consumer_key]

        # main loop
        try:
            while True:
                if not self.is_running:
                    logger.info(f"Shutdown event set {topic}, stopping consumer...")
                    break

                # use timeout of 500ms (default value of the async iterator of AIOKafkaConsumer)
                batch = await consumer.getmany(timeout_ms=500)

                # this lock ensures that rebalancing does not destroy progress
                async with rebalance_lock:
                    key_value_pairs = []
                    for _, messages in batch.items():
                        for message in messages:
                            if message.key is None:
                                key = None
                            else:
                                try:
                                    message_key: list = json.loads(message.key)
                                except json.JSONDecodeError:
                                    # if we can't decode the key as JSON, we assume it is a string
                                    message_key = [message.key.decode("utf-8")]
                                key = tuple(message_key)

                            # distinguish tombstoned records by checking if value is None
                            if message.value is None:
                                value = None
                            else:
                                value = json.loads(message.value)

                            key_value_pairs.append((key, value))

                    if len(key_value_pairs) == 0:
                        continue

                    try:
                        yield key_value_pairs
                    except Exception:
                        logger.error("Error while yielding messages", exc_info=True)
                        # do not commit the message, but retry
                        continue

                    try:
                        await consumer.commit()
                    except CommitFailedError as e:
                        logger.error("Commit failed, trying again.", exc_info=e)
        finally:
            try:
                await consumer.stop()
            except Exception:
                logger.error("Error while stopping consumer", exc_info=True)
            finally:
                self._consumers.pop(consumer_key, None)

    async def _send(self, topic: str, key: Optional[tuple], value: Optional[dict]) -> None:
        if key is None:
            message_key = None
        else:
            message_key = json.dumps(key).encode("utf-8")

        # fetch value
        if value is None:
            message_value = None
        else:
            message_value = json.dumps(value).encode("utf-8")

        await self._producer.send_and_wait(topic, value=message_value, key=message_key)

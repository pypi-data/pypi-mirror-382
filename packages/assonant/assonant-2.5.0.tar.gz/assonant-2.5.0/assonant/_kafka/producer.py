"""Implementation of both synchronous and asynchronous message Kafka producer.

See Also:
    https://www.confluent.io/blog/kafka-python-asyncio-integration/
"""
import asyncio
from threading import Thread
from typing import Callable

import confluent_kafka
from confluent_kafka import KafkaException, Message


class Producer:
    """A Multithreading Kafka producer."""

    def __init__(self, configs):
        """Class constructor method.

        Args:
            configs (dict): A dictionary that contains overall kafka cluster configurations.
        """
        self._producer = confluent_kafka.Producer(configs)
        self._cancelled = False
        self._poll_thread = Thread(target=self._poll_loop)
        self._poll_thread.start()

    def _poll_loop(self):
        """Polls the producer for events and calls the corresponding callbacks (if registered)."""
        while not self._cancelled:
            self._producer.poll(0.1)

    def close(self):
        """Wait until all threads terminates.

        This blocks the calling thread until the thread whose join() method is called terminates.
        """
        self._cancelled = True
        self._poll_thread.join()

    def produce(self, topic: str, value: dict, key: str = None, on_delivery: Callable = None):
        """A waitable produce method.

        Initiate sending a message to Kafka, passing in the message value and optionally a key,
        partition, and callback.

        Args:
            topic (str): The name of a topic where the producer will send the message.
            value (dict): Payload of the message.
            key (str): Used to determine the partition within a log to which a message get's appended to.
            on_delivery (Callable, optional): TODO _description_. Defaults to None.
        """
        self._producer.produce(topic, value, on_delivery=on_delivery)


class AsyncProducer:
    """An Awaiting Multithreading Kafka producer."""

    def __init__(self, configs: dict, loop: Callable = None):
        """Class constructor method.

        Args:
            Args:
            configs (dict): A dictionary that contains overall kafka cluster configurations.
            loop (Callable, optional):  A running event loop. Defaults to None.
        """
        self._loop = loop or asyncio.get_event_loop()
        self._producer = confluent_kafka.Producer(configs)
        self._cancelled = False
        self._poll_thread = Thread(target=self._poll_loop)
        self._poll_thread.start()

    def _poll_loop(self):
        """Polls the producer for events and calls the corresponding callbacks (if registered)."""
        while not self._cancelled:
            self._producer.poll(0.1)

    def close(self):
        """Wait until all threads terminates.

        This blocks the calling thread until the thread whose join() method is called terminates.
        """
        self._cancelled = True
        self._poll_thread.join()

    def produce(self, topic: str, value: dict, key: str = None):
        """An awaitable produce method.

        Initiate sending a message to Kafka, passing in the message value and optionally a key,
        partition, and callback.

        Args:
            topic (str): The name of a topic where the producer will send the message.
            value (dict): Payload of the message.
            key (str): Used to determine the partition within a log to which a message get's appended to.

        Returns:
            TODO _type_: TODO _description_
        """
        result = self._loop.create_future()

        def ack(err: str, msg: Message):
            """Delivery report callback to call (from poll() or flush()) on successful or failed delivery.

            A function reference that is called once for each produced message to indicate the final delivery
            result (success or failure).

            Args:
                err (str): Kafka error message.
                msg (Message): The Message object represents either a single consumed or produced message, or an event.
            """
            if err:
                self._loop.call_soon_threadsafe(result.set_exception, KafkaException(err))
            else:
                self._loop.call_soon_threadsafe(result.set_result, msg)

        self._producer.produce(topic, value, on_delivery=ack)
        return result

    def produce_with_delivery(self, topic: str, value: dict, on_delivery: Callable):
        """A produce method with delivery notifications.

        A produce method in which delivery notifications are made available via both the returned
        future and on_delivery callback (if specified).

        Args:
            topic (str): The name of a topic where the producer will send the message.
            value (dict): Payload of the message.
            on_delivery (Callable): Delivery report callback called on successful or failed delivery of message.

        Returns:
            TODO _type_: TODO _description_
        """
        result = self._loop.create_future()

        def ack(err: str, msg: Message):
            """Delivery report callback to call (from poll() or flush()) on successful or failed delivery.

            A function reference that is called once for each produced message to indicate the final delivery
            result (success or failure).

            Args:
                err (str): Kafka error message.
                msg (Message): The Message object represents either a single consumed or produced message, or an event.
            """
            if err:
                self._loop.call_soon_threadsafe(result.set_exception, KafkaException(err))
            else:
                self._loop.call_soon_threadsafe(result.set_result, msg)
            if on_delivery:
                self._loop.call_soon_threadsafe(on_delivery, err, msg)

        self._producer.produce(topic, value, on_delivery=ack)
        return result

from typing import Union

from assonant._kafka.producer import Producer
from assonant.data_classes import AssonantDataClass
from assonant.data_classes.events import AssonantEvent

from ._assonant_data_sender_interface import IAssonantDataSender
from .exceptions import AssonantDataSenderError


class KafkaDataSender(IAssonantDataSender):
    """Kafka Data Sender.

    Data sender specialized on sending AssonantDataClasses over a Kafka
    data broker
    """

    def __init__(self, configs: dict):
        self._parse_configs(configs)
        producer_configs = self._mount_producer_configs_dict()
        self.producer = Producer(configs=producer_configs)

    def send_data(self, payload: Union[AssonantDataClass, AssonantEvent]):
        """Method for sending data through a Kafka topic.

        Args:
            payload (Union[AssonantDataClass, AssonantEvent]): AssonantDataClass or AssonantEvent
            that will be send.
        """
        # Serialize payload as json and send it over topic
        self.producer.produce(topic=self.topic, value=payload.json())
        self._close()

    def _close(self):
        """Close Kafka Producer instance."""
        self.producer.close()

    def _parse_configs(self, configs: dict) -> None:
        """Parse configuration dictionary to extract configuration settings from it.

        Parsed data should be set to class properties, not returned by the method.

        Args:
            configs (dict): Dictionary containing configuration settings which will be parsed.
        """
        self._validade_configs(configs)

        self.server = configs["server"]
        self.topic = configs["topic"]

    def _validade_configs(self, configs: dict) -> None:
        """Validate if all mandatory configurations were passed in the configuration.

        Args:
            configs (dict): Dictionary containing configuration settings which will be parsed.

        Raises:
            AssonantDataSenderError: Mandatory field is missing in configuration data.
        """
        if "server" not in configs.keys():
            raise AssonantDataSenderError("Mandatory field 'server' missing on " "config data!")
        elif "topic" not in configs.keys():
            raise AssonantDataSenderError("Mandatory field 'topic' missing on " "config data!")

    def _mount_producer_configs_dict(self) -> dict:
        """Format configuration settings to specific format Kafka Producer expects.

        Returns:
            dict: Formatted configuration dictionary.
        """
        kafka_configs = {}
        kafka_configs["bootstrap.servers"] = self.server

        return kafka_configs

from typing import List

from ._assonant_data_sender_interface import IAssonantDataSender
from ._kafka_data_sender import KafkaDataSender
from .exceptions import AssonantDataSenderError


class DataSenderFactory:
    """Data Sender Factory.

    Class that implements the factory design pattern
    (https://refactoring.guru/design-patterns/factory-method) to fully abstract
    the procedure of creating Assonant Data senders
    """

    _supported_comm_methods = ["kafka"]

    def create_data_sender(self, comm_method: str, configs: dict) -> IAssonantDataSender:
        """Public method that abstracts data sender creation process for the factory user.

        Internally, this method deals with validation and specific Data Sender
        creation

        Args:
            comm_method (str): Communication method used by the Data Sender that
            will be created.
            configs (dict): Dictionary containing all configuration settings
            from the specific Data Sender that will created. Different
            communication methods may require different settings and fields.

        Raises:
            AssonantDataSenderError: An error occured during the creation of
            the respective Data Sender.

        Returns:
            IAssonantDataSender: Data Sender instance which implements the
            IAssonantDataSender interface
        """
        self._validate_comm_method(comm_method)

        if comm_method == "kafka":
            return self._create_kafka_data_sender(configs)
        raise AssonantDataSenderError(
            f"'{comm_method}' communication method is set as supported but its creation method is not implemented."
        )

    def _create_kafka_data_sender(self, configs: dict) -> KafkaDataSender:
        return KafkaDataSender(configs)

    def _validate_comm_method(self, comm_method: str) -> None:
        """Validate if passed communication method is currently supported.

        Args:
            comm_method (str): Communication method to be validated

        Raises:
            AssonantDataSenderError: Communication method not supported.
        """
        if comm_method not in self._supported_comm_methods:
            raise AssonantDataSenderError(
                f"'{comm_method}' communication method isn't currently supported. "
                f"The supported methods are: {self._supported_comm_methods}"
            )

    def get_supported_comm_methods(self) -> List[str]:
        """Getter method for current supported communication methods.

        Returns:
            List[str]: List containing curretly supported communication methods.
        """
        return self._supported_comm_methods

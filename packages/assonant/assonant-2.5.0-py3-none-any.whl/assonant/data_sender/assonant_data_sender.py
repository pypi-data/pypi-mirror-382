"""Assonant class to handle AssonantDataClasses transference over any communication method."""

from typing import Any, List

from ._assonant_data_sender_interface import IAssonantDataSender
from ._data_sender_factory import DataSenderFactory


class AssonantDataSender(IAssonantDataSender):
    """Assonant Data Sender. Wrapper class to deal with AssonantDataClass sending process.

    Wrapper class that abstracts all process related to creating specific data
    senders, sending data and response handling no matter the communication
    method used.
    """

    _factory = DataSenderFactory()

    def __init__(self, comm_method: str, configs: dict):
        # Persist comm_method and config informations on wrapper instance
        self.comm_method = comm_method
        self.configs = configs

        # Create specific data sender based on chosen comm_method
        self.data_sender = self._factory.create_data_sender(comm_method, configs)

    def send_data(self, payload: Any):
        """Method for sending data using the specific communication method implemented by the created Data Sender.

        Args:
            payload (Any): Any data that will be sent.
        """
        self.data_sender.send_data(payload)

    def get_supported_comm_methods(self) -> List[str]:
        """Getter method for current supported communication methods.

        Returns:
            List[str]: List containing curretly supported communication methods.
        """
        return self._factory.get_supported_comm_methods()

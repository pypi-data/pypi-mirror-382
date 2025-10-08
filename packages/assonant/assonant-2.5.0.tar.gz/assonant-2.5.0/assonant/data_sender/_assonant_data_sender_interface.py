from abc import ABC, abstractmethod
from typing import Any


class IAssonantDataSender(ABC):
    """Assonant Data Sender Interface.

    This interface defines what must be implemented by a class to be a data
    sender in Assonant environment
    """

    @abstractmethod
    def send_data(self, payload: Any):
        """Method resposible for sending a payload through Data Sender specific communication method.

        Args:
            payload (Any): Any data that will be send. Type verification and specific treatment are responsibility
            from each specific DataSender.
        """

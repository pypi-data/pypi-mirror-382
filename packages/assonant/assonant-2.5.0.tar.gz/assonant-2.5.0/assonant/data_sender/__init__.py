"""Assonant Data Sender.

Assonant data sender module handle all process related to creating
data senders for all supported communication methods and sending data over them.
"""

from .assonant_data_sender import AssonantDataSender
from .exceptions import AssonantDataSenderError

__all__ = ["AssonantDataSender", "AssonantDataSenderError"]

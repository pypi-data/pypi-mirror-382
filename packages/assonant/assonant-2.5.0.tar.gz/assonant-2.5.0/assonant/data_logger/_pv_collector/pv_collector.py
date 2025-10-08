from typing import Any, Dict, List

from epics import PV

from assonant.data_classes.enums import ValuePlaceholders


class PVCollector:
    """PV Collector.

    Object responsible to abstracting the collection of values from multiple EPICS PVs.
    """

    pv_handlers = {}

    def __init__(self, pv_names: List[str]):
        """PV Collector Constructor

        Args:
            pv_names (List[str]): List of PV names which the collector will be responsible for.
        """

        # Pre-start PV handler for all passed PVs as it is faster than doing
        # it only when acquisition is demanded.
        for pv_name in pv_names:
            if pv_name not in self.pv_handlers:
                self.pv_handlers[pv_name] = PV(pv_name, connection_timeout=0.1)

        # Guarantee connection for PVs
        for pv_name in self.pv_handlers.keys():
            self.pv_handlers[pv_name].wait_for_connection()

    def acquire_data(self) -> Dict[str, Any]:
        """Call each pv handler to acquire and return current PV value.

        Example of returned data structure:

        {
            PV1_NAME: ACQUIRED_VALUE,
            PV2_NAME: ACQUIRED_VALUE,
            ...
        }

        Returns:
            Dict: Dict with keys being the PV name and value the acquired value for that PV.
        """

        acquisition_result = {}

        # Get value from all PVs
        for pv_name in self.pv_handlers.keys():
            if self.pv_handlers[pv_name].wait_for_connection():
                acquisition_result[pv_name] = self.pv_handlers[pv_name].get()
            else:
                acquisition_result[pv_name] = ValuePlaceholders.PV_NOT_CONNECTED.value

        return acquisition_result

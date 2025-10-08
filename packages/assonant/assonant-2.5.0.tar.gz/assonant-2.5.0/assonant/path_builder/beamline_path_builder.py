from pathlib import Path


class BeamlinePathBuilder:
    """A utility class to build standardized filesystem paths for beamline-related data and proposals.

    Attributes:
        _root (Path): The root directory for all beamline paths.
        _data_schema_file_name (str): The name of the data schema metadata file.
        beamline_name (str): The name of the beamline (must be set before building paths).
        proposal_id (str): The ID of the proposal (optional, but required for some paths).
    """

    def __init__(self):
        """Initializes the BeamlinePathBuilder with default root and data schema filename."""
        self._root = Path("/ibira/lnls/beamlines")
        self._data_schema_file_name = "metadata.csv"
        self.beamline_name = None
        self.proposal_id = None

    def set_beamline_name(self, beamline_name: str):
        """Sets the beamline name for which paths will be built.

        Args:
            beamline_name (str): The name of the beamline.
        """
        self.beamline_name = beamline_name

    def set_proposal(self, proposal_id: str):
        """Sets the proposal ID for which paths will be built.

        Args:
            proposal_id (str): The ID of the proposal.
        """
        self.proposal_id = proposal_id

    def build_path_to_data_schema(self):
        """Builds the path to the data schema metadata file for the specified beamline.

        Returns:
            Path: The full path to the data schema file.

        Raises:
            AssertionError: If beamline_name is not set.
        """
        assert (
            self.beamline_name is not None
        ), "Beamline name property must be set to allow building path to data schema file!"

        path_to_data_schema = self._root / self.beamline_name / Path("apps/assonant") / self._data_schema_file_name
        return str(path_to_data_schema)

    def build_path_to_proposal(self):
        """Builds the path to the directory for the proposal ID previously set.

        Returns:
            Path: The full path to the specific proposal ID directory.

        Raises:
            AssertionError: If beamline_name or proposal_id is not set.
        """
        assert (
            self.beamline_name is not None
        ), "Beamline name property must be set to allow building path to proposal directory!"
        assert (
            self.proposal_id is not None
        ), "Proposal ID property must be set to allow building path to proposal directory!"

        path_to_proposal = self._root / self.beamline_name / Path("proposals") / self.proposal_id
        return str(path_to_proposal)

    def reset(self):
        """Resets the beamline name and proposal ID to None.
        Useful for reusing the builder for different configurations.
        """
        self.beamline_name = None
        self.proposal_id = None

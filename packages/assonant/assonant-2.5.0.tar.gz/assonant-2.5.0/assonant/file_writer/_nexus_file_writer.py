import os

from nexusformat.nexus import NeXusError, nxopen

from assonant._nexus import NeXusObjectFactory
from assonant.data_classes import AssonantDataClass

from .assonant_file_writer_interface import IAssonantFileWriter
from .exceptions import (
    AssonantFileWriterError,
    FileAlreadyExistsError,
    NeXusObjectAlreadyExistsError,
)


class NexusFileWriter(IAssonantFileWriter):
    """NeXus File Writer.

    File Writer specialized on accessing data from AssonantDataClasses and
    write into a HDF5 file following NeXus data model standards.
    """

    def __init__(self):
        self.nexus_factory = NeXusObjectFactory()
        self.file_extension = ".nxs"

    def write_data(self, filepath: str, filename: str, data: AssonantDataClass):
        """Method for writing data into a NeXus file.

        File will be created if it doesn't exist yet, otherwise data will be add to NXroot object of the NeXus file.

        Args:
            filepath (str): Path where NeXus file will be saved.
            filename (str): Name that will be given to file.
            data (AssonantDataClass): AssonantDataClass that contains data
            to be saved in file.
        """
        nexus_filepath = os.path.join(filepath, os.path.splitext(filename)[0]) + self.file_extension

        mode = "rw" if os.path.isfile(nexus_filepath) else "a"

        try:
            with nxopen(nexus_filepath, mode=mode) as nxf:
                nxobject = self.nexus_factory.create_nxobject(data)
                try:
                    nxf.insert(nxobject)
                except NeXusError:
                    # insert method returns NeXusError when NXobject already exist in file
                    raise NeXusObjectAlreadyExistsError(
                        f"NeXus object {nxobject} already exisits on NeXus file from {nexus_filepath}"
                    )
        except NeXusObjectAlreadyExistsError as e:
            # To the upper layer, this must be faced as a FileAlreadyExistError, so raise this Exception.
            raise FileAlreadyExistsError(
                "Due to conflict on writing NeXus object, file is considered to be already existent!"
            ) from e
        except Exception as e:
            raise AssonantFileWriterError(f"NeXusFileWriter failed to write data into {filepath}") from e

    def get_file_extension(self) -> str:
        """Getter method for the file extension of currently handled file writer.

        Returns:
            str: File extenstion of urrently handled file writer.
        """
        return self.file_extension

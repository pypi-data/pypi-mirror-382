from furthrmind.collection.baseclass import BaseClass
import os
from io import BytesIO

class File(BaseClass):
    """
    Attributes
    ----------
    id : str
        id of the file
    name : str
        name of the file including the extension
    """

    id = ""
    name = ""

    _attr_definition = {
    }

    def __init__(self, id=None, data=None):
        super().__init__(id, data)

    @classmethod
    def get(cls, id=None):
        raise TypeError("Not implemented")

    @classmethod
    def _get_all(cls):
        raise TypeError("Not implemented")

    def download(self, folder: str, overwrite: bool = False):
        """
        Method to download a file

        Parameters
        ----------
        folder : str
            The folder where the file should be saved
        overwrite : bool, optional
            Whether to overwrite the existing file in the folder if it already exists (default is False)
        """

        from furthrmind.file_loader import FileLoader
        fl = FileLoader(self.fm.host, self.fm.api_key)

        if not os.path.isdir(folder):
            raise ValueError("Folder does not exist")
        fl.downloadFile(self.id, folder, overwrite)

    def download_bytes(self) -> BytesIO:
        """
        Method to download a file and save to BytesIO object

        Returns:
            BytesIO: The downloaded file stored as BytesIO object
        """

        from furthrmind.file_loader import FileLoader
        fl = FileLoader(self.fm.host, self.fm.api_key)

        flag, bytes_io = fl.downloadFile(self.id, bytesIO=True)
        return bytes_io

    def update_file(self, file_path: str, file_name: str = ""):
        """
        Update a file.

        Parameters
        ----------
        file_path : str
            The path to the file.
        file_name : str, optional
            The new file name. Defaults to "". If not set, the file_name is taken from the file_path.

        Raises
        ------
        ValueError
            If the file does not exist.

        """
        from furthrmind.file_loader import FileLoader
        fl = FileLoader(self.fm.host, self.fm.api_key)

        if not os.path.isfile(file_path):
            raise ValueError("File does not exist")

        fl.updateFile(self.id, file_path, file_name)





import csv

from contextlib import AbstractContextManager
from abc import ABC
from os import PathLike
from pathlib import Path
from io import TextIOBase
from typing import Optional, Union, TextIO
from tabbyset.utils.folder import PathParam


class SourceIO(AbstractContextManager, ABC):
    """
    Implementation for source input output operations.

    :param file: The path of the file or an open file object.
    """
    _file_path: Optional[PathParam] = None
    _textio: Optional[TextIO] = None
    _starting_position: int = 0

    def __init__(self, file: Union[PathParam, TextIO]):
        if isinstance(file, TextIOBase):
            self._textio = file
            self._starting_position = file.tell()
        elif isinstance(file, (PathLike, str, Path)):
            self._file_path = file
        else:
            raise ValueError(f"Invalid file provided: {file}")

    def _prepare_textio_writable(self):
        if self._textio is None:
            self._textio = open(self._file_path, "w", newline='', encoding='utf-8')
        return self._textio

    def _prepare_textio_readable(self):
        if self._textio is None:
            self._textio = open(self._file_path, "r", newline='', encoding='utf-8')
        else:
            self._textio.seek(self._starting_position)
        return self._textio

    def _prepare_csv_writer(self):
        return csv.writer(self._prepare_textio_writable())

    def _prepare_csv_reader(self):
        return csv.reader(self._prepare_textio_readable())

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def __del__(self):
        self.close()

    def close(self):
        """
        Close the file.
        """
        if self._textio is not None:
            self._textio.close()

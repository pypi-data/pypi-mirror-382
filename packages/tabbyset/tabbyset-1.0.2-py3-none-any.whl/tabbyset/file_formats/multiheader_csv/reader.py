import copy
import csv
from typing import Optional, Iterable

from ..common.reader import zip_columns_with_values
from ..common.multiheader_csv.config import MultiheaderConfig
from ..common.multiheader_csv.core import MultiheaderCsvCore

class MHdrCsvReader(Iterable[dict[str, str]]):
    """
    A class for reading custom multiheader CSV files.
    """

    _is_headers_read: bool = False
    _multiheader_core: MultiheaderCsvCore
    _unyieled_line: Optional[dict] = None

    def __init__(self, f, dialect="excel",
                 multiheader_config: Optional[MultiheaderConfig] = None, *args, **kwds):
        self.reader = csv.reader(f, dialect, *args, **kwds)
        self._multiheader_core = MultiheaderCsvCore(multiheader_config)
        self.dialect = dialect

    def __iter__(self):
        return self

    @property
    def line_num(self):
        return self.reader.line_num

    @property
    def headers(self):
        if not self._is_headers_read:
            self._unyieled_line = next(self)
        h = copy.deepcopy(self._multiheader_core.headers)
        for k in h:
            h[k] = [x for x in h[k] if x]
        return h


    @headers.setter
    def headers(self, value: dict[str, list[str]]):
        self._multiheader_core.set_headers(value)

    def __next__(self):
        if self._unyieled_line:
            d = self._unyieled_line
            self._unyieled_line = None
            return d
        line, parsed_line = self._parse_next_line()
        if parsed_line.error_msg:
            raise ValueError(parsed_line.error_msg)
        if not self._is_headers_read:
            while parsed_line.is_header:
                line, parsed_line = self._parse_next_line()
            self._is_headers_read = True
        d = zip_columns_with_values(parsed_line.columns, line)
        d.pop('', None)
        return d

    def _parse_next_line(self):
        line = next(self.reader)
        while not line:
            line = next(self.reader)
        return line, self._multiheader_core.read_line(line)


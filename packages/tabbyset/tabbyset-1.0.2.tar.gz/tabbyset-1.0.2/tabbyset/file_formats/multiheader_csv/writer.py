import copy
import csv
from typing import Optional, Iterable

from ..common.reader import zip_columns_with_values
from ..common.multiheader_csv.config import MultiheaderConfig
from ..common.multiheader_csv.core import MultiheaderCsvCore

class MHdrCsvWriter:
    _multiheader_core: MultiheaderCsvCore

    def __init__(self, f, headers: dict[str, list[str]], restval="", extrasaction="raise",
                 dialect="excel", multiheader_config: Optional[MultiheaderConfig] = None,
                 *args, **kwds):
        self.restval = restval          # for writing short dicts
        if extrasaction.lower() not in ("raise", "ignore"):
            raise ValueError("extrasaction (%s) must be 'raise' or 'ignore'"
                             % extrasaction)
        self.extrasaction = extrasaction
        self._multiheader_core = MultiheaderCsvCore(multiheader_config)
        self._multiheader_core.set_headers(headers, writable=True)
        self.writer = csv.writer(f, dialect, *args, **kwds)

    @property
    def headers(self) -> dict[str, list[str]]:
        return self._multiheader_core.headers

    @headers.setter
    def headers(self, headers: dict[str, list[str]]):
        self._multiheader_core.set_headers(headers, writable=True)

    def writeheaders(self):
        return self.writer.writerows(self._multiheader_core.generate_headers_definitions())

    def writerow(self, rowdict: dict):
        return self.writer.writerow(self._multiheader_core.generate_writable_line(rowdict))

    def writerows(self, rowdicts: Iterable[dict]):
        return self.writer.writerows(map(self._multiheader_core.generate_writable_line, rowdicts))
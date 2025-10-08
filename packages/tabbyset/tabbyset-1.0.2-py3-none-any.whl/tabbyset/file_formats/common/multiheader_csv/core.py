import copy
from dataclasses import dataclass
from tabbyset.presets.multiheader_configs import msgtype_multiheader_config
from .config import MultiheaderConfig
from typing import Union, Optional

from tabbyset.utils.flex_table import dict_row_to_list
from tabbyset.file_formats.common import complete_row


@dataclass(frozen=True)
class ReadLineResult:
    __slots__ = ('is_header', 'category', 'columns', 'is_header', 'error_msg')
    category: str
    columns: list[str]
    is_header: bool
    error_msg: Optional[str]

class MultiheaderCsvCore:
    config: MultiheaderConfig = msgtype_multiheader_config
    headers: dict[str, list[str]]

    def __init__(self, config: MultiheaderConfig = None):
        if config:
            self.config = config
        self.headers = {}

    def set_headers(self, headers: dict[str, list[str]], writable: bool = False):
        headers = copy.deepcopy(headers)
        self.headers = headers
        if writable:
            for category, columns in headers.items():
                category: str
                columns: list[str]
                if self.config.column_before_row_category is not None:
                    if self.config.column_before_row_category in columns:
                        insert_after = columns.index(self.config.column_before_row_category)
                        columns.insert(insert_after + 1, f'{self.config.row_category_prefix}:{category}')
                    else:
                        columns.append(f'{self.config.row_category_prefix}:{category}')

    def reset_headers(self):
        self.headers = {}

    def read_line(self, line: list[str]) -> ReadLineResult:
        line = list(line)
        err_msg = None
        if len(line) < 2:
            tail = ['', '']
        else:
            tail = line[-2:]
        is_multiheader_columns = (
                tail[0] == 'HeaderDefinition'
                and tail[1].startswith(f'HeaderDefinition{self.config.header_category_postfix}:')
        )
        if is_multiheader_columns:
            category = tail[1].split(':', 1)[1]
            if category in self.headers:
                err_msg = f'Duplicated multiheader category - {category}'
            # Remove technical category column from business data
            row_category_column = f'{self.config.row_category_prefix}:{category}'
            for i, cell in enumerate(line):
                if cell == row_category_column:
                    line[i] = ''
                    break
            self.headers[category] = line[:-2]
            return ReadLineResult(category=category, columns=self.headers[category], is_header=True, error_msg=err_msg)
        else:
            current_row_category = self.get_line_multiheader_category(line)
            if current_row_category is None:
                return ReadLineResult(category='', columns=[], is_header=False, error_msg='Multiheader category not found')
            if current_row_category not in self.headers:
                return ReadLineResult(category=current_row_category, columns=[], is_header=False, error_msg=f'Category "{current_row_category}" is not defined in multiheader')
            return ReadLineResult(category=current_row_category, columns=self.headers[current_row_category], is_header=False, error_msg=None)

    def generate_headers_definitions(self) -> list[list[str]]:
        definitions = []
        for category, columns in self.headers.items():
            tail = [
                'HeaderDefinition',
                f'HeaderDefinition{self.config.header_category_postfix}:{category}',
            ]
            definitions.append(columns + tail)
        return definitions

    def generate_writable_line(self, row: dict) -> list[str]:
        category = self.config.categorizer(row)
        category_string = f'{self.config.row_category_prefix}:{category}'
        current_columns = self.headers.get(category, None)
        if current_columns is None:
            raise ValueError(f'The category "{category}" is not defined in the global columns.')
        return dict_row_to_list(row | {category_string: category_string}, current_columns)

    def check_row_category(self, row: dict, category: str) -> tuple[bool, Optional[str]]:
        category_from_config = self.config.categorizer(row)
        if category_from_config != category:
            return False, f'Category mismatch: expected "{category}", got "{category_from_config}"'
        return True, None

    def get_line_multiheader_category(self, line: list[str]) -> Optional[str]:
        for value in line:
            if value.startswith(f'{self.config.row_category_prefix}:'):
                return value.split(':', 1)[1]
        return None

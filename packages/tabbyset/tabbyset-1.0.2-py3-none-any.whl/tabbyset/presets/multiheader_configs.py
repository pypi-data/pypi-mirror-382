"""
Predefined configs for multiheader files.
"""
from tabbyset.file_formats.common.multiheader_csv.config import MultiheaderConfig


def msgtype_categorizer(row: dict) -> str:
    category_key = "MessageType" if "MessageType" in row else "#messagetype"
    return row.get(category_key, 'UNDEFINED')


msgtype_multiheader_config = MultiheaderConfig(row_category_prefix="#messagetype",
                                               column_before_row_category="MessageType",
                                               header_category_postfix="MessageTypes",
                                               categorizer=msgtype_categorizer)

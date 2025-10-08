from .core import MultiheaderCsvCore
from .config import MultiheaderConfig

def set_default_multiheader_config(config: MultiheaderConfig):
    MultiheaderCsvCore.config = config
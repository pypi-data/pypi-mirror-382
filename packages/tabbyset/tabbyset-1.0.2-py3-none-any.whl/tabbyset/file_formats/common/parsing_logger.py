import logging
import csv

class CSVFileHandler(logging.FileHandler):
    def __init__(self, filename: str):
        super().__init__(filename, mode='w', encoding='utf-8')
        self._initialize_log_file()

    def _initialize_log_file(self):
        writer = csv.writer(self.stream, lineterminator='\n')
        writer.writerow(['level', 'filepath', 'lineno', 'test_case_index', 'summary', 'original_line'])

    def emit(self, record: logging.LogRecord):
        writer = csv.writer(self.stream, lineterminator='\n')
        writer.writerow([
            record.levelname,
            record.pathname,
            record.lineno,
            getattr(record, 'test_case_index', None),
            record.getMessage(),
            getattr(record, 'original_line', None),
        ])

class FileParsingLogger:
    def __init__(self, name: str, filename: str,
                 *,
                 level: int = logging.INFO):
        self.native_logger = logging.getLogger(name)
        is_handler_present = False
        for handler in self.native_logger.handlers:
            if isinstance(handler, CSVFileHandler):
                if handler.baseFilename == filename:
                    is_handler_present = True
                    break
        if not is_handler_present:
            self.native_logger.addHandler(CSVFileHandler(filename))
        self.set_level(level)

    def set_level(self, level: int):
        self.native_logger.setLevel(level)

    def make_record(self, level: int, filepath: str, lineno: int, msg: str, test_case_index: int, original_line: str):
        return self.native_logger.makeRecord(
            name=self.native_logger.name,
            level=level,
            fn=filepath,
            lno=lineno,
            msg=msg,
            args=(),
            exc_info=None,
            extra={'test_case_index': test_case_index, 'original_line': original_line}
        )

    def debug(self, msg: str, filepath: str, lineno: int, test_case_index: int, original_line: str):
        if not self.native_logger.isEnabledFor(logging.DEBUG):
            return
        self.native_logger.handle(self.make_record(logging.DEBUG, filepath, lineno, msg, test_case_index, original_line))

    def info(self, msg: str, filepath: str, lineno: int, test_case_index: int, original_line: str):
        if not self.native_logger.isEnabledFor(logging.INFO):
            return
        self.native_logger.handle(self.make_record(logging.INFO, filepath, lineno, msg, test_case_index, original_line))

    def warning(self, msg: str, filepath: str, lineno: int, test_case_index: int, original_line: str):
        if not self.native_logger.isEnabledFor(logging.WARNING):
            return
        self.native_logger.handle(self.make_record(logging.WARNING, filepath, lineno, msg, test_case_index, original_line))

    def error(self, msg: str, filepath: str, lineno: int, test_case_index: int, original_line: str):
        if not self.native_logger.isEnabledFor(logging.ERROR):
            return
        self.native_logger.handle(self.make_record(logging.ERROR, filepath, lineno, msg, test_case_index, original_line))
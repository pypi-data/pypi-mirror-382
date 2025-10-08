from tabbyset.__legacy__.file_formats.v1 import Csv1Reader as LegacyCsv1Reader
import tabbyset as tbs
import logging

def legacy_csv1_file_report(file_path: tbs.PathParam,
                            report_path: tbs.PathParam,
                            *,
                            level: int = logging.WARNING) -> None:
    """
    Print the parsing logs for CSV1 file.
    :param file_path: The path to the file.
    :param report_path: The path to the report file.
    :param level: Minimum level of the messages in report. Default: `logging.WARNING`.
    """
    logger = tbs.FileParsingLogger(f'csv1_parser/legacy/file/{str(file_path)}', report_path, level=level)
    with LegacyCsv1Reader(file_path, tolerant_mode=True, parsing_logger=logger) as reader:
        reader.check_validity()

def legacy_csv1_folder_report(folder_path: tbs.PathParam,
                              report_path: tbs.PathParam,
                              *,
                              level: int = logging.WARNING,
                              deep = False):
    csv1_pattern = tbs.GlobPatterns.csv1_pattern(deep)
    folder = tbs.Folder(folder_path)
    logger = tbs.FileParsingLogger(f'csv1_parser/legacy/folder/{str(folder_path)}', report_path, level=level)
    for file in folder.glob(csv1_pattern):
        with LegacyCsv1Reader(file, tolerant_mode=True, parsing_logger=logger) as reader:
            reader.check_validity()

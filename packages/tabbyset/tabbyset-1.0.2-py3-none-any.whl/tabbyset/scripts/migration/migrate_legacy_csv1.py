import os.path
import sys

from tabbyset.__legacy__.file_formats.v1 import Csv1Reader as LegacyCsv1Reader
import logging
import tabbyset as tbs
import shutil
from tqdm import tqdm

def migrate_legacy_csv1_folder(folder_path: tbs.PathParam,
                               report_path: tbs.PathParam = 'migration_solved_problems.csv',
                               *,
                               deep: bool = False,
                               level: int = logging.INFO):
    legacy_problems_logger = tbs.FileParsingLogger(name=f'csv1_parser/migration/folder/{folder_path}',
                                                   filename=report_path,
                                                   level=level)
    if not os.path.isdir(folder_path):
        raise FileNotFoundError(f'Folder {folder_path} does not exist')
    csv1_pattern = tbs.GlobPatterns.csv1_pattern(deep)
    folder = tbs.Folder(folder_path)
    files = list(folder.glob(csv1_pattern))
    for file in tqdm(files, desc='Migrating Test Scripts', file=sys.stdout):
        tmp_file = str(file)+'.tmp'
        with LegacyCsv1Reader(file, parsing_logger=legacy_problems_logger) as reader, tbs.Csv1Writer(tmp_file) as writer:
            for test_case in reader:
                test_case.id = tbs.TestsTracker.get_id_from_steps(test_case)
                writer.write(test_case)
        shutil.move(tmp_file, file)
    print(f'Migration of {len(files)} files completed')
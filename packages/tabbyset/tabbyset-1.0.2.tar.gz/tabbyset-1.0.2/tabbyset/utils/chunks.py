import sys
from tqdm import tqdm
from tabbyset.file_formats.csv1.reader import Csv1Reader
from tabbyset.file_formats.csv1.writer import Csv1Writer
from .folder import PathParam, Folder

def chunkify_csv1_file(input_file: PathParam, chunks_folder: PathParam, chunk_size: int = 3000) -> None:
    chunks_folder = Folder(chunks_folder)
    progress_bar = tqdm(unit='chunks', file=sys.stdout)
    with Csv1Reader(input_file) as reader:
        chunks_counter = 0
        written_in_chunk = 0
        current_writer = None
        for test_case in reader:
            if written_in_chunk == 0:
                chunks_counter += 1
                current_writer = Csv1Writer(chunks_folder.get_file_path(f'chunk_{chunks_counter}.csv'))
            current_writer.write(test_case)
            written_in_chunk += 1
            progress_bar.set_postfix_str(f'{written_in_chunk} test cases in chunk {chunks_counter}')
            if written_in_chunk >= chunk_size:
                progress_bar.update(1)
                written_in_chunk = 0
                current_writer.close()
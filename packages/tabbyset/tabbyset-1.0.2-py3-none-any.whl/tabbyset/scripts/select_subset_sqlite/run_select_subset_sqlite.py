def run_select_subset_sqlite(venue: str,
                             folder_traces,
                             folder_cases,
                             coverage_script: str,
                             folder_output,
                             *,
                             keep_db: bool = False,
                             with_code_coverage: bool = False,
                             iterator_type):
    """
    This function runs the select subset pipeline.

    In the result of this pipeline, following files will be saved in the `folder_output`:

    - `traces.db`: The SQLite database containing the data used.
    - `<coverage_script>.maxanno.csv`: Minimum set of test cases that cover all traces merged into single CSV1 file.
    - `<coverage_script>.minanno.csv`: Maximum set of test cases that cover all traces merged into single CSV1 file.
    - `<venue>_annotations_summary.csv`: Report file containing the summary of all traces.
    - `<venue>_duplicates_summary.csv`: Report file containing links of traces covered by the same set of test cases.
    - `weights.csv`: Report on the chosen test cases (`1` means test case is chosen, `0` otherwise).

    :param venue: The venue name, used in the names of report files.
    :param folder_traces: The folder containing the traces.
    :param folder_cases: The folder containing the test cases.
    :param coverage_script: The name of the coverage script, used in the names of CSV1 files.
    :param folder_output: The folder where the output files will be saved.
    :param keep_db: If True, the SQLite database will not be deleted after the pipeline finishes.
    :param with_code_coverage: If True, additional traces will be created from .coverage.json files.
    :param iterator_type: The type of iterator to use when selecting the subset.
        `IteratorType.COUNT_ITERATOR` sorts test_cases depending on the number of traces they cover.
        `IteratorType.WEIGHTS_ITERATOR` sorts test_cases depending on the sum of the weights of the traces they cover.
        Default is `IteratorType.COUNT_ITERATOR`.
    """
    raise ModuleNotFoundError(
        'Select subset SQLite was moved to the proprietary module since TabbySet went Open Source. '
        'Use "from ex_subset_selector.select_subset_sqlite import run_select_subset_sqlite".')

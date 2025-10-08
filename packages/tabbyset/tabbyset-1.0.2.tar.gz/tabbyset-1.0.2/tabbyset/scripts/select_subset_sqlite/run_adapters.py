def annotation_traces_vs_test_case(venue: str, folder_traces,  # pylint: disable=too-many-arguments
                                   folder_cases,
                                   coverage_script: str,
                                   folder_output,
                                   include_code_coverage: bool = False,
                                   save_details: bool = False,
                                   exclude_annotations: list = None):
    """
    This adapter runs `tabbyset.scripts.run_select_subset_sqlite`
    with the same interface as in `ex_subset_selector.main.annotation_traces_vs_test_case`.

    These parameters are ignored, as they are not used in the `run_select_subset_sqlite` function:
    - exclude_annotations
    """
    raise ModuleNotFoundError('Select subset SQLite was moved to the proprietary module since TabbySet went Open Source. '
                              'Use "from ex_subset_selector.select_subset_sqlite import annotation_traces_vs_test_case".')

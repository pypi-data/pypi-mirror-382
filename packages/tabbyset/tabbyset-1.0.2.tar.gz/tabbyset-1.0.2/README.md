# TabbySet

TabbySet is a kit of simple tools for working with all business processes around the exactpro model.

## Installation

You can install TabbySet using pip:

```bash
pip install tabbyset
```


## Usage

In general, when you want to write a new script, you should start with the following code:

```python
import tabbyset as tbs
```

`tbs` variable will provide you with all the necessary tools for working with the proprietary tests.

Here are some utilities:
1. `tbs.Folder` - a class for working with folders
2. `tbs.TestCase` - model representing the Exactpro proprietary test case
3. `tbs.Csv1Reader`, `tbs.Csv1Writer` - classes for reading and writing test cases from/to CSV1 files
4. `tbs.Csv2Reader`, `tbs.Csv2Writer` - classes for reading and writing test cases from/to CSV2 files
5. `tbs.floor_to_tick`, `tbs.ceil_to_tick`, `tbs.round_to_tick` - functions for rounding prices to the nearest tick

### Example of filtering the CSV file

```python
import tabbyset as tbs
src_folder = tbs.Folder.mount_from_current_module('./path/to/folder')
output_folder = tbs.Folder.mount_from_current_module('./path/to/output/folder')
# Get list of all files in the folder
files = src_folder.listdir()
# You might want to sort the files
files.sort()
for file in files:
    test_script_path = src_folder.get_file_path(file)
    csv1_reader = tbs.Csv1Reader(test_script_path)
    csv1_writer = tbs.Csv1Writer(output_folder.get_file_path(file))
    for test_case in csv1_reader:
        if {"Action": "Quote"} not in test_case.steps:
            csv1_writer.write(test_case)
    csv1_reader.close()
    csv1_writer.close()
```

## Good old instruments

TabbySet provides a set of instruments with the same interface as the ones already present in the business processes,
but with tested functionality under the hood and/or faster.

## Testing

TabbySet provides utilities for testing compatible with the `unittest` module.

```python
from tabbyset.testing import TestCaseAssertions #, ... other utilities
```


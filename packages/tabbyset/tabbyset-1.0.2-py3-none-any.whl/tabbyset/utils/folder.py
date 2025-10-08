import os
import shutil
from pathlib import Path
from inspect import currentframe, getframeinfo
from typing import Union

PathParam = Union[os.PathLike, str, Path]


class Folder(os.PathLike):
    """
    A class to represent a folder in the file system.

    :param path: The path of the folder.
    """
    path: Path

    def __init__(self, path: PathParam):
        if not os.path.isabs(path):
            path = (Path(os.path.dirname(os.getcwd() + '/')) / path).resolve()
        if not os.path.exists(path) and not os.path.isdir(path):
            os.makedirs(path)
        self.path = Path(path)

    def listdir(self):
        """
        List all files and folders in the folder.
        :return: A list of file and folder names.
        """
        return os.listdir(self.path)

    def glob(self, pattern: str):
        """
        Iterate over this subtree and yield all existing files (of any kind, including directories) matching the given relative pattern.
        :param pattern: The pattern to match.
        :return: An iterator over the matching file path's.
        """
        return self.path.glob(pattern)

    def get_file_path(self, file_name: str) -> Path:
        """
        Get the path of a file in the folder.
        """
        if os.path.isabs(file_name):
            raise ValueError(f'The file name should be relative to the folder, got an absolute path instead {file_name}')
        return self.path / file_name

    def is_file_exists(self, file_name: str) -> bool:
        """
        Check if a file exists in the folder.
        :param file_name: The name of the file.
        :return: True if the file exists, False otherwise.
        """
        return self.get_file_path(file_name).exists()

    def clear(self):
        """
        Remove all files and folders in the folder.
        """
        shutil.rmtree(self.path)
        os.makedirs(self.path)

    def mount_subfolder(self, subfolder: str) -> 'Folder':
        """
        Mount a subfolder in this folder.
        :param subfolder: The name of the subfolder.
        :return: The subfolder.
        """
        return Folder(self.path / subfolder)

    def __str__(self):
        return str(self.path)

    def __repr__(self):
        return str(self.path)

    def __fspath__(self):
        return str(self.path)

    @classmethod
    def mount_from_current_module(cls, folder_rel_path: PathParam) -> 'Folder':
        """
        Mount a folder relative to the current module.

        Might be useful when you want to call the script from different directories.

        :param folder_rel_path: The relative path of the folder.
        :return: The folder.
        """
        current_file_path = getframeinfo(currentframe().f_back).filename
        path = (Path(os.path.dirname(current_file_path)) / folder_rel_path).resolve()
        return cls(path)

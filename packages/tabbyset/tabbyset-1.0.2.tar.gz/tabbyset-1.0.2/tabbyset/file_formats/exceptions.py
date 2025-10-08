from tabbyset.utils.folder import PathParam


class FileParsingException(Exception):
    def __init__(self, file_path: PathParam, line_number: int, message: str):
        """
        Custom exception for parsing errors.

        :param file_path: Path to file trying to parse.
        :param line_number: The line number where the parsing error occurred.
        :param message:  A description of the parsing error.
        """
        super().__init__(message)
        self.line_number = line_number
        self.file_path = file_path

    def __str__(self):
        return f"{super().__str__()}: {self.file_path}:{self.line_number}"


class VirtualFileParsingException(FileParsingException):
    def __init__(self, file: str, line_number: int, message: str):
        Exception.__init__(self, message)
        self.line_number = line_number
        self.file = file

    def __str__(self):
        return f"{Exception.__str__(self)} on line {self.line_number} \n{self.file}"

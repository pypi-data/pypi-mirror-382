import json

from ..abc.source_io import SourceIO

class TcJsonlWriter(SourceIO):
    """
    Implementation for writing a single testcase in JSONL format.

    Might be useful for simultaneous writing of several testcases without the need to keep all of them in memory.

    :param file: The path of the file or an open file object.
    """

    def write_metadata(self, metadata: dict):
        """
        Write the metadata of the testcase.

        Obligatory to write before writing any steps.

        Mandatory fields: name
        Optional fields: description

        :param metadata: The metadata to write.
        """
        textio = self._prepare_textio_writable()
        textio.write(json.dumps({ '$type': 'meta', '$data': metadata }))
        textio.write('\n')

    def write_step(self, step: dict):
        """
        Write a step of the testcase.

        :param step: The step to write.
        """
        textio = self._prepare_textio_writable()
        textio.write(json.dumps({ '$type': 'step', '$data': step }))
        textio.write('\n')
class GlobPatterns:
    """
    Class for defining the glob patterns for the file formats.
    """

    @classmethod
    def _deepify(cls, pattern: str) -> str:
        return '**/' + pattern

    @classmethod
    def csv1_pattern(cls, deep=False) -> str:
        pattern = '*.csv'
        if deep:
            pattern = cls._deepify(pattern)
        return pattern

    @classmethod
    def csv2_pattern(cls, deep=False) -> str:
        pattern = '*.matrix.csv'
        if deep:
            pattern = cls._deepify(pattern)
        return pattern
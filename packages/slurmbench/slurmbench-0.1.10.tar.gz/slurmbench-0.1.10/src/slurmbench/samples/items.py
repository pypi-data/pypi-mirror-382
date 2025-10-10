"""Sample items."""


class RowNumbered:
    """Row numbered sample.

    The row index corresponds to the line number, where the indices is 0-based.
    So the first item row is at line number 1.
    """

    def __init__(self, row_idx: int, sample_uid: str) -> None:
        self.__row_idx = row_idx
        self.__sample_uid = sample_uid

    def row_number(self) -> int:
        """Get row number."""
        return self.__row_idx

    def uid(self) -> str:
        """Get item."""
        return self.__sample_uid

    def to_base_one(self) -> int:
        """Get line number with a base 1.

        The header is at line number 0 (base 0).
        So the first item row (base 0, row number is 1)
        is associated to line number 2 (base 1).
        """
        return self.__row_idx + 1

class Rope:
    """A text rope data structure for efficient text manipulation."""

    def __init__(self, text: str) -> None:
        """Initialize a new Rope with the given text.

        Args:
            text: The initial text content for the rope.
        """

    def insert(self, char_idx: int, text: str) -> None:
        """Insert `text` at character index `char_idx`.

        Args:
            char_idx: The character index where to insert the text.
            text: The text to insert.

        Raises:
            IndexError: If char_idx is out of range.
        """

    def remove(self, start_char: int, end_char: int) -> None:
        """Remove characters in range `[start_char, end_char)`.

        Args:
            start_char: The starting character index (inclusive).
            end_char: The ending character index (exclusive).

        Raises:
            IndexError: If the range is invalid or out of bounds.
        """

    def get_bytes(self) -> bytes:
        """Return the whole rope as a `bytes` object.

        Returns:
            The rope content as bytes.
        """

    def len_chars(self) -> int:
        """Get the number of characters in the rope.

        Returns:
            The character count.
        """

    def len_bytes(self) -> int:
        """Get the number of bytes in the rope.

        Returns:
            The byte count.
        """

    def len_lines(self) -> int:
        """Get the number of lines in the rope.

        Returns:
            The line count.
        """

    def char(self, idx: int) -> str:
        """Get the character at the specified index.

        Args:
            idx: The character index.

        Returns:
            The character at the specified index.

        Raises:
            IndexError: If idx is out of range.
        """

    def line(self, line_idx: int) -> str:
        """Get the line at the specified index.

        Args:
            line_idx: The line index.

        Returns:
            The line content.

        Raises:
            IndexError: If line_idx is out of range.
        """

    def as_str(self) -> str:
        """Return the rope content as a string.

        Returns:
            The rope content as a string.
        """

    def slice(self, start: int, end: int) -> str:
        """Get a slice of characters from the rope.

        Args:
            start: The starting character index (inclusive).
            end: The ending character index (exclusive).

        Returns:
            The sliced string content.

        Raises:
            IndexError: If the range is invalid or out of bounds.
        """

    def byte_slice(self, start_byte: int, end_byte: int) -> bytes:
        """Get a slice of bytes from the rope.

        Args:
            start_byte: The starting byte index (inclusive).
            end_byte: The ending byte index (exclusive).

        Returns:
            The sliced bytes content.

        Raises:
            IndexError: If the range is invalid or out of bounds.
        """

    def byte_to_char(self, byte_idx: int) -> int:
        """Convert a byte index to a character index.

        Args:
            byte_idx: The byte index to convert.

        Returns:
            The corresponding character index.

        Raises:
            IndexError: If byte_idx is out of range.
        """

    def char_to_byte(self, char_idx: int) -> int:
        """Convert a character index to a byte index.

        Args:
            char_idx: The character index to convert.

        Returns:
            The corresponding byte index.

        Raises:
            IndexError: If char_idx is out of range.
        """

    def char_to_line(self, char_idx: int) -> int:
        """Convert a character index to a line index.

        Args:
            char_idx: The character index to convert.

        Returns:
            The corresponding line index.

        Raises:
            IndexError: If char_idx is out of range.
        """

    def line_to_char(self, line_idx: int) -> int:
        """Convert a line index to a character index.

        Args:
            line_idx: The line index to convert.

        Returns:
            The corresponding character index.

        Raises:
            IndexError: If line_idx is out of range.
        """

    def line_to_byte(self, line_idx: int) -> int:
        """Convert a line index to a byte index.

        Args:
            line_idx: The line index to convert.

        Returns:
            The corresponding byte index.

        Raises:
            IndexError: If line_idx is out of range.
        """

    def byte_to_line(self, byte_idx: int) -> int:
        """Convert a byte index to a line index.

        Args:
            byte_idx: The byte index to convert.

        Returns:
            The corresponding line index.

        Raises:
            IndexError: If byte_idx is out of range.
        """

    def byte_to_point(self, byte_idx: int) -> tuple[int, int]:
        """Return `(line, column)` for a given *byte* offset.

        Args:
            byte_idx: The byte index to convert.

        Returns:
            A tuple of (line, column) indices.

        Raises:
            IndexError: If byte_idx is out of range.
        """

    def point_to_byte(self, line: int, column: int) -> int:
        """Return byte offset for a given `(line, column)`.

        Args:
            line: The line index.
            column: The column index.

        Returns:
            The corresponding byte index.

        Raises:
            IndexError: If line or column is out of range.
        """

    def __repr__(self) -> str:
        """Return a string representation of the Rope.

        Returns:
            A string representation of the Rope.
        """

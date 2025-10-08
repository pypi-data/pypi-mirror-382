from typing import final

import hypothesis.strategies as st
import pytest
from hypothesis.stateful import (
    Bundle,
    RuleBasedStateMachine,
    invariant,
    precondition,
    rule,
)

from ropey_py import Rope


@final
class RopeStateMachine(RuleBasedStateMachine):
    """State machine for testing Rope vs a Python string model."""

    def __init__(self) -> None:
        """Initialize the state machine."""
        super().__init__()
        self._rope = Rope('')
        self._model = ''

    texts = Bundle('texts')

    @rule(target=texts, text=st.text())
    def gen_text(self, text: str) -> str:
        """Generate a random text snippet."""
        return text

    @rule(text=texts, char_idx=st.integers(min_value=0))
    def insert(self, text: str, char_idx: int) -> None:
        """Insert `text` at `char_idx` (clamped to valid range)."""
        char_idx = min(char_idx, len(self._model))
        self._rope.insert(char_idx, text)
        self._model = self._model[:char_idx] + text + self._model[char_idx:]

    @rule(start=st.integers(min_value=0), end=st.integers(min_value=0))
    def remove(self, start: int, end: int) -> None:
        """Remove the subrange [start, end)."""
        if not self._model:
            return
        start %= len(self._model) + 1
        end %= len(self._model) + 1
        if start > end:
            start, end = end, start
        self._rope.remove(start, end)
        self._model = self._model[:start] + self._model[end:]

    @precondition(lambda self: self._model)
    @rule(start=st.integers(min_value=0), end=st.integers(min_value=0))
    def slice(self, start: int, end: int) -> None:
        """Check slice."""
        start = min(start, len(self._model))
        end = min(end, len(self._model))

        if start <= end:
            got = self._rope.slice(start, end)
            expect = self._model[start:end]
            assert got == expect
        else:
            with pytest.raises(IndexError):
                self._rope.slice(start, end)

    @precondition(lambda self: self._model)
    @rule(idx=st.integers(min_value=0))
    def char(self, idx: int) -> None:
        """Check char."""
        idx = min(idx, len(self._model))

        if idx < len(self._model):
            got = self._rope.char(idx)
            expect = self._model[idx]
            assert got == expect
        else:
            with pytest.raises(IndexError):
                self._rope.char(idx)

    @precondition(lambda self: '\n' in self._model)
    @rule(line_idx=st.integers(min_value=0))
    def line(self, line_idx: int) -> None:
        """Check line."""
        lines = self._model.splitlines(keepends=True)

        if 0 <= line_idx < len(lines):
            got = self._rope.line(line_idx)
            expect = lines[line_idx]
            assert got == expect
        else:
            with pytest.raises(IndexError):
                self._rope.line(line_idx)

    @precondition(lambda self: self._model)
    @rule(idx=st.integers(min_value=0))
    def char_to_byte(self, idx: int) -> None:
        """Check char_to_byte."""
        idx = min(idx, len(self._model))
        # idx <= len(self._model) is valid in Rust version too
        got = self._rope.char_to_byte(idx)
        expect = len(self._model[:idx].encode())
        assert got == expect

    @invariant()
    def check_lengths(self) -> None:
        """Invariant: character length and byte length match model."""
        assert len(self._model) == self._rope.len_chars()
        assert len(self._model.encode()) == self._rope.len_bytes()

    @invariant()
    def check_content(self) -> None:
        """Invariant: content match between rope and model."""
        assert self._model == self._rope.as_str()
        assert self._model.encode() == self._rope.get_bytes()


TestRopeStateMachine = RopeStateMachine.TestCase

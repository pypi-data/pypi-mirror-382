from __future__ import annotations


class IntegerBuffer:
    def __init__(self, buffer: list[int]) -> None:
        if not isinstance(buffer, list) or any(
            not isinstance(item, int) for item in buffer
        ):
            raise TypeError("Buffer must be a list of integers.")

        self.buffer = tuple(buffer)  # Tuple to guarantee immutability
        self.cursor = 0

    def read(self, items: int = 1) -> int:
        """
        Read `items` integers from the current cursor position and move the cursor.
        """
        if self.cursor + items > len(self.buffer):
            raise IndexError("Reading beyond the buffer.")

        if items <= 0:
            raise IndexError("Can not fetch 0 or negative items.")

        values = self.buffer[self.cursor : self.cursor + items]
        self.cursor += items

        return list(values) if items > 1 else values[0]

    def readInt16BE(self) -> float:  # noqa: N802
        lsb = self.read()
        msb = self.read()

        # ---- old method ---- #
        # if msb < 0:
        #     msb = 2**8 + msb
        #
        # return lsb * 2**8 + msb
        # -------------------- #
        return (lsb * 2**8) + (msb & 0xFF)

    def peek(self, items: int = 1) -> int:
        """
        Peek `items` integers without moving the cursor.
        """
        if self.cursor + items > len(self.buffer):
            raise IndexError("Peeking beyond the buffer.")

        if items <= 0:
            raise IndexError("Can not fetch 0 or negative items.")

        return list(self.buffer[self.cursor : self.cursor + items])

    def seek(self, index: int) -> None:
        """
        Move the cursor to the specified position.
        """
        if not (0 <= index < len(self.buffer)):
            raise IndexError("Seek position out of range.")

        self.cursor = index

    def reset(self) -> None:
        """Reset the cursor to the start of the buffer."""
        self.cursor = 0

    def __getitem__(self, index: int) -> int:
        """
        Direct access to the buffer.
        """
        return self.buffer[index]

    def __len__(self) -> int:
        """Return the length of the buffer."""
        return len(self.buffer)

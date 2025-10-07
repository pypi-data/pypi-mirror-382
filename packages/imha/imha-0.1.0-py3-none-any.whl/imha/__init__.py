"""
imha, a more constrained and friendlier fork of ImageHash.

Copyright (c) 2013, Christopher J Pickett
Copyright (c) 2013-2025, Johannes Buchner
Copyright (c) 2025, Eric Nielsen

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are
met:

1. Redistributions of source code must retain the above copyright
   notice, this list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright
   notice, this list of conditions and the following disclaimer in the
   documentation and/or other materials provided with the distribution.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS
IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED
TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A
PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED
TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""

import math
import statistics
from typing import Any

from PIL import Image


def _reduce(image: Image.Image, size: tuple[int, int]) -> Image.Image:
    return image.convert("L").resize(size, Image.Resampling.LANCZOS)


class Hash:
    r"""
    Represents a hash object.

    The hash value can be converted to various types and representations
    using the built-in functions and provided methods. The hamming
    distance between hashes can be computed by subtracting one hash from
    another.

    >>> from PIL import Image
    >>> import imha
    >>> hash1 = imha.average_hash(Image.open("photo1.jpg"))
    >>> hash1.bin()
    '1111111111010111100100011000000110000001110010011111111111111111'
    >>> hash1.hex()
    'ffd7918181c9ffff'
    >>> hash1.uint()
    18435363585078722559
    >>> bytes(hash1)
    b'\xff\xd7\x91\x81\x81\xc9\xff\xff'
    >>> int(hash1)
    -11380488630829057
    >>> len(hash1)  # hash length in bits
    64
    >>> hash2 = imha.average_hash(Image.open("photo2.jpg"))
    >>> hash2.hex()
    '9f172786e71f1e00'
    >>> hash1 == hash2
    False
    >>> hash1 - hash2  # hamming distance between hashes
    33
    """

    __slots__ = ["_len", "_value"]

    def __init__(self, value: int, len_: int) -> None:
        """
        Create hash object.

        :param value: The hash as an unsigned integer value.
        :param len_: The hash length in bits.
        """
        if value < 0:
            msg = "value must be >= 0"
            raise ValueError(msg)
        if len_ <= 0:
            msg = "len_ must be > 0"
            raise ValueError(msg)
        self._value = value
        self._len = len_

    def bin(self) -> str:
        """Return the hash binary representation."""
        return f"{self._value:0{self._len}b}"

    def hex(self) -> str:
        """Return the hash hexadecimal representation."""
        return f"{self._value:0{math.ceil(self._len / 4)}x}"

    def uint(self) -> int:
        """Return the hash as an unsigned integer value."""
        return self._value

    def __len__(self) -> int:
        """Return len(self), the hash length in bits."""
        return self._len

    def __sub__(self, other: "Hash") -> int:  # noqa: UP037
        """Return self - other, the hamming distance between hashes."""
        if not isinstance(other, Hash):
            msg = "other must be a hash object"
            raise TypeError(msg)
        if self._len != other._len:
            msg = "hash objects must be of the same length"
            raise ValueError(msg)
        diff = self._value ^ other._value
        return sum((diff >> i) & 1 for i in range(self._len))

    def __eq__(self, other: Any) -> bool:
        """Return self == other."""
        if not isinstance(other, Hash):
            return False
        return self._value == other._value and self._len == other._len

    def __hash__(self) -> int:
        """Return hash(self)."""
        return hash((self._value, self._len))

    def __bytes__(self) -> bytes:
        """Return bytes(self), the hash as bytes."""
        return self._value.to_bytes(math.ceil(self._len / 8), byteorder="big")

    def __int__(self) -> int:
        """Return int(self), the hash as a signed integer value."""
        return int.from_bytes(self.__bytes__(), byteorder="big", signed=True)

    def __index__(self) -> int:
        """Return integer for bin(self), hex(self) and oct(self)."""
        return self._value

    def __repr__(self) -> str:
        """Return repr(self)."""
        return f"Hash({self._value}, {self._len})"

    def __str__(self) -> str:
        """Return str(self)."""
        return self.hex()


def average_hash(image: Image.Image, size: tuple[int, int] = (8, 8)) -> Hash:
    """
    Compute Average Hash.

    Computes hash with width*height bits. See
    https://www.hackerfactor.com/blog/index.php?/archives/432-Looks-Like-It.html

    :param image: Source image.
    :param size: Tuple with width and height to resize the image to.
    (Default value = (8, 8))
    """
    pixels = _reduce(image, size).getdata()
    avg = statistics.fmean(pixels)
    width, height = size
    diff = 0
    for i in range(width * height):
        diff = diff << 1 | (pixels[i] > avg)
    return Hash(diff, width * height)


def dhash(
    image: Image.Image, size: tuple[int, int] = (9, 8), *, skip_corners: bool = False
) -> Hash:
    """
    Compute Difference Hash by row.

    Computes row hash with (width-1)*height bits. Enabling skip_corners
    reduces the hash length by 4 bits. This means a 64-bits hash can be
    generated with size=(9, 8) or a 16-bit hash be generated with either
    size=(5, 4) or size=(6, 4), skip_corners=True for example. See
    https://www.hackerfactor.com/blog/index.php?/archives/529-Kind-of-Like-That.html

    :param image: Source image.
    :param size: Tuple with width and height to resize the image to.
    (Default value = (9, 8))
    :param skip_corners: Ignore the four corners.
    (Default value = False)
    """
    pixels = _reduce(image, size).getdata()
    width, height = size
    diff = 0
    for y in range(height):
        for x in range(width - 1):
            if skip_corners and (
                (x == 0 or x == width - 2) and (y == 0 or y == height - 1)
            ):
                continue
            i = x + y * width
            diff = diff << 1 | (pixels[i + 1] > pixels[i])
    return Hash(diff, ((width - 1) * height) - (4 if skip_corners else 0))


def dhash_vertical(
    image: Image.Image, size: tuple[int, int] = (8, 9), *, skip_corners: bool = False
) -> Hash:
    """
    Compute Difference Hash by column.

    Computes col hash with width*(height-1) bits. Enabling skip_corners
    reduces the hash length by 4 bits. This means a 64-bits hash can be
    generated with size=(8, 9) or a 16-bit hash be generated with either
    size=(4, 5) or size=(5, 5), skip_corners=True for example. See
    https://www.hackerfactor.com/blog/index.php?/archives/529-Kind-of-Like-That.html

    :param image: Source image.
    :param size: Tuple with width and height to resize the image to.
    (Default value = (8, 9))
    :param skip_corners: Ignore the four corners.
    (Default value = False)
    """
    pixels = _reduce(image, size).getdata()
    width, height = size
    diff = 0
    for y in range(height - 1):
        for x in range(width):
            if skip_corners and (
                (x == 0 or x == width - 1) and (y == 0 or y == height - 2)
            ):
                continue
            i = x + y * width
            diff = diff << 1 | (pixels[i + width] > pixels[i])
    return Hash(diff, (width * (height - 1)) - (4 if skip_corners else 0))

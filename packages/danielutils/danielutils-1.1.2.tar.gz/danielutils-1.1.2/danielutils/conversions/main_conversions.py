from ..decorators import validate


@validate  # type:ignore
def char_to_int(c: str) -> int:
    """convert char to its representing int value

    Args:
        c (str): char to convert

    Returns:
        int: int value
    """
    return ord(c)


@validate  # type:ignore
def int_to_char(num: int) -> str:
    """convert int to its corresponding char

    Args:
        num (int): number to convert

    Returns:
        str: result character
    """
    return chr(num)


@validate  # type:ignore
def hex_to_char(h: str) -> str:
    """convert hex number to char

    Args:
        h (str): number to convert

    Returns:
        str: result char
    """
    return int_to_char(hex_to_dec(h))


@validate  # type:ignore
def hex_to_dec(h: str) -> int:
    """convert hex to dec

    Args:
        h (str): converts base 16 to base 10

    Returns:
        int: decimal value for hex number
    """
    return int(h, 16)


@validate  # type:ignore
def char_to_hex(c: str) -> str:
    """convert char to hex

    Args:
        c (str): char to convert

    Returns:
        str: hex representation
    """
    return int_to_hex(char_to_int(c))


@validate  # type:ignore
def dec_to_hex(num: int) -> str:
    """convert decimal number to hex

    Args:
        num (int): number to convert

    Returns:
        str: _description_
    """
    return int_to_hex(num)


@validate  # type:ignore
def int_to_hex(num: int) -> str:
    """converts an int to it's hex representation

    Args:
        num (int): int to convert

    Returns:
        str: the hex representation of the int
    """
    return hex(num)


@validate  # type:ignore
def bytes_to_str(b: bytes) -> str:
    """decodes bytes to str

    Args:
        b (bytes): bytes to decode

    Returns:
        str: result
    """
    return b.decode("utf-8")


@validate  # type:ignore
def str_to_bytes(s: str) -> bytes:
    """encodes a string to bytes

    Args:
        s (str): the string to encode

    Returns:
        bytes: result
    """
    return bytes(s, encoding='utf-8')


__all__ = [
    "char_to_int",
    "int_to_char",
    "hex_to_char",
    "hex_to_dec",
    "char_to_hex",
    "dec_to_hex",
    "int_to_hex",
    "bytes_to_str",
    "str_to_bytes"
]

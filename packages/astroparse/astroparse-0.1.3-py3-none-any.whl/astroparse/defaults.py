"""
This file defines the default behaviors of the parser at runtime.
"""

__all__ = [
    "sep_reg",
    "nan_reg",
    "MAX_LINE"
]

#: Regular expression that matches spaces or tabs as separators in input file.
sep_reg: str= r"(?<=\S)( |\t)+(?!\s)"

#: Regular expression that matches NaN entries in input file.
nan_reg: str= "nan"

#: Maximum number of lines that will be read from the input file.
MAX_LINE: int= 1_000_000
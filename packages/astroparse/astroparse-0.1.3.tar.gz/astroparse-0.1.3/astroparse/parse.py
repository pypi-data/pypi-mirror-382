"""
Parse irregular data tables into .csv files or astropy.Table objects.
"""

from astropy.io import ascii
from astropy.table import Table
import re

from .defaults import sep_reg
from .defaults import nan_reg
from .defaults import MAX_LINE

def parse_file(fname_in: str,
               sep_reg: str=sep_reg,
               nan_reg: str=nan_reg,
               hdr: int=-1,
               lo: int=1,
               hi: int=-1,
               fname_out: str=None) -> Table:
    """
    Translates the contents of a file into string interpretable by the astropy
    readers.

    The parsed contents are returned as an astropy `Table` and can be
    optionally be saved to an output file. Empty or NaN data can be replaced
    according to a specified pattern.

    Parameters
    ----------
    fname_in : str
        Name of the input file.
    sep_reg : str
        Regex pattern matching column separators in the input file.
    nan_reg : str
        Regex pattern matching empty or NaN data in the input file.
    hdr : int, default = -1
        Line number in the input file where the header is found. Only one line
        can be read as the 'header' and it must have the same column format as
        the data. A value of `-1` means no header will be prepended to the data.
    lo : int, default = 1
        First line number in the input file where the data appear.
    hi : int, default = -1
        Last line number in the input file where the data appear.
    fname_out : str, default = None
        Name of the output file. A value of `None` indicates that data should
        not be saved to any external file. If a file name is specified, the
        contents of any file at that existing path will be overwritten.

    Returns
    -------
    tbl : astropy.table.Table
        The parsed contents of the input file as an astropy `Table`.
    """

    # the line the header is on must be outside of the data part of the input
    if hdr >= lo:
        raise ValueError("Location of the header line in input file must " + \
                "come before the lines of data. parse_file was provided " + \
                f"hdr = {hdr} >= lo = {lo}.")

    # Read until end of file or `MAXLINE` lines read; don't want memory overflow
    if hi == -1:
        hi = MAX_LINE
    
    ### INPUT FILE PATTERNS
    # regex pattern matching input file separator/delimiter.
    psep = re.compile(sep_reg)

    # regex pattern matching input file missing data.
    pnan = re.compile(nan_reg)

    # open input file `filename`
    fin = open(fname_in, "r")
    
    # accumulate contents of the parsed table
    tbl_lines = []

    # track line number as file is read
    linect = 1

    # read first line to initiate reading process
    line = fin.readline()

    # NOTE end of file reached when `line` is empty string, i.e., ''

    ### PRE LOOP / HEADER
    # skip lines before the range of desired lines
    while linect < lo and line != '':

        # extract header if desired
        if linect == hdr:
            # if the header line matches the regular line pattern, sub for delim
            if psep.search(line) is not None:
                line_new = psep.sub(",", line)
            else:
                line_new = line


            # write the header line to the new table
            tbl_lines.append(line_new)

        # read next line in file
        line = fin.readline()
        linect += 1


    ### MAIN LOOP
    # iterate through file's lines from lo (incl.) to hi (incl.)
    while linect <= hi and line != '':

        # end of file reached
        if line == '':
            break

        # replace missing data chars with nan
        line_nonan = pnan.sub("nan", line)

        # matches for whitespace in each line
        line_new = psep.sub(",", line_nonan)

        # write modified data line to the new table
        tbl_lines.append(line_new)

        # read next line in file
        line = fin.readline()
        linect += 1

    # close input and output files before terminating executation
    fin.close()

    # read new table into memory in python-usable formats
    tbl = ascii.read(tbl_lines, format="csv")

    # write table to .csv if output file name is specified
    if fname_out is not None:
        ascii.write(tbl, fname_out, format="csv", overwrite=True)

    return tbl

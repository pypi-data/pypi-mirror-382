"""
This module defines the `Reader` class.
"""

from astropy.table import Table

from .defaults import sep_reg
from .defaults import nan_reg
from .parse import parse_file



class Reader:
    """
    The `Reader` object is a versatile class that can be leveraged to parse
    multiple input files of multiple formats.
    """



    def __init__(self,
                 sep_reg: str=sep_reg,
                 nan_reg: str=nan_reg,
                 hdr: int=-1,
                 lo: int=1,
                 hi: int=-1):
        """
        Initializes a `Reader` object with the default values for its parsing.

        The values with which a `Reader` is initialized define the default
        behavior for parsing files unless overridden in the `Reader` instance
        methods.

        Parameters
        ----------
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
        """
        self._sep = sep_reg
        self._nan = nan_reg
        self._hdr = hdr
        self._lo = lo
        self._hi = hi



    def parse_file(self,
                   fname_in: str,
                   sep_reg: str=None,
                   nan_reg: str=None,
                   hdr: int=None,
                   lo: int=None,
                   hi: int=None,
                   fname_out: str=None) -> Table:
        """
        Translates the contents of a file into string interpretable by astropy
        readers.

        The parsed contents are returned as an astropy `Table` and can be
        optionally be saved to an output file. Empty or NaN data can be replaced
        according to a specified pattern. Unless otherwise specified, the value
        for all arguments is `None` and will default to those with which the
        `Reader` object was initialized.

        Parameters
        ----------
        fname_in : str
            Name of the input file.
        sep_reg : str, default = None
            Regex pattern matching column separators in the input file.
        nan_reg : str, default = None
            Regex pattern matching empty or NaN data in the input file.
        hdr : int, default = None
            Line number in the input file where the header is found. Only one line
            can be read as the 'header' and it must have the same column format as
            the data. A value of `-1` means no header will be prepended to the data.
        lo : int, default = None
            First line number in the input file where the data appear.
        hi : int, default = None
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
        sep_reg = self._sep if sep_reg is None else sep_reg
        nan_reg = self._nan if nan_reg is None else nan_reg
        hdr = self._hdr if hdr is None else hdr
        lo = self._lo if lo is None else lo
        hi = self._hi if hi is None else hi
        return parse_file(fname_in, sep_reg, nan_reg, hdr, lo, hi, fname_out)



    def from_dicts(self,
                   dict_list: dict[list]) -> list[Table]:
        """
        Parse multiple files using dictionaries of arguments to override the
        default parsing behavior for this `Reader` instance.

        Each dictionary must have keywords that match the method signature of
        `parse_file`. Not all keywords must be specified; only those for
        which the defaults for the given `Reader` instance are not sufficient.

        Parameters
        ----------
        dict_list : list[dict]
            List of arguments for each input file to be passed to `parse_file`.

        Returns
        -------
        tbl_list : list[astropy.table.Table]
            List of the parsed contents of each input file as astropy `Table`.
        """

        # read each file and the arguments provided
        tbl_list = []
        for d in dict_list:
            tbl = self.parse_file(**d)
            tbl_list.append(tbl)

        return tbl_list



    def from_lists(self,
                   flist: list[str],
                   sep_list: list[str]=None,
                   nan_list: list[str]=None,
                   hdr_list: list[int]=None,
                   lo_list: list[int]=None,
                   hi_list: list[int]=None,
                   out_list: list[str]=None) -> list[Table]:
        """
        Parse multiple files using lists of arguments to override the default
        behavior for this `Reader` instance.

        Unless otherwise specified, the value for all lists is `None` and
        will parse each file using the default behavior for the corresponding
        argument provided to this reader. All non-`None` lists must be of the
        same length but can still contain `None` to use the default behavior.

        Parameters
        ----------
        flist : list[str]
            List of input file names.
        sep_list : list[str], default = None
            List of separator regex patterns.
        nan_list : list[str], default = None
            List of NaN regex patterns.
        hdr_list : list[int], default = None
            List of line numbers where the header can be found in each file.
        lo_list : list[int], default = None
            List of first lines where data appear in each file.
        hi_list : list[int], default = None
            List of last lines where data appear in each file.
        fname_out : list[str], default = None
            List of output file names.

        Returns
        -------
        tbl_list : list[astropy.table.Table]
            List of the parsed contents of each input file as astropy `Table`.
        """

        # set up lists of defaults for every file if arg is `None`
        n = len(flist)
        sep_list = [self._sep] * n if sep_list is None else sep_list
        nan_list = [self._nan] * n if nan_list is None else nan_list
        hdr_list = [self._hdr] * n if hdr_list is None else hdr_list
        lo_list = [self._lo] * n if lo_list is None else lo_list
        hi_list = [self._hi] * n if hi_list is None else hi_list
        out_list = [None] * n if out_list is None else out_list

        # map inputs for each file to the parse_files function
        res = map(self.parse_file, flist, sep_list, nan_list, hdr_list, lo_list,
                  hi_list, out_list)

        # return a list of astropy.Table objects for each file
        return list(res)


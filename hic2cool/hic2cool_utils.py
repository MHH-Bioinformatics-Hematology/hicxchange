"""
hic2cool
--------

Converter between .hic files (from juicer) and .cool files (for cooler).

This fork keeps the Python API of hic2cool 1.0.1 (4dn-dcic/hic2cool, written
by Carl Vitzthum, Nezar Abdennur, Soo Lee and Peter Kerpedjiev) and runs the
conversions in C++ (the _hic2cool extension module): .hic versions 6 to 9 are
read, all available CPUs are used by default, and cool2hic_convert converts in
the other direction.

The original hic parsing code was based on the straw project by Neva C. Durand
and Yue Wu (https://github.com/theaidenlab/straw); the cooler file layout
follows cooler (https://github.com/open2c/cooler).

See README for more information
"""
import os
import sys

from . import _hic2cool
from ._version import __version__


def _run(function, *args, **kwargs):
    try:
        return function(*args, **kwargs)
    except _hic2cool.ExitError as error:
        force_exit(str(error))


def hic2cool_convert(infile, outfile, resolution=0, nproc=0, show_warnings=False, silent=False):
    """
    Main function that coordinates the reading of header and footer from infile
    and uses that information to parse the hic matrix.
    Opens outfile and writes in form of .cool file

    Params:
    <infile> str .hic filename (versions 6 to 9)
    <outfile> str .cool output filename
    <resolution> int bp bin size. If 0, use all. Defaults to 0.
                Final .cool structure will change depending on this param (see README)
    <nproc> number of threads to use; 0 (the default) uses all available CPUs
    <show_warnings> bool. If True, print out WARNING messages
    <silent> bool. If true, hide standard output

    Returns the path written: .cool for one resolution, .mcool for several.
    """
    with open(infile, 'rb'):
        pass
    return _run(_hic2cool.convert, os.fspath(infile), os.fspath(outfile), int(resolution), int(nproc),
                bool(show_warnings), bool(silent))


def hic2cool_extractnorms(infile, outfile, exclude_mt=False, show_warnings=False, silent=False):
    """
    Find all normalization vectors in the given hic file at all resolutions and
    attempts to add them to the given cooler file. Does not add any metadata
    to the cooler file.

    Params:
    <infile> str .hic filename
    <outfile> str .cool output filename
    <exclude_mt> bool. If True, ignore MT contacts. Defaults to False.
    <show_warnings> bool. If True, print out WARNING messages
    <silent> bool. If true, hide standard output
    """
    with open(infile, 'rb'):
        pass
    if not os.path.exists(outfile):
        raise FileNotFoundError(2, 'No such file or directory', os.fspath(outfile))
    _run(_hic2cool.extract_norms, os.fspath(infile), os.fspath(outfile), bool(exclude_mt), bool(show_warnings),
         bool(silent))


def hic2cool_update(infile, outfile='', show_warnings=False, silent=False):
    """
    Main function that reads the version of a given input cool file produced
    by hic2cool and performs different upgrading operations.
    Adds 'update-date' metadata to cooler attributes

    Params:
    <infile> str .cool input filename
    <outfile> str outpul filename (optional)
    <show_warnings> bool. If True, print out WARNING messages
    <silent> bool. If true, hide standard output
    """
    if not os.path.exists(infile):
        raise FileNotFoundError(2, 'No such file or directory', os.fspath(infile))
    _run(_hic2cool.update, os.fspath(infile), os.fspath(outfile) if outfile else '', bool(show_warnings),
         bool(silent))


def cool2hic_convert(infile, outfile, resolution=0, nproc=0, hic_version=9, normalizations='auto',
                     add_resolutions=None, cooler_weight=None, genome=None, show_warnings=False, silent=False):
    """
    Convert a cooler file to a .hic file (the opposite of hic2cool_convert).

    Params:
    <infile> str .cool or .mcool filename, or a URI 'file.mcool::/resolutions/10000'
    <outfile> str .hic output filename
    <resolution> int bp resolution of the cooler file to write. If 0, use all.
    <nproc> number of threads to use; 0 (the default) uses all available CPUs
    <hic_version> 8 (Juicer tools 1.22) or 9 (Juicer tools 2), default 9
    <normalizations> 'auto' writes the normalization columns of the bins table
                (as hic2cool writes them) or computes VC, VC_SQRT, KR and SCALE
                when there are none; 'none'; or a list or comma separated
                string of VC, VC_SQRT, KR and SCALE to compute
    <add_resolutions> list of coarser bp resolutions to add, each a multiple
                of the finest resolution written
    <cooler_weight> str. If given, cooler's 'weight' column is written as the
                divisive hic normalization vector of this name
    <genome> str genome id; default the cooler file's genome-assembly
    <show_warnings> bool. If True, print out WARNING messages
    <silent> bool. If true, hide standard output

    Returns the path written.
    """
    path = os.fspath(infile).split('::')[0]
    if not os.path.exists(path):
        raise FileNotFoundError(2, 'No such file or directory', path)
    if not isinstance(normalizations, str):
        normalizations = ','.join(normalizations) if normalizations else 'none'
    return _run(_hic2cool.cool2hic, os.fspath(infile), os.fspath(outfile), int(resolution),
                [int(r) for r in (add_resolutions or [])], int(nproc), int(hic_version), normalizations,
                cooler_weight, genome or '', bool(show_warnings), bool(silent))


def print_stderr(message):
    """
    Simply print str message to stderr
    """
    print(message, file=sys.stderr)


def force_exit(message, req=None):
    """
    Exit the program due to some error. Print out message and close the given
    input files.
    """
    if req:
        req.close()
    print_stderr(message)
    sys.exit(1)

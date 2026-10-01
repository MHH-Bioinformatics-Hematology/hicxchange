"""
`python -m hicxchange`, the subtools of the hicxchange command in Python.

The installed `hicxchange` command is the C++ executable; this module takes the
same arguments, so that either can be used:

    hicxchange hic2cool convert in.hic out.mcool
    python -m hicxchange hic2cool convert in.hic out.mcool

The hic2cool subtool keeps the modes, arguments and defaults of hic2cool 1.0.1,
except -p/--nproc, which defaults to every available CPU.
"""
from __future__ import absolute_import
from . import (
    hic2cool_convert,
    hic2cool_update,
    hic2cool_extractnorms,
    cool2hic_convert,
    __version__
)
import argparse


def shared_arguments(parsers):
    for parser in parsers:
        parser.add_argument(
            "-s", "--silent", help="if used, silence standard program output",
            action="store_true"
        )
        parser.add_argument(
            "-w", "--warnings",
            help="if used, print out non-critical WARNING messages, which are "
                 "hidden by default. Silent mode takes precedence over this",
            action="store_true"
        )


def add_hic2cool(subtools):
    """The hic2cool subtool: .hic to cool, with its three modes."""
    help_text = ('.hic to cool or mcool, with the modes convert, update and '
                 'extract-norms')
    hic2cool = subtools.add_parser('hic2cool', help=help_text, description=help_text)
    modes = hic2cool.add_subparsers(
        title='program modes',
        description='choose one of the following modes:',
        dest='mode',
        metavar='mode: {convert, update, extract-norms}'
    )
    modes.required = True

    convert_help = 'convert a hic file to a cooler file'
    convert = modes.add_parser('convert', help=convert_help, description=convert_help)
    convert.add_argument("infile", help="hic input file path")
    convert.add_argument("outfile", help="cooler output file path")
    convert.add_argument(
        "-r", "--resolution",
        help="integer bp resolution desired in cooler file. Setting to 0 "
             "(default) will use all resolutions. If all resolutions are used, "
             "a multi-res .cool file will be created, which has a different "
             "hdf5 structure. See the README for more info",
        type=int,
        default=0
    )
    convert.add_argument(
        "-p", "--nproc",
        help="number of threads to use to parse hic file. default set to 0, "
             "all available CPUs",
        type=int,
        default=0
    )
    convert.add_argument(
        "--storage-mode", choices=['symmetric-upper', 'square'], default='symmetric-upper',
        help="symmetric-upper (default) stores the upper triangle, as hic2cool "
             "always has; square stores both triangles, cooler's layout for "
             "asymmetric matrices"
    )

    update_help = 'update a cooler file produced by hic2cool'
    update = modes.add_parser('update', help=update_help, description=update_help)
    update.add_argument("infile", help="cooler input file path")
    update.add_argument("-o", "--outfile", help="optional new output file path", default='')

    extract_help = 'extract normalization vectors from a hic file and add them to a cooler file'
    extract = modes.add_parser('extract-norms', help=extract_help, description=extract_help)
    extract.add_argument("infile", help="hic file path")
    extract.add_argument("outfile", help="cooler file path")
    extract.add_argument("-e", "--exclude-mt",
                         help="if used, exclude the mitochondria (MT) from the output",
                         action="store_true")

    shared_arguments([convert, update, extract])


def add_cool2hic(subtools):
    """The cool2hic subtool: cool and mcool to .hic."""
    help_text = 'cool or mcool to .hic version 8 or 9'
    cool2hic = subtools.add_parser('cool2hic', help=help_text, description=help_text)
    cool2hic.add_argument("infile", help="cooler input file path or URI")
    cool2hic.add_argument("outfile", help="hic output file path")
    cool2hic.add_argument("-r", "--resolution", type=int, default=0,
                          help="bp resolution of the cooler file to write; 0 (default) "
                               "writes every resolution of the file")
    cool2hic.add_argument("-a", "--add-resolutions", default='',
                          help="comma separated coarser bp resolutions to add, each a "
                               "multiple of the finest resolution written")
    cool2hic.add_argument("-p", "--nproc", type=int, default=0,
                          help="number of threads to use. default set to 0, all available CPUs")
    cool2hic.add_argument("--hic-version", type=int, choices=[8, 9], default=9,
                          help="hic format version to write: 8 (Juicer tools 1.22) or "
                               "9 (Juicer tools 2), default 9")
    cool2hic.add_argument("-n", "--normalizations", default='auto',
                          help="'auto' (default) writes the normalization vectors stored "
                               "in the bins table, or computes VC, VC_SQRT, KR and SCALE "
                               "when there are none; 'none'; or a comma separated list to "
                               "compute")
    cool2hic.add_argument("--cooler-weight", default=None, metavar='NAME',
                          help="also write cooler's balancing weights (the bins column "
                               "'weight') as the divisive hic normalization vector NAME")
    cool2hic.add_argument("-g", "--genome", default=None,
                          help="genome id for the hic header. default: the cooler file's "
                               "genome-assembly attribute")
    cool2hic.add_argument("--triangle", choices=['auto', 'upper', 'lower'], default='auto',
                          help="for square coolers: auto (default) requires a symmetric "
                               "matrix; upper or lower writes that triangle")
    shared_arguments([cool2hic])


def main():
    """
    Execute the program from the command line
    """
    parser = argparse.ArgumentParser(
        prog='hicxchange',
        description='Converting Hi-C contact matrices between the Juicer .hic format '
                    'and the cooler .cool and .mcool formats, in both directions.')
    parser.add_argument('-v', '--version', action='version',
                        version='%(prog)s ' + __version__)
    subtools = parser.add_subparsers(
        title='subtools',
        description='choose one of the following subtools:',
        dest='subtool',
        metavar='subtool: {hic2cool, cool2hic}'
    )
    subtools.required = True
    add_hic2cool(subtools)
    add_cool2hic(subtools)

    args = parser.parse_args()
    if args.subtool == 'hic2cool':
        if args.mode == 'convert':
            hic2cool_convert(args.infile, args.outfile, args.resolution, args.nproc,
                             args.warnings, args.silent, storage_mode=args.storage_mode)
        elif args.mode == 'update':
            hic2cool_update(args.infile, args.outfile, args.warnings, args.silent)
        elif args.mode == 'extract-norms':
            hic2cool_extractnorms(args.infile, args.outfile, args.exclude_mt, args.warnings,
                                  args.silent)
    elif args.subtool == 'cool2hic':
        add_resolutions = [int(r) for r in args.add_resolutions.split(',') if r.strip()]
        cool2hic_convert(args.infile, args.outfile, args.resolution, args.nproc,
                         args.hic_version, args.normalizations, add_resolutions,
                         args.cooler_weight, args.genome, args.warnings, args.silent,
                         triangle=args.triangle)


if __name__ == '__main__':
    main()

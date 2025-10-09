from ..cluster_tools import hdf2nc
from pkg_resources import get_distribution

VERSION = get_distribution('yori').version


def main():
    import argparse
    parser = argparse.ArgumentParser(description='Command to convert hdf4 files into netcdf4')
    parser.add_argument('filename', help='name of the file to convert')
    parser.add_argument('--varlist', default=[],
                        help='list of variables to include in the output file')
    parser.add_argument('-v', '--version', action='version', version=VERSION,
                        help='Show version and exit')
    parser.add_argument('-r', '--replace', action='store_true',
                        help='delete the hdf4 file after the conversion')
    parser.add_argument('-p', '--preproc', action='store_true',
                        help='preprocessing of the hdf4 before the conversion to netcdf4')
    parser.add_argument('-c', '--compression', default=0,
                        help='set netcdf compression level')
    parser.add_argument('-o', '--output', default='',
                        help='choose the output directory')
    args = parser.parse_args()

    if args.varlist == []:
        vlist = []
    else:
        vlist = [v.strip() for v in args.varlist.split(',')]

    hdf2nc(args.filename,
           var_list=vlist,
           replace=args.replace,
           preprocessing=args.preproc,
           compression=int(args.compression),
           scratch=args.output)

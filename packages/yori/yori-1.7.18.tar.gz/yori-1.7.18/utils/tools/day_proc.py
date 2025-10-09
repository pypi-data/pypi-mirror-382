from pkg_resources import get_distribution
from ..cluster_tools import process_day

VERSION = get_distribution('yori').version


def main():
    import argparse
    parser = argparse.ArgumentParser(description='Command that downloads MODIS-CALIOP ' +
                                     'matchfiles, convert them to netcdf4 and grid them')
    parser.add_argument('year', help='Year of the data to be processed')
    parser.add_argument('jday', help='Julian day of the data to be processed')
    parser.add_argument('-V', '--verbose', action='store_true', help='Enable verbose mode.')
    parser.add_argument('-v', '--version', action='version', version=VERSION, help='Show ' +
                        'version and exit')
    parser.add_argument('-j', '--maxjobs', help='number of simultaneous jobs to run')
    parser.add_argument('-d', '--download', action='store_true',
                        help='tell the code to download the files from the ftp server')
    parser.add_argument('-p', '--path',
                        help='local path where the data will be saved and processed')

    args = parser.parse_args()

    process_day(args.year,
                args.jday,
                verbose=args.verbose,
                maxjobs=args.maxjobs,
                ftp_download=args.download,
                local_path=args.path)

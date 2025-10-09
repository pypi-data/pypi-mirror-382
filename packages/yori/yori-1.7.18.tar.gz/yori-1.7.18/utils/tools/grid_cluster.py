from pkg_resources import get_distribution
from ..cluster_tools import run_year

VERSION = get_distribution('yori').version


def main():
    import argparse
    parser = argparse.ArgumentParser(description='Parallelizable command to run yori-grid on ' +
                                     'CALIOP-MODIS matchfiles. It retrieves ' +
                                     'the files from the SIPS ftp server, converts them and ' +
                                     'process them with yori-grid')
    parser.add_argument('-y', '--year', help='Year of the data to be processed')
    parser.add_argument('-p', '--path', default='/iliad/lenny/pveglio/NRL-NAV/',
                        help='Path where the files are going to be saved')
    parser.add_argument('--start', default=1, help='starting day of processing')
    parser.add_argument('--end', default=365, help='ending day of processing')
    parser.add_argument('-n', '--nfiles', default=15,
                        help='Number of files to be processed per job')
    parser.add_argument('--slurm', default='/home/pveglio/sbatch/scripts/',
                        help='Path where the sbatch scripts are saved')
    parser.add_argument('-d', '--dependency', default=0,
                        help='JobID of the job the new batch submission needs to depend on')
    parser.add_argument('-v', '--version', action='version', version=VERSION, help='Show ' +
                        'version and exit')

    args = parser.parse_args()

    run_year(args.year,
             args.path,
             args.start,
             args.end,
             args.nfiles,
             args.dependency,
             args.slurm)

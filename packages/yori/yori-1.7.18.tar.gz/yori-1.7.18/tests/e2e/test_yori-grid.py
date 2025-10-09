import os
from subprocess import run
from netCDF4 import Dataset

import numpy as np

import pytest


@pytest.fixture()
def fixturepath():
    return os.path.join(os.path.dirname(__file__), '../fixtures')


# GRIDDING TESTS
# config files
@pytest.fixture()
def dummy_config(fixturepath):
    return os.path.join(fixturepath, 'testcfg.yml')


@pytest.fixture()
def realcase_config(fixturepath):
    return os.path.join(fixturepath, 'fulltest_config.yml')


# input files
@pytest.fixture()
def dummy_inputfile(tmpdir, fixturepath):
    run('ncgen -b -o {0}/testinput.nc {1}/test.cdl'.format(tmpdir, fixturepath),
        shell=True, check=True)
    return os.path.join(str(tmpdir), 'testinput.nc')


@pytest.fixture()
def realcase_input(fixturepath):
    return os.path.join(str(fixturepath), 'preyori_ref_testfile_1.nc')


# output files
@pytest.fixture()
def dummy_outputfile(tmpdir):
    return os.path.join(str(tmpdir), 'testoutput.nc')


@pytest.fixture()
def realcase_ref_output(fixturepath):
    return os.path.join(str(fixturepath), 'grid_ref_testfile_1.nc')


@pytest.fixture()
def realcase_output(tmpdir, fixturepath):
    return os.path.join(str(tmpdir), 'grid_out_testfile_1.nc')


# run gridding tests
def test_grid_dummy(dummy_config, dummy_inputfile, dummy_outputfile):
    run('yori-grid {0} {1} {2} -c 5'.format(dummy_config, dummy_inputfile,
                                            dummy_outputfile),
        shell=True, check=True)

    assert os.path.exists(dummy_outputfile)
    assert os.stat(dummy_outputfile).st_size != 0


def test_grid_realcase(realcase_config, realcase_input, realcase_ref_output,
                       realcase_output):
    run('yori-grid {0} {1} {2} -c 5'.format(realcase_config, realcase_input,
                                            realcase_output),
        shell=True, check=True)
    assert os.path.exists(realcase_output)

    check_differences(realcase_ref_output, realcase_output)


# AGGREGATION TEST
# input files
@pytest.fixture()
def aggr_filelist(tmpdir, fixturepath):
    run('ncgen -b -o {0}/grid_input_1.nc {1}/test_aggr_1.cdl'.format(tmpdir, fixturepath),
        shell=True, check=True)
    run('ncgen -b -o {0}/grid_input_2.nc {1}/test_aggr_2.cdl'.format(tmpdir, fixturepath),
        shell=True, check=True)
    run('ls -1 {0}/grid_input_?.nc > {0}/aggr_list'.format(tmpdir),
        shell=True, check=True)
    return os.path.join(str(tmpdir), 'aggr_list')


# filelists for the aggregation tests
@pytest.fixture()
def aggr_realcase_filelist(tmpdir, fixturepath):
    run('ls -1 {0}/grid_ref_testfile_?.nc > {1}/aggr_realcase_list'.format(fixturepath,
                                                                           tmpdir),
        shell=True, check=True)
    return os.path.join(str(tmpdir), 'aggr_realcase_list')


@pytest.fixture()
def aggr_daily_filelist(tmpdir, fixturepath):
    run('ls -1 {0}/grid_ref_testfile_?.nc > {1}/aggr_daily_list'.format(fixturepath,
                                                                        tmpdir),
        shell=True, check=True)
    return os.path.join(str(tmpdir), 'aggr_daily_list')


# output files
@pytest.fixture()
def dummy_aggr_outputfile(tmpdir):
    return os.path.join(str(tmpdir), 'aggr_testoutput.nc')


@pytest.fixture()
def realcase_aggr_output(tmpdir):
    return os.path.join(str(tmpdir), 'aggr_test_realcase.nc')


@pytest.fixture()
def realcase_daily_output(tmpdir):
    return os.path.join(str(tmpdir), 'aggr_daily_realcase.nc')


@pytest.fixture()
def realcase_ref_aggr_output(fixturepath):
    return os.path.join(str(fixturepath), 'aggr_ref_realcase.nc')


# run aggregation tests
def test_aggr(aggr_filelist, dummy_aggr_outputfile):
    run('yori-aggr {0} {1} -c 5'.format(aggr_filelist, dummy_aggr_outputfile),
        shell=True, check=True)

    assert os.path.exists(dummy_aggr_outputfile)
    assert os.stat(dummy_aggr_outputfile).st_size != 0


def test_aggr_realcase(aggr_realcase_filelist, realcase_aggr_output,
                       realcase_ref_aggr_output):
    run('yori-aggr {0} {1} -c 5'.format(aggr_realcase_filelist,
                                        realcase_aggr_output),
        shell=True, check=True)

    assert os.path.exists(realcase_aggr_output)

    check_differences(realcase_ref_aggr_output, realcase_aggr_output)


# def test_daily_aggr(aggr_daily_filelist, realcase_daily_output):
#     methods = ['c6aqua', 'c6terra']
#     for method in methods:
#         run(('yori-aggr {0} {1} -c 5 --daily 2014-02-02 ' +
#              '--method {2}').format(aggr_daily_filelist, realcase_daily_output,
#                                     method),
#             shell=True, check=True)
#
#         assert os.path.exists(realcase_daily_output)


def check_differences(ref_output, test_output):
    ref_file = Dataset(ref_output)
    new_file = Dataset(test_output)

    for var in list(new_file.variables):
        check = np.allclose(ref_file[var][:].filled(ref_file[var]._FillValue),
                            new_file[var][:].filled(new_file[var]._FillValue),
                            equal_nan=True)
        assert check, 'Test failed at "{}"'.format(var)
    for grp in list(new_file.groups):
        for var in list(new_file[grp].variables):
            check = np.allclose(ref_file[grp][var][:].filled(ref_file[grp][var]._FillValue),
                                new_file[grp][var][:].filled(new_file[grp][var]._FillValue),
                                equal_nan=True)
            assert check, 'Test failed at "{}, {}"'.format(grp, var)

    ref_file.close()
    new_file.close()

import os
import subprocess
import ftplib
import numpy as np
import sys
# import netCDF4 as nc

from copy import deepcopy

import yori.ioutils as io

from utils.readers import read_hdf

# _ftp_path = 'sips.ssec.wisc.edu/products/matchups/modis-caliop-alexa/v20170801/'
_ftp_path = 'sips.ssec.wisc.edu/match/modis-caliop/1.1dev6/'
_iris_path = '/data/pveglio/NRL-NAV/'
# _var_list = ['modis_latitude', 'modis_longitude', 'modis_landsea_mask',
#              'modis_daynight_mask', 'modis_cloud_top_height', 'modis_cloud_mask',
#              'modis_cloud_optical_thickness', 'modis_aod_unfiltered',
#              'caliop_clay_time', 'caliop_clay_layer_top_altitude',
#              'caliop_clay_cloud_fraction', 'caliop_cpro_cloud_extinction_msl',
#              'caliop_apro_aerosol_extinction_msl', 'caliop_clay_opacity_flag',
#              'modis_cloud_phase']

_var_list = ['master_latitude', 'master_longitude', 'master_landsea_mask',
             'master_daynight_mask', 'master_cloud_top_height', 'master_cloud_mask_myd35',
             'master_cloud_optical_thickness', 'master_aod_unfiltered',
             'caliop_clay_time', 'caliop_clay_layer_top_altitude',
             'caliop_clay_cloud_fraction', 'caliop_cpro_cloud_extinction_msl',
             'caliop_apro_aerosol_extinction_msl', 'caliop_clay_opacity_flag',
             'master_cloud_phase', 'master_solar_zenith', 'caliop_clay_ice_fraction',
             'caliop_clay_liquid_fraction', 'caliop_clay_feature_optical_depth_532',
             'master_cloud_phase', 'caliop_clay_cloud_fraction_1km']


def hdf2nc(fname, var_list=_var_list, replace=False, preprocessing=False,
           compression=0, scratch=''):

    if scratch == '':
        fout = fname[:-3] + 'nc'
    else:
        fout = scratch + fname.split('/')[-1][:-3] + 'nc'

    modcal = read_hdf(fname, var_list)
    tmp_modcal = {k: np.squeeze(modcal[k]) for k in list(modcal)}

    if preprocessing is True:
        new_modcal = preproc(tmp_modcal)
    else:
        new_modcal = tmp_modcal

    outInst = io.CreateMatchfile(fout, new_modcal, comp=compression)
    outInst.createFile()

    for k in list(new_modcal):
        outInst.saveNewVar(k)

    if replace is True:
        os.system('rm -rf ' + fname)


def preproc(dict_var):

    ot, tmp, out_dict = {}, {}, {}
    ot['cal_cloud'] = np.nansum(dict_var['caliop_cpro_cloud_extinction_msl'], axis=0)
    opacity_flag = np.nansum(dict_var['caliop_clay_opacity_flag'], axis=0)
    idx = np.nonzero(opacity_flag > 0)
    ot['cal_cloud'][idx] = 100
    ot['cal_aerosol'] = np.nansum(dict_var['caliop_apro_aerosol_extinction_msl'], axis=0)
    ot['cal_total'] = ot['cal_cloud'] + ot['cal_aerosol']

###

    ot['cal_cloud_532'] = np.nansum(dict_var['caliop_clay_feature_optical_depth_532'], axis=0)
    ot['cal_cloud_532'][ot['cal_cloud_532'] < 0] = 0
    tmp['caliop_cf_1km'] = np.ceil(dict_var['caliop_clay_cloud_fraction_1km'][0, :])
    cf_ice = np.nansum(dict_var['caliop_clay_ice_fraction'], axis=0)
    cf_wtr = np.nansum(dict_var['caliop_clay_liquid_fraction'], axis=0)
    cf_tot = cf_ice + cf_wtr
    idx = np.nonzero(cf_tot == 0)
    cf_ice[idx], cf_wtr[idx], cf_tot[idx] = 0., 0., 1.

    ice_fraction = np.floor(cf_ice) / cf_tot
#    water_fraction = cf_wtr / cf_tot

    idx1 = np.nonzero(ice_fraction == 1)
#    idx2 = np.nonzero(water_fraction == 1)
#    idx3 = np.nonzero((ice_fraction < 1) & (water_fraction < 1))
#    idx4 = np.nonzero((ice_fraction == 0) & (water_fraction == 0))

    tmp_ice_mask = np.zeros(np.shape(cf_tot))
    tmp_ice_mask[idx1] = 1

# PLEASE DOUBLE CHECK THESE LINES AND MAKE SURE THEY MAKE SENSE!!!
    tmp['caliop_cf_ice'] = np.zeros(np.shape(tmp['caliop_cf_1km']))
    tmp['caliop_cf_ice'] = ice_fraction

#    tmp['caliop_cf_mixed'] = np.zeros(np.shape(cf_tot))
#    tmp['caliop_cf_mixed'][idx2] = dict_var['caliop_clay_cloud_fraction_1km'][0, idx2]
#    tmp['caliop_cf_water'] = np.zeros(np.shape(cf_tot))
#    tmp['caliop_cf_water'][idx3] = dict_var['caliop_clay_cloud_fraction_1km'][0, idx3]
#    tmp['caliop_cf_clear'] = np.zeros(np.shape(cf_tot))
#    tmp['caliop_cf_clear'][idx4] = dict_var['caliop_clay_cloud_fraction_1km'][0, idx4]

###

    ot['mod_cloud'] = np.squeeze(dict_var['master_cloud_optical_thickness']*0.01)
    ot['mod_aerosol'] = dict_var['master_aod_unfiltered']

    masks = cloud_phase_masks(dict_var['master_cloud_phase'])
    masks['cal_mask_ice'] = tmp_ice_mask

    ot['mod_cloud'][ot['mod_cloud'] == 0] = np.nan
    ot['mod_cloud'][masks['clear'] == 1] = 0
    ot['mod_total'] = np.nansum(np.dstack((ot['mod_cloud'], ot['mod_aerosol'])), 2)
    ot['mod_total'] = np.squeeze(ot['mod_total'])

    tmp['caliop_cloud_fraction'] = dict_var['caliop_clay_cloud_fraction'][0, :]
    tmp['modis_cloud_fraction'] = np.abs(np.floor(dict_var['master_cloud_mask_myd35']/2)-1)
    tmp['modis_cloud_fraction'] = np.squeeze(tmp['modis_cloud_fraction'])

    for k in list(ot):
        tmp[k + '_transmittance'] = compute_transmittance(ot[k])

    transbins = np.concatenate(([100, 98, 95], np.arange(90, 0, -10), [7, 5]))

    for tau in transbins:
        cal_tr = deepcopy(tmp['cal_cloud_transmittance'])
        mod_tr = deepcopy(tmp['mod_cloud_transmittance'])
        cal_tr[np.isnan(cal_tr)] = -1
        mod_tr[np.isnan(mod_tr)] = -1
        cf_mask_cal = deepcopy(tmp['caliop_cloud_fraction'])
        cf_mask_cal[cal_tr > tau/100.] = 0
        tmp['cal_mask_lt_' + str(tau)] = cf_mask_cal

        cf_mask_mod = deepcopy(tmp['modis_cloud_fraction'])
        cf_mask_mod[mod_tr > tau/100.] = 0
        tmp['mod_mask_lt_' + str(tau)] = cf_mask_mod

    out_dict['modis_latitude'] = dict_var['master_latitude']
    out_dict['modis_longitude'] = dict_var['master_longitude']
    out_dict.update(tmp)
    out_dict.update(ot)

    idx_day = np.nonzero(np.squeeze(dict_var['master_solar_zenith']) < 90.)
    idx_night = np.nonzero(np.squeeze(dict_var['master_solar_zenith']) >= 90.)
    out_dict['modis_day_mask'] = np.zeros(np.shape(np.squeeze(dict_var['master_solar_zenith'])))
    out_dict['modis_night_mask'] = np.zeros(np.shape(np.squeeze(dict_var['master_solar_zenith'])))
    out_dict['modis_day_mask'][idx_day] = 1
    out_dict['modis_night_mask'][idx_night] = 1

    for k in list(masks):
        out_dict['cloud_mask_' + k] = masks[k]

    return out_dict


def cloud_phase_masks(cpop):
    mask = {}

    mask_list = ['undetermined', 'clear', 'water', 'ice', 'undetermined_phase']
    for k in list(mask_list):
        mask[k] = np.zeros(np.shape(cpop))

    mask['undetermined'][cpop == 0] = 1
    mask['clear'][cpop == 1] = 1
    mask['water'][cpop == 2] = 1
    mask['ice'][cpop == 3] = 1
    mask['undetermined_phase'][cpop == 4] = 1

    return mask


def compute_transmittance(optical_thickness):
    trans = np.exp(-optical_thickness)
    return trans


def download_only(year, local_path=_iris_path, start_day=1, end_day=366):

    days = range(start_day, end_day+1)
    ftp_jobid = 0
    for jday in days:
        grid = SelectDate(year, jday, iris_path=local_path)
        file_list = grid.check_path()
        if len(file_list) > 0:
            grid.set_folders()

            fid = open(grid.wdir + 'flist', 'w')
            for fname in file_list:
                fid.write(fname + '\n')
            fid.close()

            if ftp_jobid == 0:
                ftp_cmd = ('sbatch /home/pveglio/sbatch_scripts/yori_download.sh ' +
                           str(year) + ' ' + format(jday, '03d'))
                ftp_status = subprocess.getstatusoutput(ftp_cmd)
                ftp_jobid = ftp_status[1].strip('Submitted batch job ')
            else:
                ftp_cmd = ('sbatch --dependency=afterany:{0} ' +
                           '/home/pveglio/sbatch_scripts/yori_download.sh ' +
                           str(year) + ' ' + format(jday, '03d')).format(ftp_jobid)
                ftp_status = subprocess.getstatusoutput(ftp_cmd)
                ftp_jobid = ftp_status[1].strip('Submitted batch job ')
            grid_cmd = ('sbatch ' + '--dependency=afterok:{0} ' +
                        '/home/pveglio/sbatch_scripts/sbatch_repack.sh ' +
                        grid.wdir).format(ftp_jobid)
            # print(grid_cmd)
            subprocess.call(grid_cmd, shell=True)


def grid_only(year, local_path=_iris_path, start_day=1, end_day=366):

    days = range(start_day, end_day+1)

    for jday in days:
        grid = SelectDate(year, jday, iris_path=local_path)
        grid_cmd = ('sbatch ' + '/home/pveglio/sbatch_scripts/yori_cluster.sh ' + grid.wdir)
        subprocess.call(grid_cmd, shell=True)


def run_year(year, local_path=_iris_path, start_day=1, end_day=366,
             nfiles=30, ftp_jobid=0, path_slurm_scripts='/home/pveglio/sbatch_scripts/'):

    days = range(start_day, end_day+1)
    for jday in days:
        grid = SelectDate(year, jday, iris_path=local_path)
        file_list = grid.check_path()
        if len(file_list) > 0:
            grid.set_folders()

            fid = open(grid.wdir + 'flist', 'w')
            for fname in file_list:
                fid.write(fname + '\n')
            fid.close()

            n_parts = len(file_list) // nfiles
            partial_flist = split_list(file_list, n_parts)
            save_partial_list(partial_flist, grid.wdir)

            if ftp_jobid == 0:
                ftp_cmd = ('sbatch ' + path_slurm_scripts + 'yori_download.sh ' +
                           str(year) + ' ' + format(jday, '03d'))
                ftp_status = subprocess.getstatusoutput(ftp_cmd)
                ftp_jobid = ftp_status[1].strip('Submitted batch job ')
                # print(ftp_cmd)
            else:
                ftp_cmd = ('sbatch --dependency=afterany:{0} ' +
                           path_slurm_scripts + 'yori_download.sh ' +
                           str(year) + ' ' + format(jday, '03d')).format(ftp_jobid)
                ftp_status = subprocess.getstatusoutput(ftp_cmd)
                ftp_jobid = ftp_status[1].strip('Submitted batch job ')
                # print(ftp_cmd)
            grid_cmd = ('sbatch ' + '--dependency=afterok:{0} ' +
                        '--array=1-{1} ' +
                        path_slurm_scripts + 'yori_cluster.sh ' +
                        grid.wdir).format(ftp_jobid, n_parts)
            # print(grid_cmd)
            subprocess.call(grid_cmd, shell=True)


def split_list(inlist, wanted_parts):
    length = len(inlist)

    return [inlist[i*length // wanted_parts: (i+1)*length // wanted_parts]
            for i in range(wanted_parts)]


def save_partial_list(inlist, path):
    for i in range(len(inlist)):
        f = open('{0}tmp_flist_{1}'.format(path, i), 'w')
        for l in inlist[i]:
            f.write(l + '\n')
        f.close()


class SelectDate(object):

    def __init__(self, year, jday, verbose=False, ftp_path=_ftp_path, iris_path=_iris_path):
        self.year = int(year)
        self.jday = int(jday)
        self.verbose = verbose
        self.ftp_path = ftp_path
        self.iris_path = iris_path
        self.sub_path = str(self.year) + '/' + format(self.jday, '03d') + '/'
        self.wdir = self.iris_path + self.sub_path

    def set_folders(self):
        os.system('mkdir -p ' + self.wdir)

    def check_path(self):
        ftp_root = self.ftp_path.split('/')[0]
        subdir = self.ftp_path.strip(ftp_root)
        ftp = ftplib.FTP(ftp_root, 'anonymous')
        flist = []

        if subdir + str(self.year) in ftp.nlst(subdir):
            ftp.cwd(subdir + str(self.year))

            if format(self.jday, '03d') in ftp.nlst():
                ftp.cwd(format(self.jday, '03d'))
                flist = ftp.nlst('*.hdf')
        ftp.quit()

        return flist


if __name__ == '__main__':

    hdf2nc(fname=sys.argv[1],
           replace=True,
           preprocessing=True)

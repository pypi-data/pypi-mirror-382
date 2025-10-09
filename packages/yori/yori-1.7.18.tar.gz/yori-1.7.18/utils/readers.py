import numpy as np

from pyhdf.SD import SD


########################################
#               FUNCTION               #
########################################
# function for reading variables inside an hdf4 file
def read_hdf(fstr, varlist=[]):
    """read_hdf(fstr[, varlist])

    read the variables provided as inputs from an hdf4 file and save them into a dictionary

    Parameters
    ----------
    fstr : string
        name of the hdf4file
    varlist : array [string]
        name of the variables to be read inside the file
        default = 0 (reads the entire file)

    Returns
    -------
    output : dictionary
        dictionary of variables contained in the input hdf4 file
    """
    #read open the hdf file
    hdff = SD(fstr);

    #define the string of variables to read if not defined
    if varlist != []:
        varlist = varlist;
    else:
        varlist = hdff.datasets();
        varlist = varlist.keys();
    #end var list files

    #define the dictionary
    output = {};

    for varname in varlist:
        vartmp    = hdff.select(varname);
        attr      = vartmp.attributes();
        attr_list = attr.keys();
        var       = vartmp.get();
        varf      = var.astype('float64')

        if '_FillValue' in attr_list:
            fillvalue = attr['_FillValue'];
            fillidx = np.where(varf == fillvalue);
            varf[fillidx]=0 #np.nan;
        else:
            fillvalue = 0
        if 'add_offset' in attr_list:
            add_offset = attr['add_offset'];
        else:
            add_offset = 0;
        if 'scale_factor' in attr_list:
            scale_factor = attr['scale_factor'];
        else:
            scale_factor = 1

        output[varname] = varf*scale_factor+add_offset;

    hdff.end()

    return output

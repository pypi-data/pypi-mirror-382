import glob
import math as mth
import numpy as np
import matplotlib.pyplot as plt

from astropy.table import Table
from astropy.utils.data import get_file_contents

from ligo.raven import search, offline_search


data_path = 'ligo/raven/tests/data/injection_study/'
results_path = 'ligo/raven/tests/FAR_study_results/'


### Define functions
def rand_skymap(skymap_array):
    ind = mth.floor(np.random.random() * len(skymap_array))
    return skymap_array[ind]


### Simulate Data

def test_FAR_study():
    
    # Get GRB skymaps
    grb_skymap_fnames = glob.glob(data_path+'grb/*')

    # Get LVC skymaps
    lvc_skymap_fnames = glob.glob(data_path+'gw/*')
    for i in range(len(lvc_skymap_fnames)):
        lvc_skymap_fnames[i] = lvc_skymap_fnames[i] + str('/bayestar.fits.gz')

    years = 5
    sec_per_year = 365. * 24. * 60. * 60.
    OPA_far_thresh = 1 / sec_per_year

    far_thresh = 1 / 3600
    n_grb0 = 310 # per year
    grb_rate = n_grb0 / sec_per_year
    n_grb =  int(n_grb0 * years) # total
    n_gw = int(far_thresh * sec_per_year * years) # total
    far_gw = np.random.power(1, n_gw) * far_thresh # create FAR for each event

    tl = -60 # start window
    th = 600 # end window

    # create random time for each event
    t_grb = np.random.random(n_grb) * sec_per_year * years
    t_gw = np.random.random(n_gw) * sec_per_year * years

    # Create GW and GRB tables, outputting to .csv format
    gw_table = Table()
    gw_table['superevent_id'] = ['S' + str(i) for i in np.arange(1, n_gw + 1)]
    gw_table['t_0'] = t_gw
    gw_table['far'] = far_gw
    gw_table ['skymap'] = [rand_skymap(lvc_skymap_fnames) for i in range(n_gw)]
    gw_path = results_path + 'gw.csv'
    gw_table.write(gw_path, overwrite=True)

    grb_table = Table()
    grb_table['graceid'] = ['E' + str(i) for i in np.arange(1, n_grb + 1)]
    grb_table['gpstime'] = t_grb
    grb_table ['skymap'] = \
        [rand_skymap(grb_skymap_fnames) for i in range(n_grb)]
    grb_table['search'] = np.full(n_grb, 'GRB')
    grb_path = results_path + 'grb.csv'
    grb_table.write(grb_path, overwrite=True)

    # Run offline search
    offline_search.offline_search(gw_path, grb_path, output_path=results_path,
                                  t_start=0, t_end=(years * sec_per_year),
                                  tl=tl, th=th,
                                  gw_far_thresh=far_thresh,
                                  alert_far_thresh=OPA_far_thresh,
                                  ext_rate=n_grb / (sec_per_year * years),
                                  trials_factor=1, load_gw_fars=True)

### Run tests
test_FAR_study()

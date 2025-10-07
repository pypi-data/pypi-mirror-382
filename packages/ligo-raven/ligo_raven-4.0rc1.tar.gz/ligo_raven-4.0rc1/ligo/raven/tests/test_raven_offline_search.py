from unittest.mock import call, patch
import unittest.mock as mock
import pytest
from astropy import units as u
from astropy.coordinates import SkyCoord
from astropy.utils.data import get_file_contents
from importlib import resources
from math import isclose
import json
import tempfile
import shutil

from ligo import raven
from ligo.raven.gracedb_events import _is_gracedb_sdk
from ligo.raven.offline_search import get_skymap_filename, offline_search
from . import data


def read_json(pkg, filename):
    """Load a JSON file from package data."""
    with resources.files(pkg).joinpath(filename).open('r') as f:
        return json.load(f)


@pytest.mark.parametrize(
    'group,pipeline,ext_search,se_search',
     # Generic find everything search
    [[None, None, None, None],
     # General CBC search
     ['CBC', None, 'GRB', None],
     # General Burst search
     ['Burst', None, 'GRB', 'AllSky'],
     # Fermi SubGRBTargeted search
     [None, 'Fermi', 'SubGRBTargeted', None],
     # Swift SubGRBTargeted search
     [None, 'Swift', 'SubGRBTargeted', None],
     # Run search that won't have sky map info
     ['CBC', 'AGILE', 'GRB', 'AllSky'],
     # Run fake search which will return nothing
     ['CBC', None, None, 'Not-Real-Search']])
def test_raven_offline_search(group, pipeline, ext_search, se_search):
    # Assign constants based on search parameters
    trials_factors = 4
    if ext_search in {'SubGRB', 'SubGRBTargeted'}:
        gw_far_thresh = 2 / (24. * 60. * 60.)
        if pipeline == 'Fermi':
            tl, th = -1, 11
            ext_far_thresh = 1e-4
        elif pipeline == 'Swift':
            tl, th = -10, 20
            ext_far_thresh = 1e-3
        if group == 'Burst':
            alert_far_thresh = 1 / (365. * 24. * 60. * 60.) * 12.
        else:
            alert_far_thresh = 1 / (365. * 24. * 60. * 60.)
    else:
        if group == 'Burst':
            tl, th = -60, 600
            alert_far_thresh = 1 / (365. * 24. * 60. * 60.)
            trials_factors = 3
        else:
            tl, th = -1, 5
            alert_far_thresh = 1 / (365. * 24. * 60. * 60.) * 12.
        gw_far_thresh = None
        ext_far_thresh = None

    # Make temporary directory to delete later
    output_path = tempfile.mkdtemp()
    if pipeline == 'AGILE':
        output_path += '/directory'
    results_table = offline_search(
        'ligo/raven/tests/data/GW170817/test-gw-search.csv',
        'ligo/raven/tests/data/GW170817/test-grb-search.csv',
        output_path=output_path, t_start=0, t_end=200, tl=tl, th=th,
        load_gw_fars=(pipeline is None and ext_search is None),
        use_radec=True,
        gw_far_thresh=gw_far_thresh, ext_far_thresh=ext_far_thresh,
        alert_far_thresh=alert_far_thresh,
        group=group, pipeline=pipeline,
        ext_search=ext_search, se_search=se_search
    )
    # Check results
    print(results_table)
    # Remove temporary directory
    shutil.rmtree(output_path)


@pytest.mark.parametrize('num_events', [1, 2])
def test_raven_offline_search_events(num_events):
    # Assign constants based on search parameters
    trials_factors = 4
    tl, th = -1, 5
    alert_far_thresh = 1 / (365. * 24. * 60. * 60.) * 12.
    gw_far_thresh = None
    ext_far_thresh = None

    # Make temporary directory to delete later
    ext_event = read_json(data, 'rubin_event_sample.json')
    output_path = tempfile.mkdtemp()

    if num_events == 1:
        input = ext_event
    elif num_events == 2:
        input = [ext_event, ext_event]
    results_table = offline_search(
        'ligo/raven/tests/data/GW170817/test-gw-search.csv',
        input,
        output_path=output_path, t_start=0, t_end=200, tl=tl, th=th,
        load_gw_fars=False,
        use_radec=True,
        gw_far_thresh=gw_far_thresh, ext_far_thresh=ext_far_thresh,
        alert_far_thresh=alert_far_thresh,
        group='CBC', pipeline='Rubin',
        ext_search='Optical', se_search='AllSky',
        ext_rate=1e-4,
        joint_far_method='untargeted'
    )
    # Check results
    print(results_table)
    # Remove temporary directory
    shutil.rmtree(output_path)


@pytest.mark.parametrize(
    't_end,th',
     # End search since searched time is 0
    [[100, 5],
     # End search since time window is 0
     [105, 0]])
def test_raven_offline_search_failure_window(t_end, th):
    # Make temporary directory to delete later
    output_path = tempfile.mkdtemp()
    # Ensure a ValueError is raised
    with pytest.raises(ValueError):
        results_table = offline_search(
            'ligo/raven/tests/data/GW170817/test-gw-search.csv',
            'ligo/raven/tests/data/GW170817/test-grb-search.csv',
            output_path=output_path, t_start=100, t_end=t_end, tl=0, th=th,
        )
    # Remove temporary directory
    shutil.rmtree(output_path)


def test_raven_offline_search_failure_input():
    # Make temporary directory to delete later
    output_path = tempfile.mkdtemp()
    # Ensure a ValueError is raised
    with pytest.raises(TypeError):
        results_table = offline_search(
            1.,
            .3,
            output_path=output_path, t_start=0, t_end=200, tl=0, th=10,
        )
    # Remove temporary directory
    shutil.rmtree(output_path)


@pytest.mark.parametrize(
    'filename',
     # End search since searched time is 0
    ['bayestar.multiorder.fits,0',
     'bayestar.fits.gz,1',
     'fermi_skymap.multiorder.fits,2',
     'glg_healpix_all_bn_v00.fit,0'])
def test_get_skymap_filename(monkeypatch, filename):
    # Define mock classes to call    
    class log(object):
        def __init__(self, graceid):
            pass
        def json(self):
            return {'log': [{'filename': filename.split(',')[0],
                             'file_version': filename.split(',')[1]}]}
    class mock_gracedb(object):
        def __init__(self):
            pass
        def logs(self, graceid):
            return log(graceid)

    result = get_skymap_filename('S1', 'bayestar' in filename,
                                 gracedb=mock_gracedb())
    assert result == filename


@pytest.mark.parametrize(
    'is_gw',
     # End search since searched time is 0
    [True, False])
def test_get_skymap_filename_empty(monkeypatch, is_gw):
    # Define mock classes to call    
    class log(object):
        def __init__(self, graceid):
            pass
        def json(self):
            return {'log': []}
    class mock_gracedb(object):
        def __init__(self):
            pass
        def logs(self, graceid):
            return log(graceid)

    result = get_skymap_filename('S1', is_gw,
                                 gracedb=mock_gracedb())
    assert result == None

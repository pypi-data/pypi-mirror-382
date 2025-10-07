from unittest.mock import call, patch
import unittest.mock as mock
#from unittest.mock import Mock
import math as mth
import os
import pytest
import re
import subprocess
import sys
import tempfile

#from ligo import raven
from ligo.gracedb.rest import GraceDb
from ligo.raven.tests.mock_gracedb_rest import MockGracedb as mock_gracedb_rest


GW170817_overlap = 32.28666563951095


def test_bin_raven_query():

    try:
        result = subprocess.run([
            "raven_query",
            "-e", "Superevent",
            "-t", "100",
            "-w", "-5", "1",
            "-u", "ligo/raven/tests/data/GW170817/test-gw-search.csv",
            "-g", "CBC",
            "-S", "AllSky"],
            check=True, capture_output=True, text=True)
    except subprocess.CalledProcessError as error:
        print(error.stdout)
        print(error.stderr)
        raise error

    # Assert that the output is as expected
    assert result.returncode == 0
    # Ensure the correct event has been found in printed results
    stdout = result.stdout
    assert get_value('superevent_id', stdout) == 'S170817a'
    assert float(get_value('t_0', stdout)) == 100.
    assert float(get_value('far', stdout)) == 1e-7
    assert get_value('labels', stdout) == '[]'
    assert get_value('skymap', stdout) == \
        'ligo/raven/tests/data/GW170817/GW170817.multiorder.fits'
    assert get_value('preferred_event', stdout) == 'G1'
    assert get_value('group', stdout) == 'CBC'
    assert get_value('search', stdout) == 'AllSky'


def test_bin_raven_search():

    try:
        result = subprocess.run([
            "raven_search",
            "-i", "S170817a",
            "-w", "-1", "5",
            "-u", "ligo/raven/tests/data/GW170817/test-gw-search.csv",
            "-U", "ligo/raven/tests/data/GW170817/test-grb-search.csv",
            "-p", "Fermi",
            "-s", "GRB"],
            check=True, capture_output=True, text=True)
    except subprocess.CalledProcessError as error:
        print(error.stdout)
        print(error.stderr)
        raise error

    # Assert that the output is as expected
    assert result.returncode == 0
    # Ensure the correct event has been found in printed results
    stdout = result.stdout
    assert get_value('graceid', stdout) == 'E170817'
    assert float(get_value('gpstime', stdout)) == 102.0
    assert get_value('pipeline', stdout) == 'Fermi'
    assert get_value('search', stdout) == 'GRB'
    assert get_value('labels', stdout) == '[]'
    assert get_value('skymap', stdout) == \
        'ligo/raven/tests/data/GW170817/glg_healpix_all_bn_v00.fit'
    assert float(get_value('ra', stdout)) == 0.
    assert float(get_value('dec', stdout)) == 0.
    assert float(get_value('error_radius', stdout)) == 15.0


def test_bin_raven_coinc_far():

    try:
        result = subprocess.run([
            "raven_coinc_far",
            "-f", "1e-7",
            "-w", "-1", "5",
            "-j", "untargeted",
            "-n", "1e-5",
            "-S", "ligo/raven/tests/data/GW170817/GW170817.multiorder.fits",
            "-E", ("ligo/raven/tests/data/GW170817/glg_healpix_all_bn_v00"
                   ".multiorder.fits")],
            check=True, capture_output=True, text=True)
    except subprocess.CalledProcessError as error:
        print(error.stdout)
        print(error.stderr)
        raise error

    # Assert that the output is as expected
    assert result.returncode == 0
    # Ensure the correct event has been found in printed results
    stdout = result.stdout
    assert mth.isclose(float(get_value('temporal_coinc_far', stdout)),
                       6e-12)
    assert mth.isclose(float(get_value('spatiotemporal_coinc_far', stdout)),
                       6e-12 / GW170817_overlap)
    assert mth.isclose(float(get_value('skymap_overlap', stdout)),
                       GW170817_overlap)


def test_bin_raven_calc_signif_gracedb():

    try:
        result = subprocess.run([
            "raven_calc_signif_gracedb",
            "-s", "S170817a",
            "-e", "E170817",
            "-w", "-1", "5",
            "-u", "ligo/raven/tests/data/GW170817/test-gw-search.csv",
            "-U", "ligo/raven/tests/data/GW170817/test-grb-search.csv",
            "-j", "untargeted",
            "-n", "1e-5",
            "-S", "ligo/raven/tests/data/GW170817/GW170817.multiorder.fits",
            "-E", "ligo/raven/tests/data/GW170817/glg_healpix_all_bn_v00.fit",
            "-m"],
            check=True, capture_output=True, text=True)
    except subprocess.CalledProcessError as error:
        print(error.stdout)
        print(error.stderr)
        raise error

    # Assert that the output is as expected
    assert result.returncode == 0
    # Ensure the correct event has been found in printed results
    stdout = result.stdout
    assert mth.isclose(float(get_value('temporal_coinc_far', stdout)),
                       6e-12)
    assert mth.isclose(float(get_value('spatiotemporal_coinc_far', stdout)),
                       6e-12 / GW170817_overlap, rel_tol=1e-8)
    assert mth.isclose(float(get_value('skymap_overlap', stdout)),
                       GW170817_overlap, rel_tol=1e-8)
    assert get_value('preferred_event', stdout) == 'G1'
    assert get_value('external_event', stdout) == 'E170817'


def test_bin_raven_skymap_overlap():

    try:
        result = subprocess.run([
            "raven_skymap_overlap",
            "-i", "ligo/raven/tests/data/GW170817/GW170817.multiorder.fits",
            "ligo/raven/tests/data/GW170817/glg_healpix_all_bn_v00.fit",
            "-m"],
            check=True, capture_output=True, text=True)
    except subprocess.CalledProcessError as error:
        print(error.stdout)
        print(error.stderr)
        raise error

    # Assert that the output is as expected
    assert result.returncode == 0
    # Ensure the correct event has been found in printed results
    stdout = result.stdout
    assert mth.isclose(float(get_value('Skymap overlap integral', stdout)),
                       GW170817_overlap, rel_tol=1e-8)


def test_bin_raven_offline_search():

    with tempfile.TemporaryDirectory() as tmpdirname:
        try:
            result = subprocess.run([
                "raven_offline_search",
                "-i", "ligo/raven/tests/data/GW170817/test-gw-search.csv",
                "ligo/raven/tests/data/GW170817/test-grb-search.csv",
                "-o", str(tmpdirname),
                "-t", "0", "200",
                "-w", "-1", "5",
                "-r", "1e-5",
                "-n", "4",
                "-j", "untargeted",
                "-g", "CBC",
                "-s", "GRB"],
                check=True, capture_output=True, text=True)
        except subprocess.CalledProcessError as error:
            print(error.stdout)
            print(error.stderr)
            raise error

        files_in_dir = os.listdir(tmpdirname)
        assert set(['output_log.txt',
                    'all_far.png',
                    'Coincidence_far.png',
                    'Coincidence_spat_far.png',
                    'results.csv']) \
                == set(files_in_dir)


def get_value(key, string):
    """Analyze string and grab value following a given key."""
    # Try once with standard dict like format with 'key'
    try:
        result = re.search(r"{}': ([A-Za-z0-9\.'-\[\]_]+)".format(key),
                           string).group(1).replace("'", "")
        # Replace some extra characters
        if ',' in result:
            result = result.replace(',', '')
        if '}' in result:
            result = result.split('}')[0]
        return result
    # If failure, try once again without surrounding string characters
    except AttributeError:
        try:
            result = re.search(r"{}: ([A-Za-z0-9\.'-\[\]]+)".format(key),
                               string).group(1)
            return result
        # If still nothing, return None
        except AttributeError:
            return None

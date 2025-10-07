from unittest.mock import call, patch
import unittest.mock as mock
import pytest
from math import isclose

import os
import sys
import healpy as hp
import numpy as np
from numpy import deg2rad as rads
import pytest
from scipy import integrate

from ligo.skymap import io, distance
from astropy.coordinates import ICRS, SkyCoord
from astropy import units as u
from astropy_healpix import HEALPix, nside_to_level, pixel_resolution_to_nside

from ligo.raven.search import skymap_overlap_integral


### Functions to create/combine sky maps ###
############################################


def from_cone(ra, dec, error):
    """ Create a gaussian sky map centered on the given ra, dec
    with width determined by 1-sigma error radius. """ 
    center = SkyCoord(ra * u.deg, dec * u.deg)
    radius = error * u.deg

    # Determine resolution such that there are at least
    # 4 pixels across the error radius.
    hpx = HEALPix(pixel_resolution_to_nside(radius / 4, round='up'),
                  'nested', frame=ICRS())
    nside = hpx.nside
    npix2 = hp.nside2npix(nside)
    ipix = np.arange(npix2)

    # Evaluate Gaussian.
    distance = hpx.healpix_to_skycoord(ipix).separation(center)
    probdensity = np.exp(-0.5 * np.square(distance / radius).to_value(
        u.dimensionless_unscaled))
    probdensity /= probdensity.sum() * hpx.pixel_area.to_value(u.steradian)
    
    return probdensity, nside

    
def make_skymap(nside, skymap_type, hemi=(1,0,0), ra=0, dec=0, error=10):
    
    npix2 = hp.nside2npix(nside)
    
    if skymap_type == 'hemi':
        m1 = np.zeros(npix2)
        disc_idx = hp.query_disc(nside, hemi, np.pi / 2, nest=True)
        m1[disc_idx] = 1   
    elif skymap_type =='allsky':
        m1 = np.full(npix2 ,1.)
    elif skymap_type =='cone':
        m1, nside = from_cone(ra, dec, error)
    else:
        raise AssertionError
        
    m1 /= m1.sum()
    return m1, nside


### Functions to calculate overlap integrals by numerical integration ###
#########################################################################


def angdist(alpha, delta, alpha0=0, delta0=0):
    x = np.cos(delta)*np.cos(delta0)+np.sin(delta)*np.sin(delta0)*np.cos(alpha-alpha0)
    # Make sure all values are valid and remap deviations due to numerical errors
    x = np.piecewise(x, [x < 1., x > 1., ((x <= 1.) & (x >= -1.))], [-1, 1, lambda dist: dist])
    return np.arccos(x)


def gaussian_probdensity(alpha, delta, alpha0, delta0, omega0):
    return np.exp(-.5*(angdist(alpha, delta, alpha0=alpha0, delta0=delta0)/omega0)**2.0)


def gaussian_probdensity_integrand(alpha, delta, alpha0, delta0, omega0):    
    return gaussian_probdensity(alpha, delta, alpha0, delta0, omega0)*np.sin(delta)


def gaussian_overlap_integrand(alpha, delta, alpha0, delta0, omega0, alpha00, delta00, omega00):
    return (gaussian_probdensity(alpha, delta, alpha0, delta0, omega0) * 
    gaussian_probdensity(alpha, delta, alpha00, delta00, omega00) * np.sin(delta))


def gaussian_overlap_integral(alpha0, alpha00, delta0, delta00, omega0, omega00):    
    numerator = 4 * np.pi*integrate.nquad(gaussian_overlap_integrand,[[0, 2*np.pi], [0, np.pi]], args=(alpha0,delta0,omega0,alpha00,delta00,omega00))[0]
    denominator = (integrate.nquad(gaussian_probdensity_integrand,[[0, 2*np.pi], [0, np.pi]], args=(alpha0,delta0,omega0))[0] * 
                   integrate.nquad(gaussian_probdensity_integrand,[[0, 2*np.pi], [0, np.pi]], args=(alpha00,delta00,omega00))[0])
    
    answer = numerator/denominator
    return answer


### Start tests ###
###################

@pytest.mark.parametrize(
    'test_type',
     ['no-overlap-hemi','allsky','allsky-hemi','same-hemi','concentric-gaussians',
      'noncoincident-gaussians','gaussian-hemi'])
def test_overlap_integrals_basic(test_type):
    
    # generate a sky map
    if test_type == 'no-overlap-hemi':
        m1, nside1 = make_skymap(32, 'hemi', hemi=(1,0,0))
        m2, nside2 = make_skymap(64, 'hemi', hemi=(-1,0,0))
        expected_overlap = 0.003916
    elif test_type == 'allsky':
        m1, nside1 = make_skymap(16, 'allsky')
        m2, nside2 = make_skymap(16, 'allsky')
        expected_overlap = 1
    elif test_type == 'allsky-hemi':
        m1, nside1 = make_skymap(32, 'allsky')
        m2, nside2 = make_skymap(64, 'hemi', hemi=(0,1,0))
        expected_overlap = 1
    elif test_type == 'same-hemi':
        m1, nside1 = make_skymap(64, 'hemi', hemi=(1,0,0))
        m2, nside2 = make_skymap(32, 'hemi', hemi=(1,0,0))
        expected_overlap = 2
    elif test_type == 'concentric-gaussians':
        ra1, ra2, dec1, dec2, error1, error2 = 180, 180, 0, 0, 10, 5
        m1, nside1 = make_skymap(16, 'cone', ra=ra1, dec=dec1, error=error1)
        m2, nside2 = make_skymap(16, 'cone', ra=ra1, dec=dec2, error=error2)
        expected_overlap = gaussian_overlap_integral(rads(ra1), rads(ra2), rads(dec1)+np.pi/2,
                                            rads(dec2)+np.pi/2, rads(error1), rads(error2))
    elif test_type == 'noncoincident-gaussians':
        ra1, ra2, dec1, dec2, error1, error2 = 180, 0, 0, 45, 15, 15
        m1, nside1 = make_skymap(16, 'cone', ra=ra1, dec=dec1, error=error1)
        m2, nside2 = make_skymap(16, 'cone', ra=ra2, dec=dec2, error=error2)
        expected_overlap = gaussian_overlap_integral(rads(ra1), rads(ra2), rads(dec1)+np.pi/2,
                                            rads(dec2)+np.pi/2, rads(error1), rads(error2))    
    elif test_type == 'gaussian-hemi':
        ra1, dec1, error1 = 270, 0, 1
        m1, nside1 = make_skymap(16, 'cone', ra=ra1, dec=dec1, error=error1)
        m2, nside2 = make_skymap(32, 'hemi', hemi=(0,-1,0))
        expected_overlap = 2
    
    # calculate spatial overlap integral and compare to expected value
    assert isclose(skymap_overlap_integral(m1, m2), expected_overlap, rel_tol=.1)


@pytest.mark.parametrize('gw_filename,ext_filename',
    [['hemi-1', 'hemi-2'],
     ['hemi-1', 'point-2'],
     ['point-1', 'hemi-2'],
     ['point-1', 'point-2']])
def test_overlap_integral_zero(gw_filename, ext_filename):
    if gw_filename == 'hemi-1':
        skymap1 = np.array([1/6, 1/6, 1/6, 1/6, 1/6, 1/6,
                            0, 0, 0, 0, 0, 0])
    elif gw_filename == 'point-1':
        skymap1 = np.full(12, 0)
        skymap1[0] = 1.
    
    if ext_filename == 'hemi-2':
        skymap2 = np.array([0, 0, 0, 0, 0, 0,
                            1/6, 1/6, 1/6, 1/6, 1/6, 1/6])
    elif ext_filename == 'point-2':
        skymap2 = np.full(12, 0)
        skymap2[6] = 1.

    assert isclose(skymap_overlap_integral(skymap1, skymap2), 0, rel_tol=.001)


### Test multi-ordered sky maps###
@pytest.mark.parametrize(
    'gw_filename,ext_filename',
    [['flat-skymap.fits.gz', 'flat-skymap.fits.gz'],
     ['flat-skymap.multiorder.fits', 'flat-skymap.fits.gz'],
     ['flat-skymap.multiorder.fits', 'flat-skymap.multiorder.fits'],
     ['flat-skymap.fits.gz', 'fermi_test_skymap.fits.gz'],
     ['flat-skymap.fits.gz', 'swift_test_skymap.fits.gz'],
     ['flat-skymap.fits.gz', ''],
     ['flat-skymap.multiorder.fits', ''],
     ['bayestar.multiorder.fits', 'flat-skymap.fits.gz'],
     ['bayestar.multiorder.fits', 'flat-skymap.multiorder.fits']])
def test_overlap_integrals_moc(gw_filename, ext_filename):

    path = 'ligo/raven/tests/data/basic_skymaps/'
    use_radec = ext_filename == ''
    gw_filename = path + gw_filename
    ext_filename = path + ext_filename

    gw_moc = 'multiorder' in gw_filename
    ext_moc = 'multiorder' in ext_filename
    ra, dec = None, None
    if gw_moc:
        gw_skymap = io.read_sky_map(gw_filename, moc=gw_moc, nest=True)
    else:
        gw_skymap, header = io.read_sky_map(gw_filename, moc=gw_moc, nest=True)

    if use_radec:
        ra, dec = 0., 0.
        ext_skymap = None
    elif ext_moc:
        ext_skymap = io.read_sky_map(ext_filename, moc=ext_moc)
    else:
        ext_skymap, header = io.read_sky_map(ext_filename, moc=ext_moc, nest=True)

    assert isclose(skymap_overlap_integral(gw_skymap, ext_skymap,
                                           gw_nested=True, ext_nested=True,
                                           ra=ra, dec=dec),
                   1.0, rel_tol=.00001)


### Test GW170817 related sky maps ###

@pytest.mark.parametrize(
    'gw_filename,ext_filename',
    [['GW170817.fits.gz', 'glg_healpix_all_bn_v00.fit'],
     ['GW170817.multiorder.fits', 'glg_healpix_all_bn_v00.fit'],
     ['GW170817.multiorder.fits', 'glg_healpix_all_bn_v00.multiorder.fits']])
def test_overlap_integrals_GW170817(gw_filename, ext_filename):

    path = 'ligo/raven/tests/data/GW170817/'
    gw_filename = path + gw_filename
    ext_filename = path + ext_filename

    gw_moc = 'multiorder' in gw_filename
    ext_moc = 'multiorder' in ext_filename
    if gw_moc:
        gw_skymap = io.read_sky_map(gw_filename, moc=gw_moc, nest=True)
    else:
        gw_skymap, header = io.read_sky_map(gw_filename, moc=gw_moc, nest=True)
    if ext_moc:
        ext_skymap = io.read_sky_map(ext_filename, moc=ext_moc)
    else:
        ext_skymap, header = io.read_sky_map(ext_filename, moc=ext_moc, nest=True)

    assert isclose(skymap_overlap_integral(gw_skymap, ext_skymap,
                                           gw_nested=True, ext_nested=True),
                   32.286, rel_tol=.01)
    # Note the difference compared to 32.4 (10.3847/1538-4357/aabfd2) due to
    # using different sky maps


@pytest.mark.parametrize(
    'gw_filename',
    ['GW170817.fits.gz', 'GW170817.multiorder.fits'])
def test_overlap_integrals_NGC4993(gw_filename):

    path = 'ligo/raven/tests/data/GW170817/'
    gw_filename = path + gw_filename
    # Location of NGC4993 from https://en.wikipedia.org/wiki/NGC_4993
    c = SkyCoord('13h09m48.09s', '−23° 22′ 53.3″')
    ra_em, dec_em = c.ra.value, c.dec.value

    gw_moc = True if 'multiorder' in gw_filename else False
    if gw_moc:
        gw_skymap = io.read_sky_map(gw_filename, moc=gw_moc, nest=True)
    else:
        gw_skymap, header = io.read_sky_map(gw_filename, moc=gw_moc, nest=True)

    assert isclose(skymap_overlap_integral(gw_skymap,
                                           ra=ra_em, dec=dec_em, gw_nested=True),
                   1430.6, rel_tol=.001)


# Project Librarian: Brandon Piotrzkowski
#              Staff Scientist
#              UW-Milwaukee Department of Physics
#              Center for Gravitation & Cosmology
#              <brandon.piotrzkowski@ligo.org>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

"""
Module to define functions and attributes corresponding
to both gravitational-wave candidates and external triggers.
"""
__author__ = "Alex Urban <alexander.urban@ligo.org>"


# Imports.
import healpy as hp
import numpy as np
import tempfile

from astropy.io.fits import getheader
from astropy.table.table import Table
from ligo.gracedb.rest import GraceDb
from ligo.skymap.io import fits


#######################################################
# Define object classes for GWs and external triggers #
#######################################################

class ExtTrig(object):
    """ Instance of an external trigger event (e.g. gamma-ray burst)

    Parameters
    ----------
    graceid: str
        ID of the trigger used by GraceDB
    gracedb: class
        SDK or REST API client for HTTP connection
    event_dict: dict
        Dictionary of external event
    fitsfile: str
        External event's skymap file name
    is_moc: bool
        If True, assumes multi-order coverage (MOC) external event skymap.
        If None, reads the file to determine whether MOC
    use_radec: bool
        If True, use ra and dec for single pixel external skymap
    nested: bool
        If True, assumes external skymap uses nested ordering, otherwise
        assumes ring ordering
    """
    def __init__(self, graceid, gracedb=None, event_dict=None,
                 fitsfile=None, is_moc=None, use_radec=False, nested=True):
        self.is_gracedb_sdk = _is_gracedb_sdk(gracedb)
        self.is_gracedb_mock = _is_gracedb_mock(gracedb)
        self.graceid = graceid
        self.fits = fitsfile  # name of fits file
        self.neighbor_type = 'S'  # by default, look for superevents
        self.is_moc = is_moc
        self.use_radec = use_radec
        self.nested = nested

        # Initiate correct instance of GraceDb.
        if gracedb is None:
            self.gracedb = GraceDb()
        else:
            self.gracedb = gracedb

        # Check if event dictionary provided, otherwise
        # get other properties from GraceDb.
        if event_dict:
            event = event_dict
        else:
            if self.is_gracedb_sdk:
                event = self.gracedb.events[graceid].get()
            else:
                event = self.gracedb.event(graceid).json()
        self.inst = event['pipeline']  # instrument that detected the event
        self.search = event['search']
        self.far = event.get('far')
        self.gpstime = float(event['gpstime'])  # event time in GPS seconds

        self.skymap = None
        self.ra, self.dec = None, None
        # If prompted, use RA/dec method to calculate overlap
        if use_radec:
            self.ra = event['extra_attributes']['GRB']['ra']
            self.dec = event['extra_attributes']['GRB']['dec']

        # If using a mocked GraceDB class, try to load sky map locally
        elif self.fits and self.is_gracedb_mock:
            # If not determined, read file to figure out whether MOC or not
            if self.is_moc is None:
                self.is_moc = is_skymap_moc(fitsfile)
            self.skymap = load_skymap(fitsfile, is_moc=self.is_moc,
                                      nested=nested)

        # Otherwise, try to load sky map from GraceDB
        elif self.fits:
            kwargs = {'mode': 'w+b'}
            with tempfile.NamedTemporaryFile(**kwargs) as skymapfile:
                if self.is_gracedb_sdk:
                    skymap = \
                        self.gracedb.events[
                            self.graceid].files[self.fits].get().read()
                else:
                    skymap = self.gracedb.files(self.graceid, self.fits,
                                                raw=True).read()
                skymapfile.write(skymap)
                skymapfile.flush()
                skymapfile.seek(0)
                # If not determined, read file to figure out whether MOC or not
                if self.is_moc is None:
                    self.is_moc = is_skymap_moc(skymapfile.name)
                self.skymap = load_skymap(skymapfile.name,
                                          is_moc=self.is_moc,
                                          nested=nested)

    def submit_gracedb_log(self, message, filename=None, filecontents=None,
                           tags=[]):
        """ Upload log to GraceDB for this event

        Parameters
        ----------
        message: str
            Log message to upload
        filename: class
            Name of file to upload
        filecontents: bytes
            Contents of file to upload in bytes
        tags: list
            List of tags to include in log message"""
        if self.is_gracedb_sdk:
            self.gracedb.events[self.graceid].logs.create(
                comment=message,
                filename=filename,
                filecontents=filecontents,
                tags=tags)
        else:
            self.gracedb.writeLog(
                self.graceid,
                message=message,
                filename=filename,
                filecontents=filecontents,
                tag_name=tags)


class SE(object):
    """Instance of a superevent

    Parameters
    ----------
    graceid: str
        ID of the trigger used by GraceDB
    gracedb: class
        SDK or REST API client for HTTP connection
    event_dict: dict
        Dictionary of superevent
    fitsfile: str
        GW's skymap file name
    is_moc: bool
        If True, assumes multi-order coverage (MOC) GW skymap.
        If None, reads the file to determine whether MOC
    nested: bool
        If True, assumes GW skymap uses nested ordering, otherwise
        assumes ring ordering
    """
    def __init__(self, superevent_id, event_dict=None, gracedb=None,
                 fitsfile=None, is_moc=None, nested=True,
                 use_preferred_event_skymap=False):
        self.is_gracedb_sdk = _is_gracedb_sdk(gracedb)
        self.is_gracedb_mock = _is_gracedb_mock(gracedb)
        self.graceid = superevent_id
        self.neighbor_type = 'E'
        self.fits = fitsfile  # name of fits file
        self.is_moc = is_moc
        self.nested = nested

        if gracedb is None:
            self.gracedb = GraceDb()
        else:
            self.gracedb = gracedb

        # Check if event dictionary provided, otherwise
        # get other properties from GraceDb.
        if event_dict:
            superevent = event_dict
        else:
            if self.is_gracedb_sdk:
                superevent = self.gracedb.superevents[superevent_id].get()
            else:
                superevent = self.gracedb.superevent(superevent_id).json()
        self.preferred_event = superevent['preferred_event']
        self.far = superevent['far']
        self.gpstime = superevent['t_0']

        self.skymap = None
        # If using a mocked GraceDB class, try to load sky map locally
        if self.fits and self.is_gracedb_mock:
            # If not determined, read file to figure out whether MOC or not
            if self.is_moc is None:
                self.is_moc = is_skymap_moc(fitsfile)
            self.skymap = load_skymap(fitsfile, is_moc=self.is_moc,
                                      nested=nested)

        elif self.fits:
            # self.sky_map = fits.read_sky_map( self.fits )
            kwargs = {'mode': 'w+b'}
            with tempfile.NamedTemporaryFile(**kwargs) as skymapfile:
                skymap_graceid = \
                    (self.preferred_event if
                     use_preferred_event_skymap else self.graceid)
                if self.is_gracedb_sdk:
                    skymap = \
                        self.gracedb.events[skymap_graceid].files[
                            self.fits].get().read()
                else:
                    skymap = self.gracedb.files(skymap_graceid,
                                                self.fits, raw=True).read()
                skymapfile.write(skymap)
                skymapfile.flush()
                skymapfile.seek(0)
                # If not determined, read file to figure out whether MOC or not
                if self.is_moc is None:
                    self.is_moc = is_skymap_moc(skymapfile.name)
                self.skymap = load_skymap(skymapfile.name,
                                          is_moc=self.is_moc,
                                          nested=nested)

    def submit_gracedb_log(self, message, filename=None, filecontents=None,
                           tags=[]):
        """ Upload log to GraceDB for this event

        Parameters
        ----------
        message: str
            Log message to upload
        filename: class
            Name of file to upload
        filecontents: bytes
            Contents of file to upload in bytes
        tags: list
            List of tags to include in log message"""
        if self.is_gracedb_sdk:
            self.gracedb.superevents[self.graceid].logs.create(
                comment=message,
                filename=filename,
                filecontents=filecontents,
                tags=tags)
        else:
            self.gracedb.writeLog(
                self.graceid,
                message=message,
                filename=filename,
                filecontents=filecontents,
                tag_name=tags)


def _is_gracedb_sdk(gracedb):
    # Only gracedb-sdk has this attribue, which REST has _service_url
    return hasattr(gracedb, 'url') if gracedb else False


def _is_gracedb_mock(gracedb):
    # Only gracedb-sdk has this attribue, which REST has _service_url
    return hasattr(gracedb, 'mock_gracedb') if gracedb else False


def _get_gracedb_url(gracedb):
    return gracedb.url if _is_gracedb_sdk(gracedb) else gracedb._service_url


def load_skymap(filename, is_moc=True, nested=True):
    if is_moc:
        skymap = fits.read_sky_map(filename, moc=is_moc)

    else:
        try:
            skymap, h = fits.read_sky_map(filename,
                                          moc=is_moc,
                                          nest=nested)
        except KeyError:
            skymap = hp.read_map(filename,
                                 nest=nested)
    return skymap


def is_skymap_moc(skymap):
    # If path to sky map, load and check
    if isinstance(skymap, str):
        return getheader(skymap, ext=1)['INDXSCHM'] == 'EXPLICIT'
    # Array-like should be flattened
    elif isinstance(skymap, (np.ndarray, list)):
        return False
    # Table should be MOC
    elif isinstance(skymap, Table):
        return True
    else:
        raise AssertionError(f'Non-supported variable type: {type(skymap)}')

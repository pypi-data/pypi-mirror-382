from astropy.table import Table
from numpy.ma.core import MaskedConstant
from ligo.gracedb.rest import GraceDb
import numpy as np
import unittest.mock as mock
import validators

from astropy.utils.data import get_file_contents


class MockGraceDb(object):
    """Mock GraceDB class meant to be similar and callable like
    ligo.gracedb.rest.GraceDb but being populated by a given file, such as
    .csv.

    Parameters
    ----------
    input : str
        Path to file, such as .csv, to create mock GraceDB class from or data
        in JSON format

    """
    def __init__(self, input):
        self._service_url = 'https://gracedb-mock.org/api/'
        # If string, read as filename
        if isinstance(input, str):
            self.data = Table.read(input)
        # If dict, treat as single event
        elif isinstance(input, dict):
            self.data = Table([input])
        elif isinstance(input, list) or isinstance(input, np.ndarray):
            self.data = Table(input)
        else:
            raise TypeError(
                f"""
                Not a valid input: {input}.\nMust be a string, dict, or
                array-like (list or numpy array).
                """)
        self.mock_gracedb = True

    def events(self, args):
        """Query mock database for external events.

        Parameters
        ----------
        args : str
            String to perform query, in the format of 'group start_time ..
            end_time search pipeline far_cutoff'

        Returns
        -------
        results : list
            List of event dictonaries

        """
        print("Performed search with {}".format(args))
        arg_list = args.split(' ')
        tl, th = float(arg_list[1]), float(arg_list[3])
        # Try to grab values, is missing then pass None
        search = get_list_item(arg_list, 4)
        pipeline = get_list_item(arg_list, 5)
        far_eq = get_list_item(arg_list, 6)
        results = []
        mask = (tl < self.data['gpstime']) * (self.data['gpstime'] < th)
        # Apply additional filters if given
        if search:
            mask *= self.data['search'] == search
        if pipeline:
            mask *= self.data['pipeline'] == pipeline
        if far_eq:
            mask *= (self.data['far'] < float(far_eq.split('<')[1]))
        for result in self.data[mask]:
            results.append({"graceid": to_str(result.get('graceid')),
                            "gpstime": to_float(result.get('gpstime')),
                            "pipeline": to_str(result.get('pipeline')),
                            "search": to_str(result.get('search')),
                            "far": to_float(result.get('far')),
                            "labels": [],
                            "skymap": to_str(result.get('skymap')),
                            "extra_attributes": {
                                "GRB": {
                                    "ra": to_float(result.get('ra')),
                                    "dec": to_float(result.get('dec')),
                                    "error_radius": to_float(result.get(
                                        'error_radius'))}}})
        return results

    def superevents(self, args):
        """Query mock database for superevents.

        Parameters
        ----------
        args : str
            String to perform query, in the format of 'start_time .. end_time
            far_cutoff'

        Returns
        -------
        results : list
            List of superevent dictonaries

        """
        print("Performed search with {}".format(args))
        arg_list = args.split(' ')
        tl, th = float(arg_list[0]), float(arg_list[2])
        results = []
        mask = (tl < self.data['t_0']) * (self.data['t_0'] < th)
        # Apply additional filters if given
        try:
            mask *= (self.data['far'] < float(arg_list[3].split('<')[1]))
        except IndexError:
            pass
        for result in self.data[mask]:
            results.append({"superevent_id": to_str(result.get(
                                                 'superevent_id')),
                            "t_0": to_float(result.get('t_0')),
                            "far": to_float(result.get('far')),
                            "labels": [],
                            "skymap": to_str(result.get('skymap')),
                            "preferred_event": to_str(result.get(
                                                   'preferred_event')),
                            "preferred_event_data":
                            {"group": to_str(result.get('group')),
                             "search": to_str(result.get('search'))}})
        return results

    def superevent(self, graceid):
        return mock_superevent(graceid, data=self.data)

    def event(self, graceid):
        return mock_event(graceid, data=self.data)

    def files(self, graceid, filename, raw=True):
        return File(filename)

    @mock.create_autospec
    def writeLog(self, *args, **kwargs):
        print("Sent log message")
        return


class Files(object):
    """Load up File class to recreate the calls in the GraceDB REST API."""
    def __init__(self, file):
        self.file = file

    def get(self):
        return File(self.file)


class File(object):
    """Load files by pointing to local path."""
    def __init__(self, file):
        self.file = file

    def read(self):
        return get_file_contents('ligo/raven/tests/data/GW170817/' + self.file,
                                 encoding='binary', cache=False)


class mock_event(object):
    """Return event from mock database, as well as mock up other calls that
    could be performed for an individual event.

    Parameters
    ----------
    graceid : str
        GraceDB ID
    data : Table
        Mock GraceDB database to populate result from

    """
    def __init__(self, graceid, data=None):
        self.graceid = graceid
        self.data = data
        self.logs = self.logs()
        self.files = self.files()

    def json(self):
        result = self.data[self.data['graceid'] == self.graceid][0]
        return {"graceid": to_str(result.get('graceid')),
                "gpstime": to_float(result.get('gpstime')),
                "pipeline": to_str(result.get('pipeline')),
                "search": to_str(result.get('search')),
                "far": to_float(result.get('far')),
                "labels": [],
                "skymap": to_str(result.get('skymap')),
                "extra_attributes": {
                    "GRB": {
                        "ra": to_float(result.get('ra')),
                        "dec": to_float(result.get('dec')),
                        "error_radius": to_float(result.get('error_radius'))}}}

    class logs(object):
        """Mock dummy logs class."""
        @mock.create_autospec
        def create(*args, **kwargs):
            print("Sent log message")
            return

    class files(object):
        """Load up Files class to recreate the calls in GraceDB REST API."""
        def __getitem__(self, file):
            """Dummy call for class."""
            return Files(file)


class mock_superevent(object):
    """Return superevent from mock database, as well as mock up other calls
    that could be performed for an individual superevent.

    Parameters
    ----------
    graceid : str
        GraceDB ID
    data : Table
        Mock GraceDB database to populate result from

    """
    def __init__(self, graceid, data=None):
        self.superevent_id = graceid
        self.data = data
        self.logs = self.logs()
        self.files = self.files()

    def json(self):
        result = self.data[self.data['superevent_id'] == self.superevent_id][0]
        return {"superevent_id": to_str(result.get('superevent_id')),
                "t_0": to_float(result.get('t_0')),
                "far": to_float(result.get('far')),
                "labels": [],
                "skymap": to_str(result.get('skymap')),
                "preferred_event": to_str(result.get('preferred_event')),
                "preferred_event_data":
                {"group": to_str(result.get('group')),
                 "search": to_str(result.get('search'))}}

    class logs(object):
        """Mock dummy logs class."""
        @mock.create_autospec
        def create(*args, **kwargs):
            print("Sent log message")
            return

    class files(object):
        """Load up Files class to recreate the calls in GraceDB REST API."""
        def __getitem__(self, file):
            """Dummy call for class."""
            return Files(file)


def is_string_a_url(url_string):
    """Takes URL string and returns True or False whether a string is a URL."""
    result = validators.url(url_string)
    # result is True if URL, else is Django ValidationError
    if isinstance(result, bool):
        return result
    return False


def choose_gracedb(path):
    """Determine whether the input given is from an official GraceDB online
       server or from a local file.

    Parameters
    ----------
    path : str
        Either GraceDB API URL or path to local local

    Returns
    -------
    GraceDB: class
        GraceDB class instance, either official online or mock offline

    """
    # If no path, use default GraceDB instance
    if path is None:
        return GraceDb()
    # If clearly a GraceDB API UR (or any URL), use official GraceDB API
    elif is_string_a_url(path):
        return GraceDb(path)
    # Otherwise use mock GraceDB to load local file
    else:
        return MockGraceDb(path)


def get_list_item(list, index):
    """Grab item from list at a given index, return None if missing."""
    try:
        return list[index]
    except IndexError:
        return None


def to_float(val):
    """Convert to float if present. If missing return None."""
    return float(val) if not isinstance(val, MaskedConstant) and \
        val is not None else None


def to_str(val):
    """Convert to string if not None. If None return None."""
    result = str(val) if val is not None else None
    if result is not None and result == '--':
        return None
    return result

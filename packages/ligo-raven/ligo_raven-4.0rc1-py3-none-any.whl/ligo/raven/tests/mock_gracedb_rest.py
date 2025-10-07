import unittest.mock as mock

from astropy.coordinates import SkyCoord
from astropy.utils.data import get_file_contents

# Position of NGC 4993
c = SkyCoord('13h09m48.09s', '−23° 22′ 53.3″')
ra_em, dec_em = c.ra.value, c.dec.value

class mock_superevent(object):
    def __init__(self, graceid):
        self.graceid = graceid
        self.logs = self.logs()
        self.files = self.files()
    def json(self):
        if self.graceid == 'S100':
            return {"superevent_id": "S100",
                    "far": 1e-5,
                    "t_0": 100,
                    "preferred_event": "G1"}
        if self.graceid == 'S101':
            return {"superevent_id": "S101",
                    "far": 1e-7,
                    "t_0": 100,
                    "preferred_event": "G2"}
        if self.graceid == 'S102':
            return {"superevent_id": "S102",
                    "far": 1e-9,
                    "t_0": 100,
                    "preferred_event": "G3"}

    class logs(object):
        @mock.create_autospec
        def create(*args, **kwargs):
            print("Sent log message")
            return 
    class files(object):
        def __getitem__(self, file):
            return Files(file)


class mock_event(object):
    def __init__(self, graceid):
        self.graceid = graceid
        self.logs = self.logs()
        self.files = self.files()
    def json(self):
        if self.graceid == 'E0':
            return {"graceid": "E0",
                    "gpstime": 100.0,
                    "group": "External",
                    "pipeline": "NOT_REAL",
                    "search": "GRB"}
        if self.graceid == 'E1':
            return {"graceid": "E1",
                    "gpstime": 102.0,
                    "group": "External",
                    "pipeline": "Swift",
                    "search": "GRB",
                    "extra_attributes": {
                        "GRB": {
                            "ra": ra_em,
                            "dec": dec_em}}}
        if self.graceid == 'E2':
            return {"graceid": "E2",
                    "gpstime": 106.0,
                    "group": "External",
                    "pipeline": "SNEWS",
                    "search": "Supernova"}
        if self.graceid=='E3':
            return {"graceid": "E3",
                    "gpstime": 115.0,
                    "group": "External",
                    "pipeline": "Fermi",
                    "search": "SubGRB"}
        if self.graceid=='E4':
            return {"graceid": "E4",
                    "gpstime": 115.0,
                    "group": "External",
                    "pipeline": "Swift",
                    "search": "SubGRBTargeted",
                    "far": 1e-4,
                    "extra_attributes": {
                        "GRB": {
                            "ra": 20.,
                            "dec": 30.}}}
        if self.graceid=='M5':
            return {"graceid": "M5",
                    "gpstime": 104.0,
                    "group": "External",
                    "pipeline": "Fermi",
                    "search": "MDC"}
        if self.graceid=='E6':
            return {"graceid": "E6",
                    "gpstime": 109.0,
                    "group": "External",
                    "pipeline": "IceCube",
                    "search": "HEN"}
        if self.graceid=='E7':
            return {"graceid": "E7",
                    "gpstime": 100.0,
                    "group": "External",
                    "pipeline": "Fermi",
                    "search": "SubGRBTargeted",
                    "far": 1e-6}
    class logs(object):
        @mock.create_autospec
        def create(*args, **kwargs):
            print("Sent log message")
            return
    class files(object):
        def __getitem__(self, file):
            return Files(file)

        
class Files(object):
    def __init__(self, file):
        self.file = file
    def get(self):
        return File(self.file)

class File(object):
    def __init__(self, file):
        self.file = file
    def read(self):
        return get_file_contents('ligo/raven/tests/data/GW170817/' + self.file,
                                 encoding='binary', cache=False)
 

class MockGracedb(object):
    def __init__(self, url='https://gracedb-mock.org/api/'):
        self._service_url = url

    def events(self, args):
        print("Performed search with {}".format(args))
        arg_list = args.split(' ')
        tl, th = float(arg_list[1]), float(arg_list[3])
        results = []
        if tl <= 102 <= th:
            results.append({"graceid": "E1",
                            "gpstime": 102.0,
                            "pipeline": "Swift",
                            "group": "External",
                            "search": "GRB",
                            "extra_attributes": {
                                 "GRB": {
                                    "ra": 120.,
                                    "dec": 30.}}})
        if tl <= 106 <= th :
            results.append({"graceid": "E2",
                            "gpstime": 106.0,
                            "pipeline": "SNEWS",
                            "group": "External",
                            "search": "Supernova"})
        if tl <= 115 <= th:
            results.append({"graceid": "E3",
                            "gpstime": 115.0,
                            "pipeline": "Fermi",
                            "group": "External",
                            "search": "SubGRB"})
        if tl <= 99.5 <= th:
            results.append({"graceid": "E4",
                            "gpstime": 99.5,
                            "pipeline": "Fermi",
                            "group": "External",
                            "search": "SubGRB"})
        if (tl <= 100. <= th) and 'MDC' in args:
            results.append({"graceid": "E4",
                            "gpstime": 100.,
                            "pipeline": "Fermi",
                            "group": "External",
                            "search": "MDC"})
        return results
    def superevents(self, args):
        print("Performed search with {}".format(args))
        arg_list = args.split(' ')
        tl, th= float(arg_list[0]), float(arg_list[2])
        results = []
        if tl <= 100.5 <= th:
            results.append({"superevent_id": "S1",
                            "t_0": 100.5,
                            "far": 1e-7,
                            "preferred_event": "G1",
                            "preferred_event_data": 
                            {"group": "CBC",
                             "search": "AllSky"}})

        if tl <= 96 <= th:
            results.append({"superevent_id": "S2",
                            "t_0": 96.0,
                            "far": 1e-7,
                            "preferred_event": "G2",
                            "preferred_event_data":
                            {"group": "Burst",
                             "search": "AllSky"}})
        if tl <= 106 <= th:
            results.append({"superevent_id": "S3",
                            "t_0": 106.0,
                            "far": 1e-7,
                            "preferred_event": "G3",
                            "preferred_event_data":
                            {"group": "CBC",
                             "search": "AllSky"}})
        if (tl <= 100.5 <= th) and 'MDC' in args:
            results.append({"superevent_id": "S4",
                            "t_0": 100.5,
                            "far": 1e-8,
                            "preferred_event": "G4",
                            "preferred_event_data":
                            {"group": "CBC",
                             "search": "MDC"}})
        return results
    def superevent(self, graceid):
        return mock_superevent(graceid)
    def event(self, graceid):
        return mock_event(graceid)
    def files(self, graceid, filename, raw=True):
        return File(filename)
    @mock.create_autospec
    def writeLog(self, *args, **kwargs):
        print("Sent log message")
        return

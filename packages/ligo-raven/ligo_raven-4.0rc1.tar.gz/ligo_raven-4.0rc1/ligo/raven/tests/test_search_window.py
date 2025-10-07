from unittest.mock import call, patch
import unittest.mock as mock
import pytest

from ligo import raven


class GResponse(object):
    def __init__(self, graceid):
        self.graceid = graceid
    def json(self):
        return {"graceid": self.graceid}


class MockGracedb(object):
    def __init__(self, url='https://gracedb-mock.org/api/'):
        self._service_url = url

    def event(self, graceid):
        return GResponse(graceid)

    def superevents(self, args):
        print("Performed search with {}".format(args))
        arg_list = args.split('..')
        tl, th= float(arg_list[0]), float(arg_list[1])
        results = []
        if tl <= 999999995.5 <= th:
            results.append({"superevent_id": "S1",
                            "t_0": 999999995.5,
                            "preferred_event": "G1",
                            "preferred_event_data": 
                            {"group": "CBC"}})
        if tl <= 999999996.5 <= th:
            results.append({"superevent_id": "S2",
                            "t_0": 999999996.5,
                            "preferred_event": "G2",
                            "preferred_event_data": 
                            {"group": "CBC"}})
        if tl <= 999999997.5 <= th:
            results.append({"superevent_id": "S3",
                            "t_0": 999999997.5,
                            "preferred_event": "G3",
                            "preferred_event_data": 
                            {"group": "CBC"}})
        if tl <= 999999998.5 <= th:
            results.append({"superevent_id": "S4",
                            "t_0": 999999998.5,
                            "preferred_event": "G4",
                            "preferred_event_data": 
                            {"group": "CBC"}})
        if tl <= 999999999.5 <= th:
            results.append({"superevent_id": "S5",
                            "t_0": 999999999.5,
                            "preferred_event": "G5",
                            "preferred_event_data": 
                            {"group": "CBC"}})
        if tl <= 1000000000.5 <= th:
            results.append({"superevent_id": "S6",
                            "t_0": 1000000000.5,
                            "preferred_event": "G6",
                            "preferred_event_data": 
                            {"group": "CBC"}})
        if tl <= 1000000001.5 <= th:
            results.append({"superevent_id": "S7",
                            "t_0": 1000000001.5,
                            "preferred_event": "G7",
                            "preferred_event_data": 
                            {"group": "CBC"}})
        if tl <= 1000000002.5 <= th:
            results.append({"superevent_id": "S8",
                            "t_0": 1000000002.5,
                            "preferred_event": "G8",
                            "preferred_event_data": 
                            {"group": "Burst"}})
        if tl <= 1000000003.5 <= th:
            results.append({"superevent_id": "S9",
                            "t_0": 1000000003.5,
                            "preferred_event": "G9",
                            "preferred_event_data": 
                            {"group": "CBC"}})
        if tl <= 1000000004.5 <= th:
            results.append({"superevent_id": "S10",
                            "t_0": 1000000004.5,
                            "preferred_event": "G10",
                            "preferred_event_data": 
                            {"group": "CBC"}})
        for result in results:
            result['far'] = 1e-7
        return results

    @mock.create_autospec
    def writeLog(self, gid, message, tag_name=[],
                 filename=None, filecontents=None):
        return gid, message, tag_name, filename


def expected_results(event_type, gpstime, tl, th,
                 gracedb=None, group=None, pipelines=[]):
    if tl==-2 and (th==2 and group==None):
        return [{"superevent_id": "S4",
                 "t_0": 999999998.5,
                 "far":1e-7,
                 "preferred_event": "G4",
                 "preferred_event_data":
                 {"group": "CBC"}},
                {"superevent_id": "S5",
                 "t_0": 999999999.5,
                 "far":1e-7,
                 "preferred_event": "G5",
                 "preferred_event_data":
                 {"group": "CBC"}},
                {"superevent_id": "S6",
                 "t_0": 1000000000.5,
                 "far":1e-7,
                 "preferred_event": "G6",
                 "preferred_event_data":
                 {"group": "CBC"}},
                {"superevent_id": "S7",
                 "t_0": 1000000001.5,
                 "far":1e-7,
                 "preferred_event": "G7",
                 "preferred_event_data":
                 {"group": "CBC"}}]
    elif tl==-5 and (th==1 and group==None):
        return [{"superevent_id": "S1",
                 "t_0": 999999995.5,
                 "far":1e-7,
                 "preferred_event": "G1",
                 "preferred_event_data":
                 {"group": "CBC"}},
                {"superevent_id": "S2",
                 "t_0": 999999996.5,
                 "far":1e-7,
                 "preferred_event": "G2",
                 "preferred_event_data":
                 {"group": "CBC"}},
                {"superevent_id": "S3",
                 "t_0": 999999997.5,
                 "far":1e-7,
                 "preferred_event": "G3",
                 "preferred_event_data":
                 {"group": "CBC"}},
                {"superevent_id": "S4",
                 "t_0": 999999998.5,
                 "far":1e-7,
                 "preferred_event": "G4",
                 "preferred_event_data":
                 {"group": "CBC"}},
                {"superevent_id": "S5",
                 "t_0": 999999999.5,
                 "far":1e-7,
                 "preferred_event": "G5",
                 "preferred_event_data":
                 {"group": "CBC"}},
                {"superevent_id": "S6",
                 "t_0": 1000000000.5,
                 "far":1e-7,
                 "preferred_event": "G6",
                 "preferred_event_data":
                 {"group": "CBC"}}]
    elif tl==2 and th==5:
        return [{"superevent_id": "S8",
                 "t_0": 1000000002.5,
                 "far":1e-7,
                 "preferred_event": "G8",
                 "preferred_event_data":
                 {"group": "Burst"}},
                {"superevent_id": "S9",
                 "t_0": 1000000003.5,
                 "far":1e-7,
                 "preferred_event": "G9",
                 "preferred_event_data":
                 {"group": "CBC"}},
                {"superevent_id": "S10",
                 "t_0": 1000000004.5,
                 "far":1e-7,
                 "preferred_event": "G10",
                 "preferred_event_data":
                 {"group": "CBC"}}]
    elif group=='Burst':
        return [{"superevent_id": "S8",
                 "t_0": 1000000002.5,
                 "far":1e-7,
                 "preferred_event": "G8",
                 "preferred_event_data":
                 {"group": "Burst"}}]
    else:
        return [] 



@pytest.mark.parametrize(
    'gracedb_id, event_type,gpstime,tl,th, group',
    [['E1','Superevent', 1000000000, -2, 2, None],
     ['E2','Superevent', 1000000000, -5, 1, None],
     ['E3','Superevent', 1000000000,  2, 5, None],
     ['E4','Superevent', 1000000000, -5, 5, 'Burst'],
     ['E5','Superevent', 1000000050, -10, 10, None]])
def test_search_return(monkeypatch,
                       gracedb_id, event_type, gpstime, tl, th, group):

    event_dict = {'graceid': gracedb_id,
                  'gpstime': gpstime,
                  'group': group,
                  'pipeline': 'Fermi',
                  'search': 'GRB'}

    results = raven.search.search(gracedb_id, tl, th, gracedb=MockGracedb(),
                                  group=group, pipelines=[], event_dict=event_dict)
    assert results == expected_results(event_type, gpstime, tl, th, group=group)

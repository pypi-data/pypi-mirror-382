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
Module containing time- and sky- coincidence search functions.
"""
__author__ = "Alex Urban <alexander.urban@ligo.org>"


# Imports.
import json
import re

from astropy import units as u
from astropy.coordinates import SkyCoord
import astropy_healpix as ah
import healpy as hp
from hpmoc import PartialUniqSkymap
import numpy as np

from .gracedb_events import SE, ExtTrig
from .gracedb_events import _is_gracedb_sdk, _get_gracedb_url, is_skymap_moc
from ligo.gracedb.rest import GraceDb


#########################################################
# Functions implementing the actual coincidence search. #
#########################################################

def query(event_type, gpstime, tl, th, gracedb=None, group=None,
          pipelines=None, ext_searches=None, se_searches=None):
    """ Query for coincident events of type event_type occurring within a
        window of [tl, th] seconds around gpstime.

    Parameters
    ----------
    event_type: str
        "Superevent" or "External"
    gpstime: float
        Event's gps time
    tl: float
        Start of coincident time window
    th: float
        End of coincident time window
    gracedb: class
        SDK or REST API client for HTTP connection
    group: str
        "CBC", "Burst", or "Test",
    pipelines: array
        List of external trigger pipeline names
    ext_searches: array
        List of external trigger searches
    se_searches: array
        List of superevent searches
    """

    # Perform a sanity check on the time window.
    if tl >= th:
        raise ValueError("ERROR: The time window [tl, th] must have tl < th.")

    # Catch potential error if pipelines or searches are None
    if pipelines is None:
        pipelines = []
    if ext_searches is None:
        ext_searches = []
    if se_searches is None:
        se_searches = []

    # Initiate instance of GraceDb if not given.
    if gracedb is None:
        gracedb = GraceDb()
    is_gracedb_sdk = _is_gracedb_sdk(gracedb)

    # Perform the GraceDB query.
    start, end = gpstime + tl, gpstime + th

    if event_type == 'External':  # Searching for external events
        arg = (f"{event_type} {start} .. {end}"
               f"{' MDC' if 'MDC' in ext_searches else ''}")
        # Return list of graceids of coincident events.
        if is_gracedb_sdk:
            results = list(gracedb.events.search(query=arg))
        else:
            results = list(gracedb.events(arg))

        if pipelines:
            results = [event for event in results if event['pipeline']
                       in pipelines]
        if ext_searches:
            results = [event for event in results if
                       event['search'] in ext_searches]
        return results

    elif event_type == 'Superevent':  # Searching for superevents
        arg = f"{start} .. {end}{' MDC' if 'MDC' in se_searches else ''}"
        # Return list of coincident superevent_ids.
        if is_gracedb_sdk:
            results = list(gracedb.superevents.search(query=arg))
        else:
            results = list(gracedb.superevents(arg))
        if group:
            results = [superevent for superevent in results if
                       superevent['preferred_event_data']['group'] == group]
        if se_searches:
            results = [superevent for superevent in results if
                       superevent['preferred_event_data']['search'] in
                       se_searches]
        return results


def search(gracedb_id, tl, th, gracedb=None, gracedb_ext=None,
           group=None, pipelines=None,
           ext_searches=None, se_searches=None, event_dict=None):
    """ Perform a search for neighbors coincident in time within
        a window [tl, th] seconds around an event. Uploads the
        results to the selected gracedb server.

    Parameters
    ----------
    gracedb_id: str
        ID of the trigger used by GraceDB
    tl: float
        Start of coincident time window
    th: float
        End of coincident time window
    gracedb: class
        SDK or REST API client for HTTP connection
    gracedb_ext: class
        SDK or REST API client for HTTP connection for external candidate, if
        separate from GW candidate (necessary for offline search)
    group: string
        "CBC", "Burst", or "Test",
    pipelines: array
        List of external trigger pipeline names
    ext_searches: array
        List of external trigger searches
    se_searches: array
        List of superevent searches
    event_dict: dict
        Dictionary of the gracedb event
    """
    # Initiate correct instance of GraceDb.
    if gracedb is None:
        gracedb = GraceDb()

    # If no separate GraceDB instance indicated, use GW instance
    if gracedb_ext is None:
        gracedb_ext = gracedb

    # Identify neighbor types with their graceid strings.
    types = {'G': 'GW', 'E': 'External', 'S': 'Superevent',
             'T': 'Test'}
    groups = {'G': 'CBC Burst', 'E': 'External', 'S': 'Superevent'}

    # Catch potential error if pipelines or searches are None
    if pipelines is None:
        pipelines = []
    if ext_searches is None:
        ext_searches = []
    if se_searches is None:
        se_searches = []

    # Load in event
    if 'S' in gracedb_id:
        event = SE(gracedb_id, gracedb=gracedb, event_dict=event_dict)
        gracedb_for_query = gracedb_ext
    else:
        event = ExtTrig(gracedb_id, gracedb=gracedb_ext, event_dict=event_dict)
        gracedb_for_query = gracedb

    # Grab any and all neighboring events.
    # Filter results depending on the group if specified.
    neighbors = query(groups[event.neighbor_type], event.gpstime, tl, th,
                      gracedb=gracedb_for_query,
                      group=group, pipelines=pipelines,
                      ext_searches=ext_searches, se_searches=se_searches)

    # If no neighbors, report a null result.
    if not neighbors:
        if 'S' in gracedb_id:
            message = (f"RAVEN: No {types[event.neighbor_type]} "
                       f"{str(pipelines) + ' ' if pipelines else ''}"
                       f"{str(ext_searches) + ' ' if ext_searches else ''}"
                       f"candidates in window [{tl}, +{th}] seconds. ")
        else:
            message = (f"RAVEN: No {types[event.neighbor_type]} "
                       f"{str(group) + ' ' if group else ''}"
                       f"{str(se_searches) + ' ' if se_searches else ''}"
                       f"candidates in window [{tl}, +{th}] seconds. ")
        message += f"Search triggered from {gracedb_id}"
        event.submit_gracedb_log(message, tags=["ext_coinc"])

    # If neighbors are found, report each of them.
    else:
        for neighbor in neighbors:
            if event.neighbor_type == 'S':
                # search called on a external event
                deltat = event.gpstime - neighbor['t_0']
                superid = neighbor['superevent_id']
                extid = event.graceid
                tl_m, th_m = tl, th
                relat_word = ['before', 'after']
                ext = event
                se = SE(superid, gracedb=gracedb, event_dict=neighbor)
            else:
                # search called on a superevent
                deltat = event.gpstime - neighbor['gpstime']
                superid = event.graceid
                extid = neighbor['graceid']
                tl_m, th_m = -th, -tl
                relat_word = ['after', 'before']
                se = event
                ext = ExtTrig(extid, gracedb=gracedb, event_dict=neighbor)
            if deltat < 0:
                relat_word.reverse()
                deltat = abs(deltat)
            selink = 'superevents/'
            extlink = 'events/'
            gracedb_url = re.findall('(.*)api/', _get_gracedb_url(gracedb))[0]

            # Send message to external event
            message_ext = \
                (f"RAVEN: {types['S']} {str(group) + ' ' if group else ''}"
                 f"{str(se_searches) + ' ' if se_searches else ''}candidate "
                 f"<a href='{gracedb_url}{selink}{superid}'>{superid}</a> "
                 f"within [{tl_m}, +{th_m}] seconds, about {float(deltat):.3f}"
                 f" second(s) {relat_word[0]} {types['E']} event. "
                 f"Search triggered from {gracedb_id}")
            ext.submit_gracedb_log(message_ext, tags=["ext_coinc"])

            # Send message to superevent
            message_gw = \
                (f"RAVEN: {types['E']} "
                 f"{str(pipelines) + ' ' if pipelines else ''}"
                 f"{str(ext_searches) + ' ' if ext_searches else ''}event "
                 f"<a href='{gracedb_url}{extlink}{extid}'>{extid}</a> "
                 f"within [{-th_m}, +{-tl_m}] seconds, about "
                 f"{float(deltat):.3f} second(s) {relat_word[1]} "
                 f"{types['S']}. Search triggered from {gracedb_id}")
            se.submit_gracedb_log(message_gw, tags=["ext_coinc"])

    # Return search results.
    return neighbors


def skymap_overlap_integral(gw_skymap, ext_skymap=None,
                            ra=None, dec=None,
                            gw_nested=True, ext_nested=True):
    """Sky map overlap integral between two sky maps.

    This method was originally developed in:
        doi.org/10.3847/1538-4357/aabfd2
    while the flattened sky map version was mentioned in:
        https://git.ligo.org/brandon.piotrzkowski/raven-paper

    Either a multi-ordered (MOC) GW sky map with UNIQ ordering,
    or a flattened sky map with Nested or Ring ordering can be used.
    Either a mutli-ordered (MOC) external sky map with UNIQ ordering,
    flattened sky map with Nested or Ring ordering,
    or a position indicated by RA/DEC can be used.

    Parameters
    ----------
    gw_skymap: array or Table
        Array containing either GW sky localization probabilities
        if using nested or ring ordering,
        or probability density if using UNIQ ordering
    ext_skymap: array or Table
        Array containing either external sky localization probabilities
        if using nested or ring ordering,
        or probability density if using UNIQ ordering
    ra: float
        Right ascension of external localization in degrees
    dec: float
        Declination of external localization in degrees
    gw_nested: bool
        If True, assumes GW sky map uses nested ordering, otherwise
        assumes ring ordering
    ext_nested: bool
        If True, assumes external sky map uses nested ordering, otherwise
        assumes ring ordering

    """
    # Set initial variables
    gw_skymap_uniq = None
    gw_skymap_prob = None
    ext_skymap_uniq = None
    ext_skymap_prob = None

    # Determine MOC or flattened
    gw_moc = is_skymap_moc(gw_skymap)
    # Set default value now, overwrite later if ext_skymap exists
    ext_moc = False

    # Load sky map arrays
    if gw_moc:
        gw_skymap_uniq = gw_skymap['UNIQ']
        try:
            gw_skymap_prob = gw_skymap['PROBDENSITY']
        except KeyError:
            gw_skymap_prob = gw_skymap['PROB']

    if ext_skymap is not None:
        ext_moc = is_skymap_moc(ext_skymap)
        if ext_moc:
            ext_skymap_uniq = ext_skymap['UNIQ']
            try:
                ext_skymap_prob = ext_skymap['PROBDENSITY']
            except KeyError:
                ext_skymap_prob = ext_skymap['PROB']

    # Set ordering
    se_order = 'nested' if gw_nested or gw_moc else 'ring'
    ext_order = 'nested' if ext_nested or ext_moc else 'ring'

    # Set negative values to zero to disclude them
    if gw_moc:
        np.clip(gw_skymap_prob, a_min=0., a_max=None)
    else:
        np.clip(gw_skymap, a_min=0., a_max=None)
    if ext_skymap is not None:
        if ext_moc:
            np.clip(ext_skymap_prob, a_min=0., a_max=None)
        else:
            np.clip(ext_skymap, a_min=0., a_max=None)

    if ext_skymap is None and not (ra is not None and dec is not None):
        # Raise error if external info not given
        raise ValueError("Please provide external sky map or ra/dec")

    # Use multi-ordered GW sky map
    if gw_moc:
        # gw_skymap is the probability density instead of probability
        # convert GW sky map uniq to ra and dec
        level, ipix = ah.uniq_to_level_ipix(gw_skymap_uniq)
        nsides = ah.level_to_nside(level)
        areas = ah.nside_to_pixel_area(nsides)
        ra_gw, dec_gw = \
            ah.healpix_to_lonlat(ipix, nsides,
                                 order='nested')
        sky_prior = 1 / (4 * np.pi * u.sr)
        se_norm = np.sum(gw_skymap_prob * areas)

        if ext_moc:
            # Use two multi-ordered sky maps
            gw_sky_hpmoc = PartialUniqSkymap(
                               gw_skymap_prob, gw_skymap_uniq,
                               name="PROBDENSITY")
            ext_sky_hpmoc = PartialUniqSkymap(
                                    ext_skymap_prob, ext_skymap_uniq,
                                    name="PROBDENSITY")
            ext_norm = np.sum(ext_sky_hpmoc.s * ext_sky_hpmoc.area())

            # Take product of sky maps and then sum to get inner product
            # Note that this method uses the highest depth grid of each sky map
            comb_sky_hpmoc = gw_sky_hpmoc * ext_sky_hpmoc
            return np.sum(comb_sky_hpmoc.s * comb_sky_hpmoc.area() /
                          sky_prior / se_norm / ext_norm).to(1).value

        elif ra is not None and dec is not None:
            # Use multi-ordered gw sky map and one external point
            # Relevant for very well localized experiments
            # such as Swift
            c = SkyCoord(ra=ra*u.degree, dec=dec*u.degree)
            catalog = SkyCoord(ra=ra_gw, dec=dec_gw)
            ind, d2d, d3d = c.match_to_catalog_sky(catalog)

            return (gw_skymap_prob[ind] / u.sr /
                    sky_prior / se_norm).to(1).value

        elif ext_skymap is not None:
            # Use multi-ordered gw sky map and flat external sky map
            # Find matching external sky map indices using GW ra/dec
            ext_nside = ah.npix_to_nside(len(ext_skymap))
            ext_ind = \
                ah.lonlat_to_healpix(ra_gw, dec_gw, ext_nside,
                                     order=ext_order)

            ext_norm = np.sum(ext_skymap)

            return np.sum(gw_skymap_prob * areas * ext_skymap[ext_ind] /
                          ah.nside_to_pixel_area(ext_nside) /
                          sky_prior / se_norm / ext_norm).to(1).value

    # Use flat GW sky map
    else:
        if ra is not None and dec is not None:
            # Use flat gw sky and one external point
            se_nside = ah.npix_to_nside(len(gw_skymap))
            ind = ah.lonlat_to_healpix(ra * u.deg, dec * u.deg, se_nside,
                                       order=se_order)
            se_norm = sum(gw_skymap)
            return gw_skymap[ind] * len(gw_skymap) / se_norm

        elif ext_skymap is not None:
            if gw_nested != ext_nested:
                raise ValueError("Sky maps must both use nested or ring "
                                 "ordering")
            # Use two flat sky maps
            nside_s = hp.npix2nside(len(gw_skymap))
            nside_e = hp.npix2nside(len(ext_skymap))
            if nside_s > nside_e:
                ext_skymap = hp.ud_grade(ext_skymap,
                                         nside_out=nside_s,
                                         order_in=('NESTED' if ext_nested
                                                   else 'RING'))
            else:
                gw_skymap = hp.ud_grade(gw_skymap,
                                        nside_out=nside_e,
                                        order_in=('NESTED' if gw_nested
                                                  else 'RING'))
            se_norm = gw_skymap.sum()
            exttrig_norm = ext_skymap.sum()
            if se_norm > 0 and exttrig_norm > 0:
                return (np.dot(gw_skymap, ext_skymap) / se_norm /
                        exttrig_norm * len(gw_skymap))
            raise ValueError("RAVEN: ERROR: At least one sky map has a "
                             "probability density that sums to zero or less.")

    raise ValueError("Please provide both GW and external sky map info")


def coinc_far(se_far, tl, th,
              joint_far_method=None,
              ext_rate=None, far_ext=None,
              far_gw_thresh=None, far_ext_thresh=None,
              ext_search=None, ext_pipeline=None,
              incl_sky=None,
              gw_skymap=None, ext_skymap=None,
              ra=None, dec=None, use_radec=False,
              gw_nested=False, ext_nested=False,
              se_preferred_event=None, ext_graceid=None):
    """ Calculate the significance of a gravitational wave candidate with the
        addition of an external astrophyical counterpart in terms of a
        coincidence false alarm rate. This includes a temporal and a
        space-time type.

    Parameters
    ----------
    se_far: float
        Superevent false alarm rate
    tl: float
        Start of coincident time window
    th: float
        End of coincident time window
    joint_far_method: str
        Joint FAR method to use, either 'untargeted' or 'targeted'
        If None, will try to determine from given search field
    ext_rate: float
        Detection rate of external events
    far_ext: float
        External event false alarm rate
    far_gw_thresh: float
        Maximum cutoff for GW FAR considered in the search
    far_ext_thresh: float
        Maximum cutoff for external event FAR considered in the search
    ext_search: str
        "GRB", "SubGRB", "SubGRBTargeted", "MDC", or "HEN"
    ext_pipeline: str
        External trigger pipeline name
    incl_sky: bool
        If True or False, uses or doesn't sky maps in the joint FAR
        calculation. If None, checks if the needed sky map info is present to
        include
    gw_skymap: array or Table
        Array containing either GW sky localization probabilities
        if using nested or ring ordering,
        or probability density if using UNIQ ordering
    ext_skymap: array or Table
        Array containing either external sky localization probabilities
        if using nested or ring ordering,
        or probability density if using UNIQ ordering
    ra: float
        Right ascension of external localization in degrees
    dec: float
        Declination of external localization in degrees
    use_radec: bool
        If True, use ra and dec for single pixel external sky map
    gw_nested: bool
        If True, assumes GW sky map uses nested ordering, otherwise
        assumes ring ordering
    ext_nested: bool
        If True, assumes external sky map uses nested ordering, otherwise
        assumes ring ordering
    se_preferred_event: str
        GraceDB ID of the preferred GW event
    ext_graceid: str
        GraceDB ID of the external event
    """
    # The combined rate of independent GRB discovery by Swift, Fermi, and SVOM
    # ECLAIRs. See here: https://dcc.ligo.org/LIGO-T2400116
    # Fermi: 236/yr
    # Swift: 65/yr
    # SVOM ECLAIRs: ~25/yr
    grb_gcn_rate = 325. / (365. * 24. * 60. * 60.)

    # Rate of subthreshold GRBs (rate of threshold plus rate of
    # subthreshold). Introduced based on an analysis done by
    # Peter Shawhan: https://dcc.ligo.org/cgi-bin/private/
    #                DocDB/ShowDocument?docid=T1900297&version=
    subgrb_gcn_rate = 65. / (365. * 24. * 60. * 60.)

    # Combined rate of all GOLD IceCube notice from Table 1 of
    # https://arxiv.org/pdf/2304.01174
    # (101.3 + 9.3 + 22.9) / 9.6 years = 13.91 / yr
    hen_gcn_rate = 13.91 / (365. * 24. * 60. * 60.)

    # If no method given, try to guess based on provided external search
    if joint_far_method is None:
        if ext_search in {'GRB', 'SubGRB', 'MDC', 'HEN'}:
            joint_far_method = 'untargeted'
        elif ext_search == 'SubGRBTargeted':
            joint_far_method = 'targeted'

    # If not determined, check whether to include sky map info
    if incl_sky is None:
        incl_sky = \
            gw_skymap is not None and (ext_skymap is not None or use_radec)

    # Calculate joint FAR
    if joint_far_method is not None \
            and joint_far_method.lower() == 'untargeted':
        # If needed variables are not determined, try to guess and pick
        # variables based on given pipelines and search
        if ext_rate is None:
            if ext_search in {'GRB', 'MDC'}:
                ext_rate = grb_gcn_rate
            elif ext_search == 'HEN':
                ext_rate = hen_gcn_rate
            elif ext_search == 'SubGRB':
                ext_rate = grb_gcn_rate + subgrb_gcn_rate

        temporal_far = (th - tl) * ext_rate * se_far

    elif joint_far_method is not None \
            and joint_far_method.lower() == 'targeted':
        # If needed variables are not determined, try to guess and pick
        # variables based on given pipelines and search
        if far_gw_thresh is None and far_ext_thresh is None and \
                ext_search == 'SubGRBTargeted':
            # Max FARs considered in analysis
            far_gw_thresh = \
                far_gw_thresh if far_gw_thresh else 2 / (3600 * 24)
            if ext_pipeline == 'Fermi':
                far_ext_thresh = \
                    far_ext_thresh if far_ext_thresh else 1 / 10000
            elif ext_pipeline == 'Swift':
                far_ext_thresh = \
                    far_ext_thresh if far_ext_thresh else 1 / 1000

        # Map the product of uniformly drawn distributions to CDF
        # See https://en.wikipedia.org/wiki/Product_distribution
        z = (th - tl) * far_ext * se_far
        z_max = (th - tl) * far_ext_thresh * far_gw_thresh
        temporal_far = z * (1 - np.log(z/z_max))

    # If a method hasn't been given or determined, throw error
    else:
        raise ValueError(
            ("Pleave provide a joint_far_method ('untargeted' or 'targeted') "
             "or a supported search ('GRB', 'SubGRB', 'SubGRBTargeted', "
             "'HEN', or 'MDC')"))

    # Apply float wrapper to remove np types
    temporal_far = float(temporal_far)

    # Include sky coincidence if desired.
    if incl_sky:
        skymap_overlap = float(
                             skymap_overlap_integral(
                                 gw_skymap, ext_skymap,
                                 ra, dec,
                                 gw_nested, ext_nested))
        spatiotemporal_far = temporal_far / skymap_overlap
    else:
        spatiotemporal_far = None
        skymap_overlap = None

    result = {"temporal_coinc_far": temporal_far,
              "spatiotemporal_coinc_far": spatiotemporal_far,
              "skymap_overlap": skymap_overlap}
    # In case this is ran locally without relevant variables, make graceids
    # optional in the final output
    if se_preferred_event is not None:
        result["preferred_event"] = str(se_preferred_event)
    if ext_graceid is not None:
        result["external_event"] = str(ext_graceid)

    return result


def calc_signif_gracedb(se_id, ext_id, tl, th,
                        joint_far_method=None,
                        ext_rate=None, far_gw_thresh=None, far_ext_thresh=None,
                        gracedb=None, gracedb_ext=None,
                        upload_to_gracedb=False,
                        se_dict=None, ext_dict=None,
                        incl_sky=None,
                        gw_fitsfile=None, ext_fitsfile=None,
                        gw_moc=None, ext_moc=None,
                        gw_nested=False, ext_nested=False,
                        use_radec=False,
                        use_preferred_event_skymap=False):
    """ Calculates and uploads the coincidence false alarm rate
        of the given superevent to the selected gracedb server.

    Parameters
    ----------
    se_id: str
        GraceDB ID of superevent
    ext_id: str
        GraceDB ID of external event
    tl: float
        Start of coincident time window
    th: float
        End of coincident time window
    joint_far_method: str
        Joint FAR method to use, either 'untargeted' or 'targeted'
        If None, will try to determine from given search field
    ext_rate: float
        Detection rate of external events
    far_gw_thresh: float
        Maximum cutoff for GW FAR considered in the search
    far_ext_thresh: float
        Maximum cutoff for external event FAR considered in the search
    gracedb: class
        SDK or REST API client for HTTP connection
    gracedb_ext: class
        SDK or REST API client for HTTP connection for external candidate, if
        separate from GW candidate (necessary for offline search)
    se_dict: float
        Dictionary of superevent
    ext_dict: float
        Dictionary of external event
    incl_sky: bool
        If True or False, uses or doesn't sky maps in the joint FAR
        calculation. If None, checks if the needed sky map info is present to
        include
    gw_fitsfile: str
        GW's sky map file name
    ext_fitsfile: str
        External event's sky map file name
    gw_moc: bool
        If True, assumes multi-order coverage (MOC) GW sky map
        If None, reads the file to determine whether MOC
    ext_moc: bool
        If True, assumes multi-order coverage (MOC) external event sky map
        If None, reads the file to determine whether MOC
    gw_nested: bool
        If True, assumes GW sky map uses nested ordering, otherwise
        assumes ring ordering
    ext_nested: bool
        If True, assumes external sky map uses nested ordering, otherwise
        assumes ring ordering
    use_radec: bool
        If True, use ra and dec for single pixel external sky map
    use_preferred_event_skymap: bool
        If True, uses the GW sky map in the preferred event rather than the
        superevent
    """
    # If no separate GraceDB instance indicated, use GW instance
    if gracedb_ext is None:
        gracedb_ext = gracedb

    if gracedb_ext is None:
        gracedb_ext = gracedb

    # Create the SE and ExtTrig objects based on string inputs.
    se = SE(se_id, fitsfile=gw_fitsfile, gracedb=gracedb, event_dict=se_dict,
            is_moc=gw_moc, nested=gw_nested,
            use_preferred_event_skymap=use_preferred_event_skymap)
    ext = ExtTrig(ext_id, fitsfile=ext_fitsfile, gracedb=gracedb_ext,
                  event_dict=ext_dict, use_radec=use_radec, is_moc=ext_moc,
                  nested=ext_nested)

    # Is the GW superevent candidate's FAR sensible?
    if not se.far:
        raise ValueError("RAVEN: WARNING: This GW superevent candidate's FAR "
                         "is zero or a NoneType object.")

    # Create coincidence_far.json
    coinc_far_output = \
        coinc_far(se.far, tl, th,
                  joint_far_method=joint_far_method,
                  ext_search=ext.search, ext_pipeline=ext.inst,
                  incl_sky=incl_sky,
                  gw_skymap=se.skymap, ext_skymap=ext.skymap,
                  far_ext=ext.far, ext_rate=ext_rate,
                  far_gw_thresh=far_gw_thresh,
                  far_ext_thresh=far_ext_thresh,
                  ra=ext.ra, dec=ext.dec, use_radec=use_radec,
                  gw_nested=gw_nested, ext_nested=ext_nested,
                  se_preferred_event=se.preferred_event,
                  ext_graceid=ext.graceid)

    # If prompted, upload results to GraceDB. Otherwise just return results.
    if upload_to_gracedb:
        coincidence_far = json.dumps(coinc_far_output)

        gracedb_events_url = \
            re.findall('(.*)api/', _get_gracedb_url(gracedb))[0]
        link1 = 'events/'
        link2 = 'superevents/'
        message_skymaps = ""
        # Include messaging for which sky map(s) used
        if incl_sky is None:
            incl_sky = \
                gw_fitsfile is not None and (ext_fitsfile is not None or
                                             use_radec)
        if incl_sky:
            message_skymaps = f", using {gw_fitsfile}"
            # Also include external sky map if used, where this won't be
            # included if we just used the RA/dec method
            if ext_fitsfile is not None and use_radec is False:
                message_skymaps += f" and {ext_fitsfile}"

        message = (f"RAVEN: Computed coincident FAR(s) in Hz with external "
                   f"trigger <a href='{gracedb_events_url + link1}"
                   f"{ext.graceid}'>{ext.graceid}</a>")
        message += message_skymaps
        se.submit_gracedb_log(message, filename='coincidence_far.json',
                              filecontents=coincidence_far,
                              tags=["ext_coinc"])

        message = (f"RAVEN: Computed coincident FAR(s) in Hz with superevent "
                   f"<a href='{gracedb_events_url + link2}"
                   f"{se.graceid}'>{se.graceid}</a>")
        message += message_skymaps
        ext.submit_gracedb_log(message, filename='coincidence_far.json',
                               filecontents=coincidence_far,
                               tags=["ext_coinc"])

    return coinc_far_output

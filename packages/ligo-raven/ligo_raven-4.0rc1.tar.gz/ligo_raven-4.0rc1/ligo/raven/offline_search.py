import math as mth
import matplotlib.pyplot as plt
import numpy as np
import os

from astropy.table import Table
from astropy import units as u

from ligo.raven import search
from ligo.raven.mock_gracedb import choose_gracedb


def num_above(array, minfar=10**(-9), maxfar=10**(-3)):
    """ Calculates the cumulative number of events with the same or smaller
        false alarm rate.

    Parameters
    ----------
    array : array
        Array of values to bin
    minfar : float
        Minimum bound of binning
    maxfar : float
        Maximum bound of binning

    Returns
    -------
    bins_used : array
        Values of bins used
    counts : counts
        Counts in each bin

    """
    powers = np.arange(mth.log10(minfar), mth.log10(maxfar), .01)
    bins = 10.**powers

    digi = np.digitize(array, bins, right=True)
    val, counts = np.unique(digi, return_counts=True)

    return np.array(bins)[val], np.cumsum(counts)


def get_skymap_filename(graceid, is_gw, gracedb):
    """Get the skymap fits filename.

    Parameters
    ----------
    graceid : str
        GraceDB ID
    is_gw : bool
        If True, uses method for superevent or preferred event. Otherwise uses
        method for external event.
    gracedb : class
        GraceDB client

    Returns
    -------
    filename : str
        Filename of latest sky map

    """
    gracedb_log = gracedb.logs(graceid).json()['log']
    if is_gw:
        # Try first to get a multiordered sky map
        for message in reversed(gracedb_log):
            filename = message['filename']
            v = message['file_version']
            fv = '{},{}'.format(filename, v)
            if filename.endswith('.multiorder.fits') and \
                    "combined-ext." not in filename:
                return fv
        # Try next to get a flattened sky map
        for message in reversed(gracedb_log):
            filename = message['filename']
            v = message['file_version']
            fv = '{},{}'.format(filename, v)
            if filename.endswith('.fits.gz') and \
                    "combined-ext." not in filename:
                return fv
    else:
        for message in reversed(gracedb_log):
            filename = message['filename']
            v = message['file_version']
            fv = '{},{}'.format(filename, v)
            if (filename.endswith('.fits') or filename.endswith('.fit') or
                    filename.endswith('.fits.gz')) and \
                    "combined-ext." not in filename:
                return fv
    return None


def offline_search(input_path_gw, input_path_ext, output_path='results',
                   t_start=None, t_end=None, tl=-1, th=5,
                   gw_far_thresh=None, ext_far_thresh=None,
                   alert_far_thresh=1/(365.*24.*60.*60.)*6.,
                   ext_rate=None,
                   trials_factor=1, use_radec=False,
                   use_calculated_ext_rate=False,
                   load_gw_fars=False,
                   joint_far_method=None,
                   group=None, pipeline=None, ext_search=None,
                   se_search=None):
    """ Perform offline RAVEN search, where the inputs can be any combination
    of two online GraceDB instances or local files.

    Parameters
    ----------
    input_path_gw : str
        Input for GW data, either a GraceDB API url or path to local file
    input_path_ext : str
        Input for external data, either a GraceDB API url or path to local file
    output_path : str
        Output path of results directory to add data products to
    t_start : float
        Start time of search
    t_end : float
        End time of search
    tl : float
        Start of coincident time window
    th : float
        End of coincident time window
    gw_far_thresh : float
        Maximum GW FAR cutoff to consider superevent in search
    ext_far_thresh : float
        Maximum external FAR cutoff to consider event in search
    alert_far_thresh : float
        Joint FAR cutoff to consider a coincidence for an alert
    ext_rate: float
        If given, use rate of external triggers in joint FAR calculation
    trials_factor : float
        Trials factor given by the number of independent GW pipelines
    use_radec : bool
        If True and needed, will use the single pixel RA/dec method to
        calculate the sky map overlap integral
    use_calculated_ext_rate : bool
        If True, will use the calculated rate of external triggers, given from,
        the time and number of triggers in the time period when calculating the
        joint FAR. Note this and ext_rate cannot both be chosen.
    load_gw_fars : bool
        If True, loads all of the GW candidates in the given time period to
        plot their FARS
    joint_far_method: str
        Joint FAR method to use, either 'untargeted' or 'targeted'
        If None, will try to determine from given search field
    group : str
        "CBC", "Burst", or "Test",
    pipeline : str
        External trigger pipeline name
    ext_search : str
        External trigger search
    se_search : str
        List of superevent search

    Returns
    -------
    output_table: Table
        AstroPy Table of joint candidates found during the search

    """
    # Correct output path string to remove final slash
    if output_path.endswith('/'):
        output_path = output_path[:-1]

    # Try to make output directory
    if not (os.path.exists(output_path) and os.path.isdir(output_path)):
        os.makedirs(output_path)
        path_msg = "Creating new results directory: {}".format(output_path)
    else:
        path_msg = "Results directory already exists"
    print(path_msg)

    # Perform a sanity check on the time to search
    if t_start >= t_end:
        raise ValueError("ERROR: The search must have t_start < t_end.")

    # Perform a sanity check on the time window.
    if tl >= th:
        raise ValueError("ERROR: The time window [tl, th] must have tl < th.")

        # Open file to write variables to
    f = open(output_path+'/output_log.txt', 'w+')
    f.write(path_msg + '\n')
    f.write('Arguments used:\n')
    f.write(str(locals()) + '\n')

    # Catch potential error if pipelines or searches are None
    pipelines = [] if pipeline is None else [pipeline]
    # FIXME: Rename searches to ext_searches and depreciate searches field
    ext_searches = [] if ext_search is None else [ext_search]
    se_searches = [] if se_search is None else [se_search]

    # Load GraceDB classes
    gracedb_gw = choose_gracedb(input_path_gw)
    gracedb_ext = choose_gracedb(input_path_ext)

    # Define basic variables
    total_time = (t_end - t_start) * u.s
    years = (total_time).to(u.yr)

    f.write('Will search of a period of {0:3f} years\n'.format(years))
    if gw_far_thresh:
        n_gw_expect = (gw_far_thresh / u.s).to(1/u.day).value
        msg = 'Expecting a GW rate of {0:2f} per day'.format(n_gw_expect)
        f.write(msg + '\n')
        print(msg)
    if ext_far_thresh:
        msg = 'Expecting a rate of external triggers of {0:2f} per day'.format(
            (ext_far_thresh / u.s).to(1/u.day).value)
        f.write(msg + '\n')
        print(msg)
    if ext_rate:
        msg = 'Expecting a rate of external triggers of {0:2f} per day'.format(
            (ext_rate / u.s).to(1/u.day).value)
        f.write(msg + '\n')
        print(msg)

    # Get list of external events to do search
    print("Loading/querying external events to search around...")

    arg = 'External {0} .. {1} {2} {3} {4}'.format(
        t_start, t_end,
        ext_search if ext_search else '',
        pipeline if pipelines else '',
        'far<{}'.format(ext_far_thresh) if ext_far_thresh else '')
    exts = list(gracedb_ext.events(arg))

    far_gw = []
    if load_gw_fars:
        print("Loading/querying superevents to compare FARs...")
        arg = '{0} .. {1} {2}'.format(
            t_start, t_end,
            'far<{}'.format(gw_far_thresh) if gw_far_thresh else '')
        gws = list(gracedb_gw.superevents(arg))
        mask = np.full(len(gws), True)
        if se_search:
            mask *= np.array([gw['preferred_event_data']['search'] == se_search
                              for gw in gws])
        if group:
            mask *= np.array([gw['preferred_event_data']['group'] == group
                              for gw in gws])
        far_gw = [gw['far'] for gw in np.array(gws)[mask]]

    # Result of initial query(ies)
    n_ext = len(exts)  # total
    n_gw = len(far_gw)
    gw_rate = (n_gw / total_time).to(1/u.s)  # per sec
    ext_rate_calculated = (n_ext / total_time).to(1/u.s)  # per sec

    if gw_rate.value:
        msg = 'Actual GW rate is {0:2f} per day'.format(
            gw_rate.to(1/u.day).value)
        f.write(msg + '\n')
        print(msg)
    if ext_rate_calculated.value:
        msg = 'Actual rate of external triggers is {0:2f} per day'.format(
            ext_rate_calculated.to(1/u.day).value)
        f.write(msg + '\n')
        print(msg)

    # predict number of coincidences
    if n_gw > 0:
        n_err_act = (n_gw * ext_rate_calculated * (th-tl) * u.s).to(1)
        f.write(('Expected number of random coincidence events based on number'
                 ' of GWs and ext events: {0:3f}\n'.format(n_err_act)))
    f.write('Looking for coincidences...\n')

    # If no trials factor given and information is available, set this given
    # the number of found GWs versus expected
    if gw_far_thresh is not None and trials_factor is None and n_gw > 0:
        trials_factor = n_gw / n_gw_expect
        msg = 'Changing trials factor to {}'.format(trials_factor)
        f.write(msg)
        print(msg)
    # If no trials_factor given, set this to a default value
    elif trials_factor is None:
        trials_factor = 1

    # If provided, use ext_rate or calculated ext_rate
    if ext_rate is not None and use_calculated_ext_rate:
        raise AssertionError((
            "Cannot choose both a given rate of external triggers (ext_rate) "
            "and to use the calculated rate of external triggers "
            "(use_calculated_ext_rate)."))
    elif ext_rate is None:
        ext_rate = (ext_rate_calculated.to(1/u.s).value if
                    use_calculated_ext_rate else None)

    # Establish joint trials factor
    joint_trials_factor = (trials_factor + 1) * trials_factor

    # Look for coincidences
    num = 0
    i = 0
    far_c = []
    far_c_spat = []
    output_table = Table(names=['superevent_id', 'external_id', 't_0',
                                'ext_search', 'gw_skymap', 'ext_skymap',
                                'gw_far', 'grb_far', 'grb_not_real',
                                'temporal_coinc_far',
                                'spatiotemporal_coinc_far', 'overlap_integral',
                                'previously_found', 'passes_threshold'],
                         dtype=['S2', 'S2', 'f8', 'S2', 'S2', 'S2', 'f8', 'f8',
                                bool, 'f8', 'f8', 'f8', bool, bool])
    for ext in exts:
        print("Searching around {}...".format(ext['graceid']))
        results = search.query('Superevent', ext['gpstime'], -th, -tl,
                               gracedb=gracedb_gw, group=group,
                               pipelines=pipelines, ext_searches=ext_searches,
                               se_searches=se_searches)
        num += len(results)
        for result in results:
            prev_known = False
            pass_thresh = False
            error = ext['extra_attributes']['GRB'].get('error_radius')
            # FIXME: We should consider an option to always force the use_radec
            # option for the coinc_far
            use_radec_temp = \
                (use_radec and error is not None and error < 0.1)
            if use_radec_temp:
                print('Using RA/dec method here...')
            print('Found coincidence between {0} and {1}'.format(
                result['superevent_id'], ext['graceid']))
            if gw_far_thresh and result['far'] > gw_far_thresh:
                print("{}'s FAR is too large, skipping...".format(
                    result['superevent_id']))
                continue
            # Try to get sky maps
            use_preferred_event_skymap = False
            gw_fitsfile = result.get('skymap')
            if result.get('labels') and 'SKYMAP_READY' in result['labels']:
                gw_fitsfile = get_skymap_filename(result['superevent_id'],
                                                  True,
                                                  gracedb=gracedb_gw)
            elif result.get('labels') and 'EM_READY' in result['labels']:
                gw_fitsfile = get_skymap_filename(result['preferred_event'],
                                                  True,
                                                  gracedb=gracedb_gw)
                use_preferred_event_skymap = True
                print('Superevent sky not available, using preferred event...')
            ext_fitsfile = ext.get('skymap')
            if ext.get('labels') and 'EXT_SKYMAP_READY' in ext['labels']:
                ext_fitsfile = get_skymap_filename(ext['graceid'], False,
                                                   gracedb=gracedb_ext)
            # Ignore flattened Swift sky maps if RA/dec preferred
            # Also override if value is not string, which occurs for empty
            # astropy Table values
            if ext_fitsfile and (not isinstance(ext_fitsfile, str) or
                                 ('multiorder' not in ext_fitsfile and
                                  use_radec_temp)):
                ext_fitsfile = None
            print('Using {0} and {1} sky maps...'.format(gw_fitsfile,
                                                         ext_fitsfile))
            coinc_far = \
                search.calc_signif_gracedb(
                    result['superevent_id'], ext['graceid'], tl, th,
                    gracedb=gracedb_gw, gracedb_ext=gracedb_ext,
                    upload_to_gracedb=False,
                    joint_far_method=joint_far_method,
                    ext_rate=ext_rate,
                    far_gw_thresh=gw_far_thresh,
                    far_ext_thresh=ext_far_thresh,
                    gw_fitsfile=gw_fitsfile,
                    ext_fitsfile=ext_fitsfile,
                    use_radec=use_radec_temp,
                    se_dict=result, ext_dict=ext,
                    use_preferred_event_skymap=use_preferred_event_skymap)

            print('FAR results: {}'.format(coinc_far))
            coinc_far_temp = coinc_far.get('temporal_coinc_far', np.nan)
            coinc_far_spat = np.nan

            far_c.append(coinc_far_temp)
            # Check if coincidence may have qualfied for an alert
            # Note more conditions are used in online RAVEN than this
            if coinc_far['spatiotemporal_coinc_far'] is not None:
                coinc_far_spat = coinc_far['spatiotemporal_coinc_far']
                if coinc_far['spatiotemporal_coinc_far'] < np.inf:
                    far_c_spat.append(coinc_far_spat)
                    # Use stringent RAVEN publishing threshold
                    # Note plotting will ignore joint trials factor
                    pass_thresh = \
                        coinc_far_spat * joint_trials_factor < alert_far_thresh
            # Check if coincidence was previously known about
            prev_known = 'EM_COINC' in result['labels']
            grb_likely_fake = 'NOT_GRB' in result['labels']

            # Output results to table row
            output_table.add_row(
                [result['superevent_id'],
                 ext['graceid'],
                 result['t_0'],
                 ext['search'],
                 gw_fitsfile if gw_fitsfile else '',
                 ext_fitsfile if ext_fitsfile else '',
                 result.get('far', np.nan),
                 ext.get('far', np.nan),
                 grb_likely_fake,
                 coinc_far_temp,
                 coinc_far_spat,
                 coinc_far.get('skymap_overlap', np.nan),
                 prev_known,
                 pass_thresh]
            )

    print("Writing results to table...")
    output_table.write(output_path+'/results.csv', overwrite=True)
    f.write('Number of found coincidences: {}\n'.format(int(num)))
    # Display some basic results
    f.write('Number of GRBs: {}\n'.format(int(n_ext)))
    if any(far_c_spat):
        f.write('Min/Max space-time coincidence FAR (Hz): {0}/{1}\n'.format(
            min(far_c_spat), max(far_c_spat)))

    if far_c == []:
        msg = 'No Joint FARs to plot! Ending search...'
        print(msg)
        f.write(msg)
        f.close()
        return

    # Examine and plot GW FARs if given
    if any(far_gw):
        f.write('Number of GWs: {}\n'.format(int(n_gw)))
        gw_far_used, gw_counts = \
            num_above(far_gw, minfar=min(far_gw) / 10, maxfar=max(far_gw) * 10)

        # Plot gravitational FAR
        plt.plot(1 / gw_far_used / trials_factor, gw_counts, zorder=2,
                 color='blue', label='GW Pipeline(s)')
        plt.plot(1 / gw_far_used, (gw_far_used * total_time), linestyle='--',
                 color='black', zorder=1, label='Expected')
        plt.xscale('log')
        plt.yscale('log')
        plt.ylim(.9, 1.05 * n_gw)
        plt.xlabel('IFAR (s)')
        plt.ylabel('Cumulative Count')
        plt.title('Gravitational Wave Pipeline(s)')
        plt.legend(loc='best')
        plt.grid()
        plt.savefig(output_path+'/Gravitational_far.png', bbox_inches='tight',
                    dpi=100)
        plt.close()
    else:
        gw_far_used, gw_counts = [], []

    # Count number above each FAR
    coinc_far_used, coinc_counts = \
        num_above(far_c, minfar=min(far_c) / 10, maxfar=max(far_c) * 10)
    if any(far_c_spat):
        coinc_far_spat_used, coinc_spat_counts = \
            num_above(far_c_spat,
                      minfar=min(far_c_spat) / 100,
                      maxfar=max(far_c_spat) * 100)
    else:
        coinc_far_spat_used, coinc_spat_counts = [], []

    # Plot coinc FAR
    plt.plot(1 / coinc_far_used / trials_factor, coinc_counts, zorder=3,
             color='orange', label='Temporal coincidence')
    plt.plot(1 / coinc_far_used, (coinc_far_used * total_time), linestyle='--',
             color='black', zorder=1, label='Expected')
    plt.xscale('log')
    plt.yscale('log')
    plt.xlabel('IFAR (s)')
    plt.ylabel('Cumulative Count')
    plt.title('Temporal Coincidence')
    plt.legend(loc='best')
    plt.grid()
    plt.savefig(output_path+'/Coincidence_far.png', bbox_inches='tight',
                dpi=100)
    plt.close()

    if any(far_c_spat):
        # Plot space-time coinc FAR
        plt.plot(1 / coinc_far_spat_used / trials_factor, coinc_spat_counts,
                 zorder=3, color='green', label='Space-time coincidence')
        plt.plot(1 / coinc_far_spat_used, (coinc_far_spat_used * total_time),
                 linestyle='--', color='black', zorder=1, label='Expected')
        plt.xscale('log')
        plt.yscale('log')
        plt.xlabel('IFAR (s)')
        plt.ylabel('Cumulative Count')
        plt.title('Space-time Coincidence')
        plt.legend(loc='best')
        plt.grid()
        plt.savefig(output_path+'/Coincidence_spat_far.png',
                    bbox_inches='tight', dpi=100)
        plt.close()

    # Plot FARs together
    if any(far_gw):
        plt.plot(1 / gw_far_used / trials_factor, gw_counts, zorder=2,
                 color='blue', label='GW Pipeline')
    plt.plot(1 / coinc_far_used / trials_factor, coinc_counts, zorder=3,
             color='orange', label='Temporal coincidence')
    if any(far_c_spat):
        plt.plot(1 / coinc_far_spat_used / trials_factor, coinc_spat_counts,
                 zorder=4, color='green', label='Space-time coincidence')

    max_far = np.amax(
        np.concatenate([gw_far_used, coinc_far_used, coinc_far_spat_used]))
    min_far = np.amin(np.concatenate([coinc_far_used, coinc_far_spat_used]))
    far_range = np.array([min_far, max_far])

    plt.plot(1 / far_range, (far_range * total_time), linestyle='--',
             color='black', zorder=1, label='Expected')
    # Make alert threshold relevant only to joint candidates and skew only
    # beyond what is done already with FARs
    plt.axvline(x=1 / alert_far_thresh * (joint_trials_factor / trials_factor),
                linestyle='-.', color='red', label='Alert threshold')
    plt.xscale('log')
    plt.yscale('log')
    plt.xlabel('IFAR (s)')
    plt.ylabel('Cumulative Count')
    plt.xlim(1/max_far*.95, 1/min_far*1.05)
    plt.ylim(.9, 1.05 * max(n_gw, num,
                            (max_far / u.s * total_time).to(1).value))
    plt.legend(loc='best')
    plt.grid()
    plt.savefig(output_path+'/all_far.png', bbox_inches='tight', dpi=125)
    plt.close()

    num_thresh = int(alert_far_thresh / u.s * total_time)
    num_temp = np.sum(np.array(far_c) * joint_trials_factor < alert_far_thresh)

    f.write('Expected number pass threshold: {}\n'.format(num_thresh))
    f.write('Number of temporal coincidences pass threshold: {}\n'.format(
        num_temp))
    if any(far_c_spat):
        num_spacetime = np.sum(np.array(far_c_spat) * joint_trials_factor
                               < alert_far_thresh)
        f.write(('Number of space-time coincidences pass threshold: '
                 '{}\n'.format(num_spacetime)))
    # Close text file
    f.close()
    # Output results
    return output_table

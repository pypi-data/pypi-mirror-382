"""Functions to calculate summary statistics."""

import numpy as np
import pandas as pd
from scipy import integrate
from scipy.interpolate import interp1d
from scipy.signal import find_peaks
from scipy.stats import iqr


def stats_err(d, **kwargs):
    """Use the half the interquartile range as an error."""
    return iqr(d) / 2


def find_smoothed_data_summary_stats(
    fitvar,
    derivname,
    statnames,
    no_samples,
    f,
    t,
    e,
    c,
    s,
    find_areas,
    plot_local_max,
    print_peak_properties,
    **kwargs,
):
    """
    Find smoothed data and summary statistics from fitderiv instance.

    Pass any kwargs to scipy's find_peaks via findlocalmaxderiv.

    Find summary statistics with bootstrapped errors including:
        - the maximal time derivative
        - the time at which the maximal time derivative occurs
        - the timescale found from inverting the maximal time derivative
        - the extreme values and range of the smoothed data
        - the lag time (the time when the tangent from the point with the
            maximal time derivative crosses a line parallel to the time-axis
            that passes through the first data point

    A summary statistic is given as the median of a distribution of the
    statistic calculated from time series sampled from the optimal Gaussian
    process.

    Its error is estimated as the interquartile range of this
    distribution.
    """
    # time-series for s dataframe
    df_for_s = pd.DataFrame(
        {
            "experiment": e,
            "condition": c,
            "strain": s,
            "time": t,
            f"smoothed_{fitvar}": f.f,
            f"smoothed_{fitvar}_err": np.sqrt(f.fvar),
            derivname: f.df,
            derivname + "_err": np.sqrt(f.dfvar),
            f"d/dt_{derivname}": f.ddf,
            f"d/dt_{derivname}_err": np.sqrt(f.ddfvar),
        }
    )
    # sample from GP
    fs, gs, hs = f.fit_deriv_sample(no_samples)
    if "log_" in fitvar:
        orig_fitvar = "".join(fitvar.split("log_"))
        df_for_s[f"smoothed_{orig_fitvar}"] = np.exp(f.f)
        df_for_s[f"smoothed_{orig_fitvar}_err"] = np.sqrt(
            np.var(np.exp(fs), axis=1)
        )
    # stats for sc dataframe
    # min f
    min_f = fs[np.argmin(fs, 0), np.arange(no_samples)]
    # max f
    max_f = fs[np.argmax(fs, 0), np.arange(no_samples)]
    # range
    range_f = fs[np.argmax(fs, 0), :] - fs[np.argmin(fs, 0), :]
    # calculate df stats
    im = np.argmax(gs, 0)
    # max df
    max_df = gs[im, np.arange(no_samples)]
    # time of max df
    t_max_df = np.array([t[i] for i in im])
    # inverse max df
    dt = np.log(2) / max_df
    # lag time
    lagtime = (
        t_max_df
        + (fs[0, np.arange(no_samples)] - fs[im, np.arange(no_samples)]) / max_df
    )
    # find local maximal derivative
    peak_coords, da, d = find_local_max_deriv(
        f, gs, print_peak_properties, **kwargs
    )
    # find area under df/dt vs f and area under f vs t
    if find_areas:
        adff, andff, aft, anft = find_areas_under(t, fs, gs)
    else:
        adff, andff, aft, anft = np.nan, np.nan, np.nan, np.nan
    # store results
    dict_for_sc = {
        "experiment": e,
        "condition": c,
        "strain": s,
        f"local_max_{derivname}": peak_coords[1],
        f"local_max_{derivname}_err": stats_err(da),
        f"time_of_local_max_{derivname}": peak_coords[0],
        f"time_of_local_max_{derivname}_err": stats_err(dt),
        # area under df/dt vs f
        f"area_under_{derivname}_vs_{fitvar}": np.median(adff),
        f"area_under_{derivname}_vs_{fitvar}_err": stats_err(adff),
        f"normalised_area_under_{derivname}_vs_{fitvar}": np.median(andff),
        f"normalised_area_under_{derivname}_vs_{fitvar}_err": stats_err(andff),
        # area under f vs t
        f"area_under_{fitvar}": np.median(aft),
        f"area_under_{fitvar}_err": stats_err(aft),
        f"normalised_area_under_{fitvar}": np.median(anft),
        f"normalised_area_under_{fitvar}_err": stats_err(anft),
    }
    # add statnames stats
    for stname, st in zip(
        statnames, [min_f, max_f, range_f, max_df, t_max_df, dt, lagtime]
    ):
        dict_for_sc[stname] = np.median(st)
        dict_for_sc[stname + "_err"] = stats_err(st)
    if not plot_local_max:
        peak_coords = None
    return df_for_s, dict_for_sc, peak_coords


def find_local_max_deriv(f, gs, print_peak_properties, **kwargs):
    """
    Find the greatest local maxima in the derivative.

    Check the derivative for local maxima and so find the local maximum
    with the highest derivative using samples, gs, of df.

    The keyword variables kwargs are passed to scipy's find_peaks.
    """
    # find peaks in mean df
    lpksmn, lpksmndict = find_peaks(f.df, **kwargs)
    if np.any(lpksmn):
        peak_coords = (
            f.t[lpksmn[np.argmax(f.df[lpksmn])]],
            f.df[lpksmn[np.argmax(f.df[lpksmn])]],
        )
        if print_peak_properties:
            # display properties of peaks
            print("Peak properties\n---")
            for prop in lpksmndict:
                print(f"{prop:15s}", lpksmndict[prop])
        # da: samples of local max df
        # dt: samples of time of local max df
        da, dt = [], []
        # find peaks of sampled df
        for gsample in np.transpose(gs):
            tpks = find_peaks(gsample, **kwargs)[0]
            if np.any(tpks):
                da.append(np.max(gsample[tpks]))
                dt.append(f.t[tpks[np.argmax(gsample[tpks])]])
        return peak_coords, da, dt
    else:
        # mean df has no peaks
        return (np.nan, np.nan), np.nan, np.nan


def find_areas_under(t, fs, gs):
    """
    Find areas.

    Given samples of f, as arguments fs, and of df, as arguments gs,
    find the area under df/dt vs f and the area under f vs t.
    """
    adff, andff, aft, anft = [], [], [], []
    for fsample, gsample in zip(np.transpose(fs), np.transpose(gs)):
        # area under df vs f: integrand has f as x and df as y
        def integrand(x):
            return interp1d(fsample, gsample)(x)

        iresult = integrate.quad(
            integrand,
            np.min(fsample),
            np.max(fsample),
            limit=100,
            full_output=1,
        )[0]
        adff.append(iresult)
        andff.append(iresult / (np.max(fsample) - np.min(fsample)))

        # area under f vs t: integrand has t as x and f as y
        def integrand(x):
            return interp1d(t, fsample)(x)

        iresult = integrate.quad(
            integrand, np.min(t), np.max(t), limit=100, full_output=1
        )[0]
        aft.append(iresult)
        anft.append(iresult / (np.max(t) - np.min(t)))
    return adff, andff, aft, anft

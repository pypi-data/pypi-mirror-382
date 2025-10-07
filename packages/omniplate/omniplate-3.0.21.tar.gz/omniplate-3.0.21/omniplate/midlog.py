"""Find and analyse mid-log growth."""

import matplotlib.pylab as plt
import numpy as np
from nunchaku import Nunchaku

import omniplate.admin as admin
import omniplate.clogger as clogger
import omniplate.omgenutils as gu
import omniplate.sunder as sunder


@clogger.log
def get_midlog(
    self,
    stats=["mean", "median", "min", "max"],
    min_duration=1,
    max_num=4,
    prior=[-5, 5],
    use_smoothed=False,
    figs=True,
    experiments="all",
    experiment_includes=False,
    experiment_excludes=False,
    conditions="all",
    condition_includes=False,
    condition_excludes=False,
    strains="all",
    strain_includes=False,
    strain_excludes=False,
    **kwargs,
):
    """
    Calculate mid-log statistics.

    Find the region of mid-log growth using nunchaku and calculate a
    statistic for each variable in the s dataframe in this region only.

    The results are added to the sc dataframe.

    Parameters
    ----------
    stats: str, optional
        A list of statistics to be calculated (using pandas).
    min_duration: float, optional
        The expected minimal duration of the midlog phase in units of time.
    max_num: int, optional
        The maximum number of segments of a growth curve.
    prior: list of two floats, optional
        Prior for nunchaku giving the lower and upper bounds on the gradients
        of the line segments.
    use_smoothed: boolean, optional
        If True, use the smoothed OD found by get_stats and its estimated
        errors.
        If False, use the OD of the replicates in different wells.
    figs: boolean, optional
        If True, show nunchaku's results with the mid-log region marked by
        black squares.
    experiments: string or list of strings, optional
        The experiments to include.
    conditions: string or list of strings, optional
        The conditions to include.
    strains: string or list of strings, optional
        The strains to include.
    experiment_includes: string, optional
        Selects only experiments that include the specified string in
        their name.
    experiment_excludes: string, optional
        Ignores experiments that include the specified string in their
        name.
    condition_includes: string, optional
        Selects only conditions that include the specified string in their
        name.
    condition_excludes: string, optional
        Ignores conditions that include the specified string in their name.
    strain_includes: string, optional
        Selects only strains that include the specified string in their
        name.
    strain_excludes: string, optional
        Ignores strains that include the specified string in their name.
    kwargs: passed to Nunchaku
    """
    admin.check_kwargs(kwargs)
    exps, cons, strs = sunder.get_all(
        self,
        experiments,
        experiment_includes,
        experiment_excludes,
        conditions,
        condition_includes,
        condition_excludes,
        strains,
        strain_includes,
        strain_excludes,
        no_null=True,
        no_media=True,
    )
    # run Nunchaku to find midlog and take the mean of summary stats
    find_midlog_stats(
        self=self,
        stats=stats,
        min_duration=min_duration,
        max_num=max_num,
        prior=prior,
        use_smoothed=use_smoothed,
        figs=figs,
        exps=exps,
        cons=cons,
        strains=strs,
        **kwargs,
    )


def get_selection(self, e, c, s):
    """Find the relevant section of the s dataframe."""
    select = (
        (self.s.experiment == e)
        & (self.s.condition == c)
        & (self.s.strain == s)
    )
    return select


def get_OD(self, e, c, s, use_smoothed):
    """Get OD and its estimated error if possible."""
    select = get_selection(self, e, c, s)
    # estimate standard deviation from replicates
    err = None
    if use_smoothed:
        t = self.s[select]["time"].values
        try:
            Y = self.s[select]["smoothed_log_OD"].values
            # use standard deviation from GP
            err = self.s[select]["smoothed_log_OD_err"].values
        except KeyError:
            print(f"Warning: smoothed ODs do not exist for {e}: {s} in {c}")
            Y = None
    else:
        t, od = sunder.extract_wells(self.r, self.s, e, c, s, "OD")
        if np.any(t):
            od[od < 0] = np.finfo(float).eps
            Y = np.log(od.T)
        else:
            Y = []
    return t, Y, err


def process_strain(strain, params):
    """Run nunchaku on a single strain."""
    t, Y, err = params[strain]
    if Y is None or len(Y) == 0:
        print(f"Error processing {strain}.")
        return
    common_i = np.all(~np.isnan(Y), axis=0)
    nc = Nunchaku(
        t[common_i],
        Y[:, common_i],
        err=err,
        prior=params["prior"],
        **params["nunchaku_params"],
    )
    num_segs, evidence = nc.get_number(num_range=params["max_num"])
    bds, bds_std = nc.get_iboundaries(num_segs)
    res_df = nc.get_info(bds)
    return strain, res_df, nc


def find_midlog_stats(
    self,
    stats,
    min_duration,
    max_num,
    prior,
    use_smoothed,
    figs,
    exps,
    cons,
    strains,
    **kwargs,
):
    """Find the stat of all variables in the s dataframe for mid-log growth."""
    stats = gu.make_list(stats)
    for e in exps:
        for c in cons:
            if len(strains):
                print(f"\nFinding mid-log growth for {e}: {c}")
                params = {
                    s: get_OD(self, e, c, s, use_smoothed) for s in strains
                }
                params["prior"] = prior
                params["nunchaku_params"] = kwargs
                params["max_num"] = max_num
                results = [
                    process_strain(s, params)
                    for s in strains
                    if (params[s][1] is not None and len(params[s][1]))
                ]
                process_nunchaku_results(
                    self=self,
                    results=results,
                    stats=stats,
                    min_duration=min_duration,
                    figs=figs,
                    e=e,
                    c=c,
                )


def process_nunchaku_results(self, results, stats, min_duration, figs, e, c):
    """Store and plot results from nunchaku."""
    for s, res_df, nc in results:
        # pick midlog segment
        t_st, t_en, y_st, y_en = pick_midlog(res_df, min_duration)
        if np.isnan(t_st) or np.isnan(t_en):
            print(f"\nError finding midlog data for {e}: {s} in {c}.")
        if figs:
            nc.plot(res_df, hlmax=None)
            for tv, yv in zip([t_st, t_en], [y_st, y_en]):
                plt.plot(tv, yv, "ks", markersize=10)
            plt.xlabel("time")
            plt.ylabel("log(OD)")
            plt.title(f"mid-log growth for {e} : {s} in {c}")
            plt.show(block=False)
        add_midlog_stats_to_sc(
            self,
            get_selection(self, e, c, s),
            e,
            c,
            s,
            t_st,
            t_en,
            stats,
        )


def pick_midlog(res_df, min_duration):
    """Find midlog from nunchaku's results dataframe."""
    # midlog had a minimal duration and positive growth rate
    sdf = res_df[(res_df["delta x"] > min_duration) & (res_df.gradient > 0)]
    if sdf.empty:
        return np.nan, np.nan
    else:
        # find mid-log growth - maximal specific growth rate
        ibest = sdf.index[sdf.gradient.argmax()]
        t_st, t_en = sdf["x range"][ibest]
        y_st = sdf.gradient[ibest] * t_st + sdf.intercept[ibest]
        y_en = sdf.gradient[ibest] * t_en + sdf.intercept[ibest]
        return t_st, t_en, y_st, y_en


def add_midlog_stats_to_sc(self, select, e, c, s, t_st, t_en, stats):
    """Find and store stats from midlog growth."""
    sdf = self.s[select]
    midlog_sdf = sdf[(sdf.time >= t_st) & (sdf.time <= t_en)]
    for stat in stats:
        # store results in dict
        res_dict = {col: np.nan for col in self.s.columns}
        res_dict["experiment"] = e
        res_dict["condition"] = c
        res_dict["strain"] = s
        stat_res = getattr(midlog_sdf, stat)(numeric_only=True)
        for key, value in zip(stat_res.index, stat_res.values):
            res_dict[key] = value
        # add "midlog" to data names
        res_dict = {
            (
                f"{stat}_midlog_{k}"
                if k
                not in [
                    "experiment",
                    "condition",
                    "strain",
                ]
                else k
            ): v
            for k, v in res_dict.items()
        }
        # add to sc dataframe
        admin.add_dict_to_sc(self, res_dict)

"""
A Bayesian method to correct for autofluorescence.

The GFP channel is denoted y ; the reference strain is denoted WT.
"""

from dataclasses import asdict, dataclass, fields

import matplotlib.pylab as plt
import numpy as np
from scipy.optimize import minimize_scalar

import omniplate.corrections as omcorr
import omniplate.omparallel as omparallel
import omniplate.omplot as omplot
import omniplate.sunder as sunder
from omniplate.omfitderiv import run_fit_deriv

rng = np.random.default_rng()
min_fl = 1e-4


def bootstrap_array(a):
    """Bootstrap 1D array."""
    na = a[rng.integers(0, a.size, a.size)]
    return na


@dataclass
class local_data:
    """Data from one time point."""

    ly: float
    lywt: float
    lyn: float
    od: float
    odwt: float

    def to_array(self):
        """Convert to array."""
        return np.array(list(asdict(self).values()))

    def to_list(self):
        """Convert to list."""
        return list(asdict(self).values())

    @classmethod
    def boot_from_list(cls, ell):
        """Define and bootstrap sample from an array."""
        field_names = [f.name for f in fields(cls)]
        return cls(
            **{
                name: bootstrap_array(val)
                for name, val in zip(field_names, ell)
            }
        )


@dataclass
class theta:
    """Parameters to infer."""

    a: float
    g: float

    def to_array(self):
        """Convert to array."""
        return np.array(list(asdict(self).values()))

    @classmethod
    def from_array(cls, arr):
        """Define from an array."""
        field_names = [f.name for f in fields(cls)]
        return cls(**{name: val for name, val in zip(field_names, arr)})

    @classmethod
    def zeros(cls):
        """Define with all values as zeros."""
        field_names = [f.name for f in fields(cls)]
        return cls(
            **{
                name: val
                for name, val in zip(field_names, np.zeros(len(field_names)))
            }
        )


@dataclass
class suff_stats:
    """Sufficient statistics."""

    yT: float
    ywtT: float
    lyT: float
    lywtT: float


def estimate_by(ld):
    """Find ML estimate of by."""
    return np.exp(np.mean(ld.lyn))


def find_suff_stats(x, ld):
    """Define the sufficient statistics."""
    th = theta.from_array(x)
    by = estimate_by(ld)
    yT = ld.od * (th.a + th.g) + by
    ywtT = ld.odwt * th.a + by
    lyT = np.log(yT)
    lywtT = np.log(ywtT)
    res = suff_stats(
        yT=yT,
        lyT=lyT,
        ywtT=ywtT,
        lywtT=lywtT,
    )
    return res


def find_bounds_x0(ld):
    """Find bounds on theta and make an initial estimate."""
    y = np.exp(ld.ly)
    ywt = np.exp(ld.lywt)
    by = estimate_by(ld)
    odwt = np.mean(ld.odwt)
    od = np.mean(ld.od)
    # bounds
    bounds = {"a": (min_fl, np.max(ywt) / odwt), "g": (min_fl, np.max(y) / od)}
    bounds = [
        bounds[theta_name] for theta_name in [f.name for f in fields(theta)]
    ]
    # estimate theta: a and g
    a0 = np.max([min_fl, (np.exp(np.mean(ld.lywt)) - by) / odwt])
    g0 = np.max([min_fl, (np.exp(np.mean(ld.ly)) - by) / od - a0])
    x0 = [a0, g0]
    return bounds, x0


def a_error(a, ld, params):
    """Find term in -log(posterior) from wild-type data."""
    ss = find_suff_stats([a, np.nan], ld)
    err = np.sum((ld.lywt - ss.lywtT) ** 2)
    return err


def g_error(g, ld, a_opt, params):
    """Find term in -log(posterior) from tagged-strain data."""
    ss = find_suff_stats(np.array([a_opt, g]), ld)
    err = np.sum((ld.ly - ss.lyT) ** 2)
    return err


def find_mode(ld, params):
    """Find mode of posterior using two 1d minimisations."""
    bounds, _ = find_bounds_x0(ld)
    a_opt = np.nan
    g_opt = np.nan
    ares = minimize_scalar(
        a_error, bounds=bounds[0], method="bounded", args=(ld, params)
    )
    if ares.success:
        a_opt = ares.x
        gres = minimize_scalar(
            g_error,
            bounds=bounds[1],
            method="bounded",
            args=(ld, a_opt, params),
        )
        if gres.success:
            g_opt = gres.x
    return theta(a=a_opt, g=g_opt)


def process_strain(strain, params):
    """Correct autofluorescence for one strain."""
    t = params["t"]
    # get data for tagged strain
    if params["y_data_dict"][strain] is None:
        return
    else:
        try:
            y, od = params["y_data_dict"][strain]
        except Exception as ex:
            print(f"Error accessing data for strain {strain}: {ex}")
            return
    print(
        f"{params['experiment']}: {strain} in {params['condition']};"
        f" {y.shape[1]} replicates"
    )
    flperod_raw = np.full((t.size, params["no_boots"]), np.nan)
    # correct autofluorescence for each time point
    for i_boot in range(params["no_boots"]):
        for i in range(t.size):
            ld = local_data(
                ly=np.log(y[i, :]),
                lywt=np.log(params["ywt"][i, :]),
                lyn=np.log(params["yn"][i, :]),
                od=od[i, :],
                odwt=params["odwt"][i, :],
            )
            if i_boot > 0:
                ld = local_data.boot_from_list(ld.to_list())
            mode = find_mode(ld, params)
            flperod_raw[i, i_boot] = mode.g
    return strain, flperod_raw


def define_bdn(options):
    """Define hyperparameters for smoothing Gaussian process."""
    bd_default = {0: (-2, 8), 1: (0, 4), 2: (-2, 1)}
    if options["bd"] is not None:
        bdn = bd_default | options["bd"]
    else:
        bdn = bd_default
    return bdn


def correct_auto_bayesian(
    self,
    f,
    ref_strain,
    no_processors,
    experiments,
    experiment_includes,
    experiment_excludes,
    conditions,
    condition_includes,
    condition_excludes,
    strains,
    strain_includes,
    strain_excludes,
    options,
):
    """
    Correct fluorescence for auto- and background fluorescence.

    Use a Bayesian method, with

        y = exp(epsilon) * ((g + a)*od + by)
        ywt = exp(epsilon) * (a*odwt + by)

    with epsilon normally distributed and modelling measurement noise.
    """
    print(f"Using Bayesian approach for {f[0]}.")
    bdn = define_bdn(options)
    exps = sunder.get_set(
        self,
        experiments,
        experiment_includes,
        experiment_excludes,
        label_type="experiment",
        no_null=True,
    )
    cons = sunder.get_set(
        self,
        conditions,
        condition_includes,
        condition_excludes,
        label_type="condition",
        no_null=True,
        no_media=True,
    )
    if no_processors > 1:
        no_processors, max_no_processors = omparallel.get_no_processors(
            no_processors
        )
        print(f"Using {no_processors} of {max_no_processors} processors.")
    for e in exps:
        for c in cons:
            # get data for reference strain
            try:
                t, (ywt, odwt) = sunder.extract_wells(
                    self.r, self.s, e, c, ref_strain, [f[0], "OD"]
                )
                ywt, keep = de_nan(ywt)

            except TypeError:
                # experiment missing condition or refstrain
                print(f"No reference data for {ref_strain} in {e}: {c}.")
                continue
            t = t[keep]
            odwt = odwt[keep, :]
            odwt[odwt < 0] = np.min(odwt[odwt > 0])
            # get data for Null
            _, yn = sunder.extract_wells(self.r, self.s, e, c, "Null", f)
            try:
                yn, _ = de_nan(yn)
            except TypeError:
                # condition missing Null strain
                print(f"No Null data for {e}: {c}.")
                continue
            if not sufficient_replicates(ywt, yn, ref_strain, c):
                continue
            # use all yn to estimate sy2
            sy2 = np.max([1e-4, np.var(np.log(yn))])
            params = {
                "experiment": e,
                "condition": c,
                "t": t,
                "ywt": ywt,
                "yn": yn,
                "odwt": odwt,
                "sy2": sy2,
                "bdn": bdn,
                "y_data_dict": {},
            }
            params = params | options
            # get strains
            all_strains = sunder.get_set(
                self,
                strains,
                strain_includes,
                strain_excludes,
                label_type="strain",
                no_null=True,
            )
            all_strains = [
                s
                for s in all_strains
                if f"{s} in {c}" in self.all_strains_conditions[e]
                and s != ref_strain
            ]
            if len(all_strains):
                # define data before parallel processing
                for s in all_strains:
                    y, od, success = get_tagged_strain_data(
                        self, e, c, s, f, keep
                    )
                    if success:
                        od[od < 0] = np.min(od[od > 0])
                        params["y_data_dict"][s] = (y, od)
                    else:
                        params["y_data_dict"][s] = None
                print(f"{c}: Processing {len(all_strains)} strains.")
                # correct autofluorescence
                if no_processors > 1:
                    # parallel
                    results = omparallel.process_strains_parallel(
                        process_strain, params, all_strains, no_processors
                    )
                else:
                    # sequential
                    results = [
                        process_strain(s, params)
                        for s in all_strains
                        if params["y_data_dict"][s] is not None
                    ]
                # finish up
                finish_store_plot(self, f, e, c, s, t, results, params)
            else:
                print(f"No strains found for {e}: {c}.")


def finish_store_plot(
    self,
    f,
    e,
    c,
    s,
    t,
    results,
    params,
):
    """Smooth, add results to s-dataframe, and plot."""
    for s, flperod_raw in results:
        flperod_samples, f_fitderiv = smooth_with_GPs(
            t,
            flperod_raw,
            bd=params["bdn"],
            fl_cv_fn=params["fl_cv_fn"],
            no_samples=params["no_samples"],
            experiment=e,
            condition=c,
            strain=s,
            max_data_pts=params["max_data_pts"],
        )
        store_results(
            self,
            f,
            e=e,
            c=c,
            s=s,
            t=t,
            flperod_samples=flperod_samples,
            flperod_raw=flperod_raw,
            corrected_name="bc" + f[0],
        )
        print(f"{e}: {s} in {c}")
        f_fitderiv.gp.results()
        print("---")
        if params["figs"]:
            omplot.inspect(
                self,
                fl=f[0],
                ylabel=f"bc{f[0]}perOD",
                strains=s,
                conditions=c,
                experiments=e,
            )
        if params["fitderiv_figs"]:
            f_fitderiv.plot_fit(e, c, s, "flperOD", "d/dtflperOD", logs=False)


def plot_noise(p, f, experiment, condition, strain, ref_strain):
    """Plot noise in y-channel from omniplate instance."""
    t, ywt = sunder.extract_wells(
        p.r, p.s, experiment, condition, ref_strain, f
    )
    ywt, od_keep = de_nan(ywt)
    t = t[od_keep]
    # get data for Null
    _, yn = sunder.extract_wells(p.r, p.s, experiment, condition, "Null", f)
    yn, _ = de_nan(yn)
    # get data for tagged strain
    y, od, _ = get_tagged_strain_data(
        p, experiment, condition, strain, f, od_keep, warn=False
    )
    title = f"{experiment}: {strain} in {condition}"
    plt.figure(figsize=(10, 6))
    plt.subplot(3, 1, 1)
    plt.plot(t, np.var(np.log(y), axis=1), "o", label="y")
    plt.plot(t, np.var(np.log(ywt), axis=1), ".", label="ywt")
    plt.plot(t, np.var(np.log(yn), axis=1), ".", label="yn")
    plt.grid()
    plt.yscale("log")
    plt.ylabel("Var(log fl)")
    plt.legend()
    plt.subplot(3, 1, 2)
    for j in range(y.shape[1]):
        plt.plot(t, y[:, j], color="b")
    plt.grid()
    plt.ylabel("fluorescence")
    plt.xlabel("time")
    plt.subplot(3, 1, 3)
    for j in range(od.shape[1]):
        plt.plot(t, y[:, j])
    plt.grid()
    plt.ylabel("OD")
    plt.xlabel("time")
    plt.suptitle(title)
    plt.tight_layout()
    plt.show(block=False)


def store_results(
    self, f, e, c, s, t, flperod_samples, flperod_raw, corrected_name
):
    """Create dict of results and add to data frames."""
    autofdict = {
        "experiment": e,
        "condition": c,
        "strain": s,
        "time": t,
    }
    autofdict[f"{corrected_name}perOD"] = np.mean(flperod_samples, 1)
    autofdict[f"{corrected_name}perOD_err"] = 2 * np.std(flperod_samples, 1)
    if flperod_raw.ndim == 1:
        flperod_raw = flperod_raw.reshape(flperod_raw.size, 1)
    autofdict[f"flperOD_raw_{f[0]}"] = flperod_raw[:, 0]
    omcorr.add_to_dataframes(self, autofdict)


def de_nan(y, most=True):
    """Remove NaN by discarding some replicates."""
    # NaNs are generated because experiments have different durations
    all_nan_cols = np.all(np.isnan(y), axis=0)
    y = y[:, ~all_nan_cols]
    counts = np.array(
        [np.where(~np.isnan(y[i, :]))[0].size for i in range(y.shape[0])]
    )
    if most:
        # choose the most replicates per time point
        keep = counts == counts.max()
    else:
        # choose the replicates with the longest duration
        keep = counts == counts[np.nonzero(counts)[0][-1]]
    return y[keep, :], keep


def sufficient_replicates(ywt, yn, ref_strain, c):
    """Check sufficient numbers of replicates."""
    sufficient = True
    if ywt.shape[1] < 3:
        print(
            f"There are only {ywt.shape[1]} replicates (<3)"
            f" for the {ref_strain} strain in {c}."
        )
        print("Abandoning correctauto.")
        sufficient = False
    if yn.shape[1] < 3:
        print(
            f"There are only {yn.shape[1]} replicates (<3)"
            f" for the Null strain in {c}."
        )
        print("Abandoning correctauto.")
        sufficient = False
    return sufficient


def get_tagged_strain_data(self, e, c, s, f, od_keep, warn=True):
    """Get and check data for fluorescently tagged strain."""
    success = True
    # get data for tagged strain
    if len(f) == 2:
        _, (y, z, od) = sunder.extract_wells(
            self.r, self.s, e, c, s, f.copy() + ["OD"]
        )
        y, z, _ = de_nan(y, z)
    elif len(f) == 1:
        _, (y, od) = sunder.extract_wells(
            self.r, self.s, e, c, s, f.copy() + ["OD"]
        )
        y, _ = de_nan(y)
    # make OD match t
    od = od[np.nonzero(od_keep)[0], :]
    if y.size == 0 or od.size == 0:
        if warn:
            print(f"Warning: No data found for {e}: {s} in {c}!!")
        success = False
    if y.shape[1] < 3:
        if warn:
            print(
                f"There are only {y.shape[1]} replicates (<3)"
                f" for {e}: {s} in {c}."
            )
            print("Abandoning correctauto.")
        success = False
    if len(f) == 2:
        return y, z, od, success
    elif len(f) == 1:
        return y, od, success


def smooth_with_GPs(
    t,
    y,
    bd,
    no_samples,
    experiment,
    condition,
    strain,
    fl_cv_fn,
    max_data_pts,
):
    """Smooth y, typically raw flperod, using a GP."""
    if np.any(y[~np.isnan(y)]):
        # run GP: omfitderiv deals with NaNs
        fitvar = "log(flperOD)"
        f_fitderiv = run_fit_deriv(
            t,
            y,
            fitvar,
            f"d/dt_{fitvar}",
            experiment=experiment,
            condition=condition,
            strain=strain,
            bd=bd,
            cvfn=fl_cv_fn,
            logs=False,
            negs_to_nan=False,
            max_data_pts=max_data_pts,
            plot_local_max=False,
        )
        if not f_fitderiv.success:
            print(
                "-> Smoothing failed for "
                f"{experiment}: {strain} in {condition}."
            )
            return np.nan * np.ones((t.size, no_samples))
        y_samples = f_fitderiv.fit_deriv_sample(no_samples)[0]
    else:
        print("No positive data.")
        # return all NaN
        y_samples = np.nan * np.ones((t.size, no_samples))
    return y_samples, f_fitderiv

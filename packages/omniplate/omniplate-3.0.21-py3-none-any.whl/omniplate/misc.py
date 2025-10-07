"""Miscellaneous functions."""

import gaussianprocessderivatives as gp
import matplotlib.pylab as plt
import numpy as np
from scipy import integrate
from scipy.interpolate import interp1d

import omniplate.clogger as clogger
import omniplate.omgenutils as gu
import omniplate.sunder as sunder
from omniplate.corrections import get_hypers, instantiate_GP
from omniplate.omstats import stats_err


@clogger.log
def average_over_expts(
    self,
    condition,
    strain,
    tvr="mean_OD",
    bd=False,
    add_noise=True,
    plot=False,
):
    """
    Average a time-dependent variable over all experiments.

    Uses a Matern Gaussian process.

    An alternative and best first choice is add_common_variable.

    Parameters
    ----------
    condition: string
        The condition of interest.
    strain: string
        The strain of interest.
    tvr: float
        The time-dependent variable to be averaged.
        For example, 'cGFPperOD' or 'mean_OD'.
    bd: dictionary, optional
        The limits on the hyperparameters for the Matern Gaussian process.
        For example, {0: (-5,5), 1: (-4,4), 2: (-5,2)}
        where the first element controls amplitude, setting the bounds to
        1e-5 and 1e5, the second controls flexibility, and the third
        determines the magnitude of the measurement error.
    add_noise: boolean
        If True, add the fitted magnitude of the measurement noise to the
        predicted standard deviation for better comparison with the spread
        of the data.

    Returns
    -------
    res: dictionary
        {'t' : time, tvr : time-dependent data, 'mn' : mean,
        'sd' : standard deviation}
        where 'mn' is the average found and 'sd' is its standard deviation.
        'tvr' is the data used to find the average.

    Examples
    --------
    >>> p.average_over_expts('1% Gal', 'GAL2', bd= {1: [-1,-1])})
    """
    # boundaries on hyperparameters
    if "OD" in tvr:
        bds = {0: (-4, 4), 1: (-1, 4), 2: (-6, 2)}
    else:
        bds = {0: (2, 12), 1: (-1, 4), 2: (4, 10)}
    if bd:
        bds = gu.merge_dicts(original=bds, update=bd)
    # extract data
    df = self.s[["experiment", "condition", "strain", "time", tvr]]
    ndf = df.query("condition == @condition and strain == @strain")
    # use GP to average over experiments
    x = ndf["time"].to_numpy()
    y = ndf[tvr].to_numpy()
    ys = y[np.argsort(x)]
    xs = np.sort(x)
    g = gp.maternGP(bds, xs, ys)
    print(f"Averaging over {tvr} experiments for {strain} in {condition}.")
    g.findhyperparameters(noruns=2, noinits=1000)
    g.results()
    g.predict(xs, addnoise=add_noise)
    if plot:
        plt.figure()
        g.sketch(".")
        plt.title("averaging " + strain + " in " + condition)
        plt.xlabel("time")
        plt.ylabel(tvr)
        plt.show(block=False)
    # return results as a dictionary
    res = {"t": xs, tvr: ys, "mn": g.f, "sd": np.sqrt(g.fvar)}
    return res


def get_fitness_penalty(
    self,
    ref,
    com,
    yvar="gr",
    figs=True,
    no_samples=100,
    abs=False,
    norm=False,
):
    """
    Estimate the difference in fitness between two strains.

    Calculate the area between typically two growth rate versus OD
    curves, normalised by the length along the OD-axis where they overlap.

    Parameters
    -----------
    self: omniplate.platereader instance
        An instance of platereader with data loaded.
    ref: list of strings
        For only a single experiment, a list of two strings. The first string
        specifies the condition and the second specifies the strain to be used
        for the reference to which fitness is to be calculated.
        With multiple experiments, a list of three strings. The first string
        specifies the experiment, the second specifies the condition, and the
        third specifies the strain.
    com: list of strings
        For only a single experiment, a list of two strings. The first string
        specifies the condition and the second specifies the strain to be
        compared with the reference.
        With multiple experiments, a list of three strings. The first string
        specifies the experiment, the second specifies the condition, and the
        third specifies the strain.
    yvar: string, optional
        The variable to be compared.
    figs: boolean, optional
        If True, a plot of the area between the two growth rate versus OD
        curves is shown.
    no_samples: integer
        The number bootstraps used to estimate the error.
    abs: boolean
        If True, integrate the absolute difference between the two curves.
    norm: boolean
        If True, returns the mean and variance of the area under the reference
        strain for normalisation.

    Returns
    -------
    fp: float
        The area between the two curves.
    err: float
        An estimate of the error in the calculated error, found by
        bootstrapping.
    reffp: float, optional
        The area beneath the reference strain.
    referr: float, optional
        An estimate of the error in the calculated area for the reference
        strain.

    Example
    -------
    >>> from omniplate as import PlateReader
    >>> from omniplate.misc import get_fitness_penalty
    >>> p = PlateReader("ExampleData.xlsx", "ExampleDataContents.xlsx",
            datadir="data")
    >>> p.get_stats(strains="WT", conditions = ["2% Mal", "WT"],
            ["2% Raf", "WT"])
    >>> fp, err = get_fitness_penalty(p, ["2% Mal", "WT"], ["2% Raf", "WT"])
    """
    if len(ref) == 2 & len(com) == 2:
        # add experiment
        ref.insert(0, self.all_experiments[0])
        com.insert(0, self.all_experiments[0])
    # get and sample from GPs
    if no_samples and yvar == "gr":
        # instantiate GPS to estimate errors
        for ecs in [ref, com]:
            e, c, s = ecs
            hypers, cvfn = get_hypers(self, e, c, s, yvar)
            if hypers is None or cvfn is None:
                raise SystemExit(
                    "\nYou must first run get_stats or set no_samples=0."
                )
            t, od = sunder.extract_wells(self.r, self.s, e, c, s, "OD")
            if ecs == ref:
                g_ref = instantiate_GP(hypers, cvfn, t, od)
            else:
                g_com = instantiate_GP(hypers, cvfn, t, od)
        # sample from GPs
        f0s, g0s = g_ref.sample(no_samples, derivs=1)
        f1s, g1s = g_com.sample(no_samples, derivs=1)
        xsref, ysref = np.exp(f0s), g0s
        xscom, yscom = np.exp(f1s), g1s

    else:
        # no estimates of errors
        if no_samples:
            print(
                "Cannot estimate errors - require y= 'gr' and a recently "
                "run get_stats"
            )
        xsref = self.s.query(
            "experiment == @ref[0] and condition == @ref[1] and "
            "strain == @ref[2]"
        )["OD mean"][:, None]
        ysref = self.s.query(
            "experiment == @ref[0] and condition == @ref[1] and "
            "strain == @ref[2]"
        )[yvar].to_numpy()[:, None]
        xscom = self.s.query(
            "experiment == @com[0] and condition == @com[1] and "
            "strain == @com[2]"
        )["OD mean"].to_numpy()[:, None]
        yscom = self.s.query(
            "experiment == @com[0] and condition == @com[1] and "
            "strain == @com[2]"
        )[yvar].to_numpy()[:, None]
        if xsref.size == 0 or ysref.size == 0:
            print(f"{ref[0]}: Data missing for {ref[2]} in {ref[1]}")
            return np.nan, np.nan
        elif xscom.size == 0 or yscom.size == 0:
            print(f"{com[0]}: Data missing for {com[2]} in {com[1]}")
            return np.nan, np.nan
    fps = np.zeros(xsref.shape[1])
    nrm = np.zeros(xsref.shape[1])
    samples = zip(
        np.transpose(xsref),
        np.transpose(ysref),
        np.transpose(xscom),
        np.transpose(yscom),
    )
    # process samples
    for j, (xref, yref, xcom, ycom) in enumerate(samples):
        # remove any double values in OD because of OD plateauing
        uxref, uiref = np.unique(xref, return_inverse=True)
        uyref = np.array(
            [
                np.median(yref[np.nonzero(uiref == i)[0]])
                for i in range(len(uxref))
            ]
        )
        uxcom, uicom = np.unique(xcom, return_inverse=True)
        uycom = np.array(
            [
                np.median(ycom[np.nonzero(uicom == i)[0]])
                for i in range(len(uxcom))
            ]
        )
        # interpolate data
        iref = interp1d(uxref, uyref, fill_value="extrapolate", kind="slinear")
        icom = interp1d(uxcom, uycom, fill_value="extrapolate", kind="slinear")
        # find common range of x
        uxi = np.max([uxref[0], uxcom[0]])
        uxf = np.min([uxref[-1], uxcom[-1]])
        # perform integration to find normalised area between curves
        if abs:

            def igrand(x):
                return np.abs(iref(x) - icom(x))

        else:

            def igrand(x):
                return iref(x) - icom(x)

        fps[j] = integrate.quad(igrand, uxi, uxf, limit=100, full_output=1)[
            0
        ] / (uxf - uxi)
        if norm:
            # calculate area under curve of reference strain as a normalisation
            def igrand(x):
                return iref(x)

            nrm[j] = integrate.quad(
                igrand, uxi, uxf, limit=100, full_output=1
            )[0] / (uxf - uxi)
        # an example figure
        if figs and j == 0:
            plt.figure()
            plt.plot(uxref, uyref, "k-", uxcom, uycom, "b-")
            x = np.linspace(uxi, uxf, np.max([len(uxref), len(uxcom)]))
            plt.fill_between(x, iref(x), icom(x), facecolor="red", alpha=0.5)
            plt.xlabel("OD")
            plt.ylabel(yvar)
            plt.legend(
                [
                    f"{ref[0]}: {ref[2]} in {ref[1]}",
                    f"{com[0]}: {com[2]} in {com[1]}",
                ],
                loc="upper left",
                bbox_to_anchor=(-0.05, 1.15),
            )
            plt.show(block=False)
    if norm:
        return (
            np.median(fps),
            stats_err(fps),
            np.median(nrm),
            stats_err(nrm),
        )
    else:
        return np.median(fps), stats_err(fps)

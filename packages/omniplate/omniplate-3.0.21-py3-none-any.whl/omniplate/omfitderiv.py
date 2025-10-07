"""Smooth and estimate time derivatives via Gaussian processes."""

import copy
import warnings

import gaussianprocessderivatives as gp
import matplotlib.pylab as plt
import numpy as np
from gaussianprocessderivatives import gaussianprocessException
from scipy.interpolate import interp1d

import omniplate.omgenutils as gu
import omniplate.omstats as omstats


def run_fit_deriv(
    t,
    d,
    fitvar,
    derivname,
    experiment,
    condition,
    strain,
    bd=False,
    cvfn="matern",
    empirical_errors=False,
    no_runs=10,
    exit_early=True,
    no_inits=100,
    no_samples=100,
    logs=False,
    negs_to_nan=True,
    find_areas=False,
    plot_local_max=True,
    print_peak_properties=False,
    linalg_max=5,
    max_data_pts=None,
    **kwargs,
):
    """
    Run fitderiv to smooth and estimate time derivatives for a single data set.

    Parameters
    ----------
    t: array
        An array of times.
    d: array
        An array of measurements of the variable to be fit.
    fitvar: string
        The name of the variable to be fit.
    derivname: string
        The name of the first time derivative of the variable.
    experiment: string
        The name of the experiment of interest.
    condition: string
        The condition of interest.
    strain: string
        The strain of interest.
    ylabels: list of strings
        The labels for the y-axis
    bd: dictionary, optional
        The bounds on the hyperparameters for the Gaussian process.
        For example, bd= {1: [-2,0])} fixes the bounds on the
        hyperparameter controlling flexibility to be 1e-2 and 1e0.
        The default for a Matern covariance function
        is {0: (-5,5), 1: (-4,4), 2: (-5,2)},
        where the first element controls amplitude, the second controls
        flexibility, and the third determines the magnitude of the
        measurement error.
    cvfn: string, optional
        The covariance function used in the Gaussian process, either
        'matern' or 'sqexp' or 'nn'.
    empirical_errors: boolean, optional
        If True, measurement errors are empirically estimated from the
        variance across replicates at each time point and so vary with
        time.
        If False, the magnitude of the measurement error is fit from the
        data assuming that this magnitude is the same at all time points.
    no_runs: integer, optional
        The number of attempts made for each fit. Each attempt is made
        with random initial estimates of the hyperparameters within their
        bounds.
    exit_early: boolean, optional
        If True, stop at the first successful fit.
        If False, use the best fit from all successful fits.
    no_inits: integer, optional
        The number of random attempts to find a good initial condition
        before running the optimization.
    no_samples: integer, optional
        The number of samples used to calculate errors in statistics by
        bootstrapping.
    logs: boolean, optional
        If True, find the derivative of the log of the data and should be
        True to determine the specific growth rate when dtype= 'OD'.
    negs_to_nan: boolean, optional
            If logs=True, negs_to_nan=True causes all negative numbers to be set
            to np.nan; negs_to_nan=False, causes all negative numbers to be set
            almost zero.
    find_areas: boolean, optional
        If True, find the area under the plot of gr vs OD and the area
        under the plot of OD vs time. Setting to True can make get_stats
        slow.
    plot_local_max: boolean, optional
        If True, mark the highest local maxima found, which is used to
        calculate statistics, on any plots.
    print_peak_properties: boolean, optional
        If True, show properties of any local peaks that have found by
        scipy's find_peaks. Additional properties can be specified as
        kwargs and are passed to find_peaks.
    linalg_max: int, optional
        The number of linear algebra errors to tolerate.
    max_data_pts: integer, optional
        If set, sufficiently large data sets with multiple replicates will
        be subsampled at each time point, randomly picking a smaller
        number of replicates, to reduce the number of data points and so
        run times.
    kwargs: passed to scipy's find_peaks.
    """
    print(f"Fitting {fitvar} for {experiment}: {strain} in {condition}")
    # define statnames
    statnames = [
        f"min_{fitvar}",
        f"max_{fitvar}",
        f"range_{fitvar}",
        f"max_{derivname}",
        f"time_of_max_{derivname}",
    ]
    if derivname == "gr":
        # special names when estimating specific growth rate
        statnames += ["doubling_time", "lag_time"]
    else:
        statnames += [
            f"doubling_time_from_{derivname}",
            f"lag_time_from_{derivname}",
        ]
    # call fitderiv
    f = FitDeriv(
        t,
        d,
        cvfn=cvfn,
        logs=logs,
        negs_to_nan=negs_to_nan,
        no_runs=no_runs,
        no_inits=no_inits,
        exit_early=exit_early,
        bd=bd,
        empirical_errors=empirical_errors,
        linalg_max=linalg_max,
        max_data_pts=max_data_pts,
    )
    if f.success:
        # check derivative has been sensibly defined
        if np.max(np.abs(f.df)) < 1.0e-20 and (
            f.dfvar.size > 1 and np.max(np.abs(np.diff(f.dfvar))) < 1.0e-20
        ):
            print(
                "\nWarning: fitderiv may have failed for"
                f" {experiment}: {strain} in {condition}."
            )
        df_for_s, dict_for_sc, peak_coords = (
            omstats.find_smoothed_data_summary_stats(
                fitvar=fitvar,
                derivname=derivname,
                statnames=statnames,
                no_samples=no_samples,
                f=f,
                t=t,
                e=experiment,
                c=condition,
                s=strain,
                find_areas=find_areas,
                plot_local_max=plot_local_max,
                print_peak_properties=print_peak_properties,
                **kwargs,
            )
        )
        if peak_coords is not None:
            f.peak_coords = peak_coords
        # store GP parameters
        dict_for_sc[f"logmaxlikehood_for_{derivname}"] = f.logmaxlike
        dict_for_sc["gp_for_" + derivname] = cvfn
        for j, val in enumerate(f.lth):
            dict_for_sc[f"log_hyperparameter_{j}_for_{derivname}"] = val
        f.df_for_s = df_for_s
        f.dict_for_sc = dict_for_sc
        return f
    else:
        raise Exception("fitderiv failed.")


class FitDeriv:
    """
    Smooth and estimate the time derivative of the data via Gaussian processes.

    After a successful optimisation, the following attributes are generated:

    t: array
        The times specified as input.
    d: array
        The data specified as input.
    f: array
        The mean of the Gaussian process with the optimal hyperparmeters
        at each time point.
    fvar: array
        The variance of the optimal Gaussian process at each time point.
    df: array
        The inferred first time-derivative.
    dfvar: array
        The inferred variance of the first time-derivative.
    ddf: array
        The inferred second time-derivative.
    ddfvar: array
        The inferred variance of the second time-derivative.

    Examples
    --------
    A typical work flow is:

    >>> from fitderiv import FitDeriv
    >>> q= FitDeriv(t, od)
    >>> q.plot_fit('df')

    or potentially

    >>> import matplotlib.pyplot as plt
    >>> plt.plot(q.t, q.d, 'r.', q.t, q.y, 'b')

    Reference
    ---------
    PS Swain, K Stevenson, A Leary, LF Montano-Gutierrez, IBN Clark, J Vogel,
    and T Pilizota.
    Inferring time derivatives including growth rates using Gaussian processes
    Nat Commun 7 (2016) 13766
    """

    def __init__(
        self,
        t,
        d,
        cvfn="matern",
        logs=True,
        negs_to_nan=True,
        no_runs=5,
        no_inits=100,
        exit_early=False,
        bd=None,
        empirical_errors=False,
        optmethod="L-BFGS-B",
        runtime_warn=False,
        linalg_max=3,
        max_data_pts=None,
        warn=False,
    ):
        """
        Smooth data and estimate time derivatives with a Gaussian process.

        Parameters
        ----------
        t: 1D array
            The time points.
        d: array
            The data corresponding to the time points with any replicates given
             as columns.
        cvfn: string
            The type of kernel function for the Gaussian process either 'sqexp'
            (squared exponential) or 'matern' (Matern with nu= 5/2) or 'nn'
            (neural network).
        logs: boolean
            If True, the Gaussian process is used to smooth the natural
            logarithm of the data and the time-derivative is therefore of the
            logarithm of the data.
        negs_to_nan: boolean, optional
            If logs=True, negs_to_nan=True causes all negative numbers to be set
            to np.nan; negs_to_nan=False, causes all negative numbers to be set
            almost zero.
        no_runs: integer, optional
            The number of attempts to be made at optimising the kernel's
            hyperparmeters.
        no_inits: integer, optional
            The number of random attempts made to find good initial choices for
            the hyperparameters before running their optimisation.
        exit_early: boolean, optional
            If True, stop at the first successful attempt at optimising the
            hyperparameters otherwise take the best choice from all successful
            optimisations.
        bd: dictionary, optional
            Specifies the limits on the hyperparameters for the Gaussian process.
            For example, bd= {0: [-1, 4], 2: [2, 6]})
            sets confines the first hyperparameter to be between 1e-1 and 1e^4
            and confines the third hyperparmater between 1e2 and 1e6.
        empirical_errors: boolean, optional
            If True, measurement errors are empirically estimated by the
            variance across replicates at each time point.
            If False, the variance of the measurement error is assumed to be
            the same for all time points and its magnitude is a hyperparameter
            that is optimised.
        optmethod: string, optional
            The algorithm used to optimise the hyperparameters, either
            'l_bfgs_b' or 'tnc'.
        warn: boolean, optional
            If False, warnings created by covariance matrices that are not
            positive semi-definite are suppressed.
        linalg_max: integer, optional
            The number of times errors generated by underlying linear algebra
            modules during the optimisation by poor choices of the
            hyperparameters should be ignored.
        max_data_pts: integer, optional
            If set, sufficiently large data sets with multiple replicates will
            be subsampled at each time point, randomly picking a smaller
            number of replicates, to reduce the number of data points and so
            run times.
        """
        self.linalg_max = linalg_max
        if not runtime_warn:
            # warning generated occasionally when sampling from the Gaussian
            # process likely because of numerical errors
            warnings.simplefilter("ignore", RuntimeWarning)
        try:
            noreps = d.shape[1]
        except IndexError:
            noreps = 1
        self.d = np.copy(d)
        self.t = np.copy(t)
        t = self.t
        d = self.d
        # default bounds for hyperparameters
        bddict = {
            "nn": {0: (-1, 5), 1: (-7, -2), 2: (-6, 2)},
            "sqexp": {0: (-5, 5), 1: (-6, 2), 2: (-5, 2)},
            "matern": {0: (-5, 5), 1: (-4, 4), 2: (-2, 0)},
        }
        # find bounds
        if bd:
            bds = bddict[cvfn] | bd
        else:
            bds = bddict[cvfn]
        # log data
        if logs:
            print("Taking natural logarithm of the data.")
            if np.nonzero(d <= 0)[0].size > 0:
                if negs_to_nan:
                    print("Warning: Negative data is being set to NaN.")
                    # replace zeros and negs so that logs can be applied
                    d[np.nonzero(d <= 0)] = np.nan
                else:
                    # NB too small values can generate odd samples from the GPs
                    print("Warning: Negative data is being set close to zero.")
                    d[np.nonzero(d <= 0)] = np.finfo(float).eps
            # take log of data
            d = np.log(np.asarray(d))
        # run checks and define measurement errors
        if empirical_errors:
            # errors must be empirically estimated
            if noreps > 1:
                lod = [
                    np.count_nonzero(np.isnan(d[:, i])) for i in range(noreps)
                ]
                if np.sum(np.diff(lod)) != 0:
                    print(
                        "The replicates have different number of data "
                        "points, but equal numbers of data points are "
                        "needed for empirically estimating errors."
                    )
                    merrors = None
                else:
                    # estimate errors empirically
                    print("Estimating measurement errors empirically.")
                    merrors = gu.find_smooth_variance(d)
            else:
                print("Not enough replicates to estimate errors empirically.")
                merrors = None
        else:
            merrors = None
        ta, da, ma, preprocessing_success = preprocess_data(
            t, d, merrors, max_data_pts
        )
        if preprocessing_success:
            self.run(
                cvfn=cvfn,
                bds=bds,
                ta=ta,
                da=da,
                ma=ma,
                no_runs=no_runs,
                no_inits=no_inits,
                exit_early=exit_early,
                optmethod=optmethod,
            )

    def run(
        self,
        cvfn,
        bds,
        ta,
        da,
        ma,
        no_runs,
        no_inits,
        exit_early,
        optmethod,
    ):
        """Instantiate and run a Gaussian process."""
        try:
            # instantiate GP
            g = getattr(gp, cvfn + "GP")(bds, ta, da, merrors=ma)
            print("Using a " + g.description + ".")
        except NameError:
            raise Exception("Gaussian process not recognised.")
        try:
            # optimise parameters
            g.findhyperparameters(
                noruns=no_runs,
                noinits=no_inits,
                exitearly=exit_early,
                optmethod=optmethod,
                linalgmax=self.linalg_max,
            )
            # display results
            if np.any(ma):
                # check measurement errors
                if len(ma) != len(self.t):
                    # NaNs have been removed
                    mainterp = interp1d(
                        ta, ma, bounds_error=False, fill_value=(ma[0], ma[-1])
                    )
                    ma = mainterp(self.t)
            g.predict(self.t, derivs=2, addnoise=True, merrorsnew=ma)
            self.success = True
            # results
            self.gp = g
            self.logmaxlike = -g.nlml_opt
            self.hparamerr = g.hparamerr
            self.lth = g.lth_opt
            self.f = g.f
            self.df = g.df
            self.ddf = g.ddf
            self.fvar = g.fvar
            self.dfvar = g.dfvar
            self.ddfvar = g.ddfvar
        except gaussianprocessException:
            self.success = False

    def fit_deriv_sample(self, no_samples, newt=None):
        """
        Generate samples from the latent function.

        Both values for the latent function and its first two
        derivatives are returned, as a tuple.

        All derivatives must be sampled because by default all are asked
        to be predicted by the underlying Gaussian process.

        Parameters
        ----------
        no_samples: integer
            The number of samples.
        newt: array, optional
            Time points for which the samples should be made.
            If None, the orginal time points are used.

        Returns
        -------
        samples: a tuple of arrays
            The first element of the tuple gives samples of the latent
            function;
            the second element gives samples of the first time derivative; and
            the third element gives samples of the second time derivative.
        """
        if np.any(newt):
            newt = np.asarray(newt)
            # make prediction for new time points
            gps = copy.deepcopy(self.gp)
            gps.predict(newt, derivs=2, addnoise=True)
        else:
            gps = self.gp
        samples = gps.sample(no_samples, derivs=2)
        return samples

    def plot_fit(
        self,
        experiment,
        condition,
        strain,
        fitvar,
        derivname,
        logs,
    ):
        """Create figure using subplot_fit to generate subplots."""
        figtitle = f"{experiment}: {strain} in {condition}"
        plt.figure()
        plt.subplot(2, 1, 1)
        self.subplot_fit("f", ylabel=fitvar, figtitle=figtitle, logs=logs)
        plt.subplot(2, 1, 2)
        self.subplot_fit("df", logs=logs, ylabel=derivname)
        # add dot on largest local peak
        if hasattr(self, "peak_coords"):
            plt.plot(
                self.peak_coords[0],
                self.peak_coords[1],
                "o",
                color="yellow",
                markeredgecolor="k",
            )
        plt.tight_layout()
        plt.show(block=False)

    def subplot_fit(
        self,
        char="f",
        errorfac=1,
        logs=None,
        xlabel="time",
        ylabel=False,
        figtitle=False,
    ):
        """
        Plot the results of the fitting.

        Either the data and the mean of the optimal Gaussian process or
        the inferred time derivatives are plotted.

        Parameters
        ----------
        char: string
            The variable to plot either 'f' or 'df' or 'ddf'.
        errorfac: float, optional
            The size of the errorbars are errorfac times the standard deviation
            of the optimal Gaussian process.
        ylabel: string, optional
            A label for the y-axis.
        figtitle: string, optional
            A title for the figure.
        """
        x = getattr(self, char)
        xv = getattr(self, char + "var")
        if char == "f":
            if logs:
                d = np.log(self.d)
            else:
                d = self.d
            plt.plot(self.t, d, "r.")
        plt.plot(self.t, x, "b")
        plt.fill_between(
            self.t,
            x - errorfac * np.sqrt(xv),
            x + errorfac * np.sqrt(xv),
            facecolor="blue",
            alpha=0.2,
        )
        if ylabel:
            plt.ylabel(ylabel)
        else:
            plt.ylabel(char)
        plt.xlabel(xlabel)
        if figtitle:
            plt.title(figtitle)


def subsample_data(t, d, no_samples=2000):
    """
    Subsample replicate data.

    At each time point, randomly choose only some of the replicates.
    """
    rng = np.random.default_rng()
    ta = np.repeat(t.reshape(-1, 1), d.shape[1], axis=1)
    rd = d[np.isfinite(d)]
    ta = ta[np.isfinite(d)]
    # make dict with time points as keys and corresponding d as values
    t_dict = {tv: rd[np.where(ta == tv)[0]] for tv in t}
    no_samples_per_tpt = np.max([1, int(no_samples / t.size)])
    # subsample
    nd = np.array(
        [
            (
                rng.choice(t_dict[tv], no_samples_per_tpt, replace=False)
                if no_samples_per_tpt < t_dict[tv].size
                else rng.choice(t_dict[tv], no_samples_per_tpt, replace=True)
            )
            for tv in t_dict
        ]
    )
    return nd


def preprocess_data(t, d, merrors, max_data_pts):
    """Remove nans and make 1D."""
    try:
        noreps = d.shape[1]
    except IndexError:
        noreps = 1
    # subsample if excessive data
    rd = d[~np.isnan(d)]
    if max_data_pts and rd.size > max_data_pts:
        print(
            f"Many data points - {rd.size}: subsampling for each time point."
        )
        nd = subsample_data(t, d, max_data_pts)
        print(f"Using {nd.size} data points.")
    else:
        nd = d
    # combine data into one array
    tb = np.tile(t, noreps)
    db = np.reshape(nd, nd.size, order="F")
    # check for NaNs
    if np.any(merrors):
        mb = np.tile(merrors, noreps)
        keep = np.intersect1d(
            np.nonzero(~np.isnan(db))[0], np.nonzero(~np.isnan(mb))[0]
        )
    else:
        keep = np.nonzero(~np.isnan(db))[0]
    # remove any NaNs
    da = db[keep]
    ta = tb[keep]
    # check data remains after removing NaNs
    success = True
    if not da.size:
        print("Warning: omfitderiv failed - too many NaNs.")
        success = False
    elif np.any(merrors):
        # measurement errors
        ma = mb[keep]
        if not ma.size:
            print("Warning: omfitderiv failed - too many NaNs.")
            success = False
    else:
        ma = None
    return ta, da, ma, success

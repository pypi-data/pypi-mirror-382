"""
Functions for performing corrections.

For non-linearity in the OD, for the fluorescence of the media,
and for autofluorescence.
"""

import importlib.resources as import_files
import re

import gaussianprocessderivatives as gp
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from nunchaku import Nunchaku
from scipy.interpolate import interp1d
from scipy.optimize import minimize_scalar
from statsmodels.nonparametric.smoothers_lowess import lowess

import omniplate.admin as admin
import omniplate.clogger as clogger
import omniplate.omerrors as errors
import omniplate.omgenutils as gu
import omniplate.sunder as sunder
from omniplate.correct_auto_bayesian import correct_auto_bayesian
from omniplate.omfitderiv import preprocess_data, run_fit_deriv


@clogger.log
def correct_OD(
    self,
    figs=True,
    bd=None,
    gp_results=False,
    OD_fname=None,
    OD_match_min=0.1,
    max_nunchaku_segments=4,
    correct_for_media=True,
    frac=0.33,
    null_dict=None,
    experiments="all",
    experiment_includes=False,
    experiment_excludes=False,
    conditions="all",
    condition_includes=False,
    condition_excludes=False,
):
    """
    Correct for the non-linear relationship between OD and cell number.

    Requires a set of dilution data set, with the default being haploid
    yeast growing in glucose.

    An alternative can be loaded from a file - a txt file of two columns
    with OD specified in the first column and the dilution factor specified
    in the second.

    Parameters
    ---------
    figs: boolean, optional
        If True, a plot of the fit to the dilution data is produced.
    bd: dictionary, optional
        Specifies the limits on the hyperparameters for the Gaussian
        process.
        For example, bd= {0: [-1, 4], 2: [2, 6]})
        sets confines the first hyperparameter to be between 1e-1 and 1e^4
        and confines the third hyperparameter between 1e2 and 1e6.
    gp_results: boolean, optional
        If True, show the results of fitting the Gaussian process
    OD_fname: string, optional
        The name of the file with the dilution data used to correct OD for
        its non-linear dependence on numbers of cells. If unspecified, data
        for haploid budding yeast growing in glucose is used.
    OD_match_min: float, optional
        An expected minimal value of the OD up to which there is a linear
        scaling of the OD with cell numbers.
    max_nunchaku_segments: int, optional
        The number of segments used by nunchaku when finding the inital
        region where the relationship between the dilution factor and OD
        is linear.
    correctformedia: boolean, optional
        If True (default), correct OD for background levels from media.
    frac: float
        The fraction of the data used for smoothing the media OD via lowess.
        Used to correct OD for the background OD of the media.
    null_dict: dict[str, list[str]], optional
        A dictionary specifying which Null conditions should be used to correct
        other conditions.
        For example:
            null_dict= {"2% glu": ["all"]}
        means that all conditions should be corrected using "Null in 2% glu";
            null_dict= {"2% glu": ["2% glu 0.1 mg/ml", "2% glu 0.2 mg/ml"],
                        "2% gal": ["2% gal 0.1 mg/ml"]}
        means that "2% glu 0.1 mg/ml" and "2% glu 0.2 mg/ml" should be
        corrected with "Null in 2% glu" and that "2% gal 0.1 mg/ml" should
        be corrected with "Null in 2% gal".
    experiments: string or list of strings
        The experiments to include.
    conditions: string or list of strings
        The conditions to include.
    experiment_includes: string, optional
        Selects only experiments that include the specified string in their
        name.
    experiment_excludes: string, optional
        Ignores experiments that include the specified string in their
        name.
    condition_includes: string, optional
        Selects only conditions that include the specified string in their
        name.
    condition_excludes: string, optional
        Ignores conditions that include the specified string in their name.

    Examples
    -------
    >>> p.correctOD()
    >>> p.correctOD(figs= False)
    """
    exps = sunder.get_set(
        self,
        experiments,
        experiment_includes,
        experiment_excludes,
        "experiment",
        no_null=True,
    )
    cons = sunder.get_set(
        self,
        conditions,
        condition_includes,
        condition_excludes,
        "condition",
        no_null=True,
        no_media=False,
    )
    # fit dilution data
    gc, od_match = find_OD_correction(
        datadir_path=self.datadir_path,
        OD_fname=OD_fname,
        figs=figs,
        bd=bd,
        gp_results=gp_results,
        OD_match_min=OD_match_min,
        max_nunchaku_segments=max_nunchaku_segments,
    )
    print()
    # correct ODs
    for e in exps:
        for c in cons:
            if correct_for_media:
                correct_OD_for_media(
                    self,
                    figs=figs,
                    frac=frac,
                    experiments=e,
                    conditions=c,
                    null_dict=null_dict,
                )
            # correct all wells
            r_data = self.r.query(
                "experiment == @e and condition == @c"
            ).OD.to_numpy()
            gc.batchpredict(r_data)
            # leave small ODs unchanged
            new_r = gc.f
            new_r[r_data < od_match] = r_data[r_data < od_match]
            # update r data frame
            self.r.loc[
                (self.r.experiment == e) & (self.r.condition == c),
                "OD",
            ] = new_r
    if self.progress["negative_values"][e]:
        print(
            "Warning: correcting OD for media has created "
            f"negative values in {e} for"
        )
        # ignore final newline
        print(self.progress["negative_values"][e][:-1])
    # update s dataframe
    admin.update_s(self)


def find_OD_correction(
    datadir_path,
    OD_fname,
    figs,
    bd,
    gp_results,
    OD_match_min,
    max_nunchaku_segments,
):
    """
    Determine a function to correct OD.

    Use a Gaussian process to fit serial dilution data to correct for
    non-linearities in the relationship between OD and cell density.

    The data are either loaded from file od_fname or the default
    data for haploid yeast growing in glucose are used.
    """
    print("Fitting dilution data for OD correction for non-linearities.")
    if OD_fname is not None:
        try:
            od_df = pd.read_csv(
                str(datadir_path / OD_fname),
                sep=None,
                engine="python",
                header=None,
            )
            print(f"Using {OD_fname}")
            od_data = od_df.to_numpy()
            od, dilfac = od_data[:, 0], od_data[:, 1]
        except (FileNotFoundError, OSError):
            raise errors.FileNotFound(str(datadir_path / OD_fname))
    else:
        print("Using default data.")
        fname = "dilution_data_xiao.tsv"
        od, dilfac = read_default_dilution_data(fname)
    od, dilfac = arrange_into_replicates(od, dilfac)
    # run nunchaku
    X = np.mean(dilfac, 1)
    nc = Nunchaku(X, od.T, estimate_err=True, prior=[-5, 5])
    num_regions, _ = nc.get_number(max_nunchaku_segments)
    bds, _ = nc.get_iboundaries(num_regions)
    # find linear region, which starts from origin
    od_match_pts = np.mean(od, 1)[bds]
    # pick end point with OD at least equal to OD_match_min
    ipick = np.where(od_match_pts > OD_match_min)[0][0]
    od_match = od_match_pts[ipick]
    dilution_factor_match = X[bds[ipick]]
    # process data
    dilfac = dilfac.flatten()[np.argsort(od.flatten())]
    od = np.sort(od.flatten())
    # rescale so that OD and dilfac match
    y = dilfac / dilution_factor_match * od_match
    # set up Gaussian process
    bds = {0: (-4, 4), 1: (-4, 4), 2: (-3, -1)}
    # find bounds
    if bd is not None:
        bds = gu.merge_dicts(original=bds, update=bd)
    gc = gp.maternGP(bds, od, y)
    # run Gaussian process
    gc.findhyperparameters(noruns=5, exitearly=True, quiet=True)
    if gp_results:
        gc.results()
    gc.predict(od)
    if figs:
        plt.figure()
        gc.sketch(".")
        plt.plot(od_match, od_match, "bs")
        plt.grid(True)
        plt.xlabel("OD")
        plt.ylabel("corrected OD (relative cell numbers)")
        if OD_fname:
            plt.title("Fitting " + OD_fname)
        else:
            plt.title("for haploid budding yeast in glucose")
        plt.show(block=False)
    return gc, od_match


def read_default_dilution_data(fname):
    """Import default dilution data."""
    d = import_files.read_text("omniplate", fname)
    res = np.array(re.split(r"\n|\t", d)[:-1]).astype(float)
    od, dilfac = res[::2], res[1::2]
    if fname == "dilution_data_xiao.tsv":
        # missing replicate - use mean of existing ones
        dilfac = np.insert(dilfac, 0, dilfac[0])
        od = np.insert(od, 0, np.mean(od[:2]))
    else:
        raise ValueError("Dilution data unrecognised.")
    return od, dilfac


def arrange_into_replicates(od, dilfac):
    """Rearrange so that data from each replicate is in a column."""
    unique_dilfac, indices, counts = np.unique(
        dilfac, return_inverse=True, return_counts=True
    )
    unique_counts = np.unique(counts)
    if len(unique_counts) == 1:
        no_reps = np.unique(counts)[0]
        dilfac_reps = np.tile(np.atleast_2d(unique_dilfac).T, no_reps)
        od_reps = np.array(
            [od[indices == i] for i in range(unique_dilfac.size)]
        ).reshape((unique_dilfac.size, no_reps))
        return od_reps, dilfac_reps
    else:
        raise ValueError(
            "There are inconsistent numbers of replicates"
            " in the OD correction data."
        )


@clogger.log
def correct_OD_for_media(
    self,
    figs=False,
    frac=0.33,
    null_dict=None,
    experiments="all",
    experiment_includes=False,
    experiment_excludes=False,
    conditions="all",
    condition_includes=False,
    condition_excludes=False,
):
    """
    Correct OD or fluorescence for that of the media.

    Use data from wells marked Null.

    Use lowess to smooth measurements from all Null wells and subtract
    this smoothed time series from the raw data.
    """
    exps = sunder.get_set(
        self,
        experiments,
        experiment_includes,
        experiment_excludes,
        "experiment",
        no_null=True,
    )
    cons = sunder.get_set(
        self,
        conditions,
        condition_includes,
        condition_excludes,
        "condition",
        no_null=True,
        no_media=False,
    )
    for e in exps:
        for c in cons:
            if c in self.all_conditions[e]:
                print(f"{e} - {c}: Correcting OD for the OD of the medium.")
                neg_values = find_Null_and_correct(
                    self,
                    df=self.r,
                    dtype="OD",
                    e=e,
                    c=c,
                    figs=figs,
                    frac=frac,
                    null_dict=null_dict,
                )
                if neg_values is not None:
                    if not self.progress["negative_values"][e]:
                        self.progress["negative_values"][e] = neg_values
                    else:
                        self.progress["negative_values"][e] += neg_values
    # update s dataframe
    admin.update_s(self)


def find_Null_and_correct(self, df, dtype, e, c, figs, frac, null_dict):
    """Find data for Null strain and pass df to perform_media_correction."""
    null_e, null_c = e, c
    if null_dict:
        for medium, conditions in null_dict.items():
            if conditions == ["all"] or null_c in conditions:
                null_c = medium
                break
    null_df = self.r[
        (self.r.experiment == null_e)
        & (self.r.condition == null_c)
        & (self.r.strain == "Null")
    ]
    if null_df.empty:
        print(f"{e}: No Null strain found for {c}.")
    else:
        neg_values = perform_media_correction(
            null_df=null_df,
            df=df,
            dtype=dtype,
            experiment=e,
            condition=c,
            figs=figs,
            frac=frac,
        )
        return neg_values


def perform_media_correction(
    null_df, df, dtype, experiment, condition, figs, frac
):
    """
    Correct data of type dtype for any signal from the media.

    Data for the Null strain is in null_df; data to be ovewritten
    is in df.

    Use lowess to smooth over time the media data from the Null
    wells and subtract the smoothed values from the data.
    """
    t, null_data = null_df["time"].to_numpy(), null_df[dtype].to_numpy()
    if ~np.any(null_data[~np.isnan(null_data)]):
        # all data is NaN
        return
    # find correction
    res = lowess(null_data, t, frac=frac)
    correctionfn = interp1d(
        res[:, 0],
        res[:, 1],
        fill_value=(res[0, 1], res[-1, 1]),
        bounds_error=False,
    )
    if figs:
        plt.figure()
        plt.plot(t, null_data, "ro", res[:, 0], res[:, 1], "b-")
        plt.xlabel("time (hours)")
        plt.title(
            f"{experiment}: media correction for {dtype} in {condition}."
        )
        plt.show(block=False)
    # perform correction to data in df
    choose = (df.experiment == experiment) & (df.condition == condition)
    df.loc[choose, dtype] = df[choose][dtype] - correctionfn(
        df[choose]["time"]
    )
    # check for any negative values
    neg_values = ""
    for s in np.unique(df[choose]["strain"][df[choose][dtype] < 0]):
        if s != "Null":
            wstr = f"\t{dtype}: {s} in {condition} for wells "
            for well in np.unique(
                df[choose][df[choose].strain == s]["well"][
                    df[choose][dtype] < 0
                ]
            ):
                wstr += f"{well}, "
            wstr = wstr[:-2] + "\n"
            neg_values += wstr
    return neg_values


@clogger.log
def correct_auto(
    self,
    f="GFP",
    ref_strain="WT",
    no_processors=1,
    options=None,
    experiments="all",
    experiment_includes=False,
    experiment_excludes=False,
    conditions="all",
    condition_includes=False,
    condition_excludes=False,
    strains="all",
    strain_includes=False,
    strain_excludes=False,
):
    """
    Correct fluorescence for autofluorescence.

    The correction is made using the fluorescence of an untagged
    reference strain.

    Arguments
    --
    f: string
        The fluorescence measurements, typically either 'mCherry' or
        'GFP'.
    ref_strain: string
        The reference strain used to estimate autofluorescence.
    no_processors: int (default: 1)
        The number of processors to use. Numpy has built-in parallelisation
        and using one processor may be fastest.
    options: None or Dict
       The keys of options are:
            bd: dict (default: None)
                Specifies the bounds on the hyperparameters for the
                Gaussian process applied to the logarithm of the inferred
                fluorescence.
                e.g. {2: (-2, 0)}.
            figs: boolean (default: True)
                If True, use omplot.inspect to show raw data and inferred
                fluorescence per cell.
            no_boots: int (default: 10)
                The number of bootstrapped data sets to fit. Larger numbers
                give better estimates of errors.
            fl_cv_fn: str (default: "matern")
                The covariance function to use for the Gaussian process
                that smooths the inferred fluorescence.
            no_samples: int (default: 1000)
                The number of samples taken to estimate errors from the
                Gaussian process used to smooth the inferred fluorescence.
            max_data_pts: int or None (default: None)
                The maximum number of data points to allow in the Gaussian
                process smoothing before subsampling.
            fitderiv_figs: boolean (default: False)
                If True, show the results of the Gaussian process smoothing.
    experiments: string or list of strings
        The experiments to include.
    conditions: string or list of strings
        The conditions to include.
    strains: string or list of strings
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

    Examples
    --------
    >>> p.correctauto('GFP', options = {"figs": False, "bd": {2: (-1,3)}})
    >>> p.correctauto('mCherry', ref_strain= 'BY4741')
    """
    f = gu.make_list(f)
    if len(f) != 1:
        print("Error: correctauto uses only one fluorescence measurement.")
        return
    # correct for autofluorescence
    default_options = {
        "bd": None,
        "figs": True,
        "no_boots": 10,
        "fl_cv_fn": "matern",
        "no_samples": 1000,
        "max_data_pts": None,
        "fitderiv_figs": False,
    }
    if options is None:
        options = default_options
    else:
        options = default_options | options
    print(
        f"\nCorrecting autofluorescence using {ref_strain} as the reference."
    )
    correct_auto_bayesian(
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
    )


@clogger.log
def correct_auto_l(
    self,
    f=["GFP", "AutoFL"],
    ref_strain="WT",
    method="default",
    options=None,
    experiments="all",
    experiment_includes=False,
    experiment_excludes=False,
    conditions="all",
    condition_includes=False,
    condition_excludes=False,
    strains="all",
    strain_includes=False,
    strain_excludes=False,
):
    """
    Correct fluorescence for autofluorescence.

    The correction is made using the fluorescence of an untagged
    reference strain.

    The reference strain is used to estimate the autofluorescence via
    either the method of Lichten et al., 2014, where measurements of
    fluorescence at two wavelengths is required, or by using the
    fluorescence of the reference strain interpolated to the OD of the
    strain of interest (Berthoumieux et al., 2013).

    Using two measurements of fluorescence is thought to be more accurate,
    particularly for low fluorescence measurements (Mihalcescu et al.,
    2015).

    Arguments
    --
    f: string or list of strings
        The fluorescence measurements, typically either ['mCherry'] or
        ['GFP', 'AutoFL'].
    ref_strain: string
        The reference strain used to estimate autofluorescence.
    method: string
        Either "default" or "bayesian".
    options: None or Dict
        If method = "default", the keys of options are:
            figs: boolean
                If True, display plots showing the fits to the reference
                strain's fluorescence.
            use_gps: boolean
                If True, use Gaussian processes to generate extra samples
                from the replicates. Recommended, particularly if there
                are only a few replicates, but slower.
            fl_cv_fn: str, optional
                The covariance function to use for the Gaussian process
                applied to the logarithm of the fluorescence if use_gps=True.
            bd: dict, optional
                Specifies the bounds on the hyperparameters for the
                Gaussian process applied to the logarithm of the
                fluorescence,
                e.g. {2: (-2, 0)}.
            no_samples: int, optional
                The number of samples to take when using Gaussian processes.
            max_data_pts: int, optional
                The maximum number of data points to use for the Gaussian
                process. Too many data points, over 1500, can be slow.
        with two fluorescence measurements, you can also specify
            frac: float, optional
                The fraction of the data used for smoothing via statmodels'
                lowess.
            null_dict: dict[str, list[str]], optional
                A dictionary specifying which Null conditions should be used to correct
                other conditions.
                For example:
                    null_dict= {"2% glu": ["all"]}
                means that all conditions should be corrected using "Null in 2% glu";
                    null_dict= {"2% glu": ["2% glu 0.1 mg/ml", "2% glu 0.2 mg/ml"],
                                "2% gal": ["2% gal 0.1 mg/ml"]}
                means that "2% glu 0.1 mg/ml" and "2% glu 0.2 mg/ml" should be
                corrected with "Null in 2% glu" and that "2% gal 0.1 mg/ml" should
                be corrected with "Null in 2% gal".
    experiments: string or list of strings
        The experiments to include.
    conditions: string or list of strings
        The conditions to include.
    strains: string or list of strings
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

    Examples
    --------
    To correct data with one type of fluorescence measurement, use:

    >>> p.correctauto('GFP', options = {"figs" : False})
    >>> p.correctauto('mCherry', ref_strain= 'BY4741')

    To correct data with two types of fluorescence measurement, use:

    >>> p.correctauto(['GFP', 'AutoFL'], options= {"use_gps" : True})
    >>> p.correctauto(['GFP', 'AutoFL'], ref_strain= 'WT')
    >>> p.correctauto(['GFP', 'AutoFL'], ref_strain= 'WT', method = "bayesian")

    References
    ----------
    S Berthoumieux, H De Jong, G Baptist, C Pinel, C Ranquet, D Ropers,
    J Geiselmann (2013).
    Shared control of gene expression in bacteria by transcription factors
    and global physiology of the cell.
    Mol Syst Biol, 9, 634.

    CA Lichten, R White, IB Clark, PS Swain (2014).
    Unmixing of fluorescence spectra to resolve quantitative time-series
    measurements of gene expression in plate readers.
    BMC Biotech, 14, 1-11.

    I Mihalcescu, MVM Gateau, B Chelli, C Pinel, JL Ravanat (2015).
    Green autofluorescence, a double edged monitoring tool for bacterial
    growth and activity in micro-plates.
    Phys Biol, 12, 066016.
    """
    f = gu.make_list(f)
    exps, cons, strains = sunder.get_all(
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
    )
    # correct for autofluorescence
    if method == "default" and len(f) == 2:
        default_options = {
            "figs": True,
            "use_gps": True,
            "fl_cv_fn": "matern",
            "bd": None,
            "no_samples": 1000,
            "max_data_pts": None,
            "frac": 0.33,
            "null_dict": None,
        }
    elif method == "default" and len(f) == 1:
        default_options = {
            "figs": True,
            "use_gps": True,
            "fl_cv_fn": "matern",
            "bd": None,
            "no_samples": 1000,
            "max_data_pts": None,
        }
    if options is None:
        options = default_options
    else:
        options = default_options | options
    checking_error = correct_auto_checks_l(
        self, f, method, options, exps, cons, strains
    )
    if checking_error:
        print("correctauto: failed checks.")
        return
    else:
        print(
            f"\nCorrecting autofluorescence using {ref_strain} as the"
            " reference."
        )
    if len(f) == 2 and method == "default":
        correct_auto2(
            self,
            f,
            ref_strain,
            experiments,
            experiment_includes,
            experiment_excludes,
            conditions,
            condition_includes,
            condition_excludes,
            strains,
            strain_includes,
            strain_excludes,
            **options,
        )
    elif len(f) == 1 and method == "default":
        correct_auto1(
            self,
            f,
            ref_strain,
            experiments,
            experiment_includes,
            experiment_excludes,
            conditions,
            condition_includes,
            condition_excludes,
            strains,
            strain_includes,
            strain_excludes,
            **options,
        )
    else:
        print(f"f = {f} must be a list of length 1 or 2.")


def correct_auto_checks_l(self, f, method, options, exps, cons, strains):
    """Perform checks on arguents and data before running correctauto."""
    # check for negative fluorescence values and gr is available
    error = False
    for e in exps:
        for c in cons:
            if self.progress["negative_values"][e]:
                for datatype in f:
                    if (
                        datatype in self.progress["negative_values"][e]
                        and c in self.progress["negative_values"][e]
                    ):
                        print(
                            f"{e}: The negative values for {datatype}"
                            f" in {c} will generate NaNs."
                        )
            if "use_gps" in options and options["use_gps"]:
                for s in strains:
                    if f"{s} in {c}" in self.all_strains_conditions[e]:
                        hypers, cvfn = get_hypers(self, e, c, s, dtype="gr")
                        if hypers is None or cvfn is None:
                            print(
                                f"You first must run get_stats for {s} in {c} "
                                f"for {e}."
                            )
                            error = True
    return error


def correct_auto1(
    self,
    f,
    ref_strain,
    experiments,
    experiment_includes,
    experiment_excludes,
    conditions,
    condition_includes,
    condition_excludes,
    strains,
    strain_includes,
    strain_excludes,
    **kwargs,
):
    """
    Correct autofluorescence for measurements with emissions at one wavelength.

    Corrects for autofluorescence for data with emissions measured at one
    wavelength using the fluorescence of the reference strain
    interpolated to the OD of the tagged strain.

    This method in principle corrects too for the fluorescence of the medium,
    although running correctmedia is still recommended.
    """
    print("Using one fluorescence wavelength.")
    print(f"Correcting autofluorescence using {f[0]}.")
    for e in sunder.get_set(
        self,
        experiments,
        experiment_includes,
        experiment_excludes,
        "experiment",
        no_null=True,
    ):
        for c in sunder.get_set(
            self,
            conditions,
            condition_includes,
            condition_excludes,
            "condition",
            no_null=True,
            no_media=True,
        ):
            # process reference strain
            if c in self.all_conditions[e]:
                ref_str_fn = process_ref1(
                    self, f, ref_strain, kwargs["figs"], e, c
                )
            else:
                ref_str_fn = None
            if ref_str_fn is None:
                continue
            # correct strains
            for s in sunder.get_set(
                self,
                strains,
                strain_includes,
                strain_excludes,
                "strain",
                no_null=True,
            ):
                if f"{s} in {c}" in self.all_strains_conditions[e]:
                    t, (od, raw_fl) = sunder.extract_wells(
                        self.r, self.s, e, c, s, ["OD", f[0]]
                    )
                    # no data
                    if od.size == 0 or raw_fl.size == 0:
                        print(f"\n-> No data found for {e}: {s} in {c}.\n")
                        continue
                    # correct autofluorescence for each replicate
                    fl = np.transpose(
                        [
                            raw_fl[:, i] - ref_str_fn(od[:, i])
                            for i in range(od.shape[1])
                        ]
                    )
                    fl[fl < 0] = np.nan
                    if kwargs["use_gps"]:
                        fl_per_od = sample_flperod_with_GPs(
                            self,
                            f[0],
                            t,
                            fl,
                            od,
                            kwargs["fl_cv_fn"],
                            kwargs["bd"],
                            kwargs["no_samples"],
                            e,
                            c,
                            s,
                            kwargs["max_data_pts"],
                            kwargs["figs"],
                        )
                    else:
                        # use only the replicates
                        fl_per_od = np.transpose(
                            [fl[:, i] / od[:, i] for i in range(od.shape[1])]
                        )
                        fl_per_od[fl_per_od < 0] = np.nan
                    # check number of NaN
                    nonans = np.count_nonzero(np.isnan(fl))
                    if np.any(nonans):
                        if nonans == fl.size:
                            print(
                                "\n-> Corrected fluorescence is all NaN "
                                f"for {e}: {s} in {c}.\n"
                            )
                        else:
                            print(
                                f"Warning - {e}: {s} in {c}\n"
                                f"{nonans} corrected data points are"
                                " NaN: the corrected fluorescence"
                                " was negative.",
                            )
                        print("---")
                    # store results
                    autof_dict = {
                        "experiment": e,
                        "condition": c,
                        "strain": s,
                        "time": t,
                        f"c{f[0]}": np.nanmean(fl, 1),
                        f"c{f[0]}_err": nan_std_zeros_to_nan(fl, 1),
                        f"c{f[0]}perOD": np.nanmean(fl_per_od, 1),
                        f"c{f[0]}perOD_err": nan_std_zeros_to_nan(
                            fl_per_od, 1
                        ),
                    }
                    add_to_dataframes(self, autof_dict)


def process_ref1(self, f, ref_strain, figs, experiment, condition):
    """
    Process reference strain for data with one fluorescence measurement.

    Use lowess to smooth the fluorescence of the reference
    strain as a function of OD.

    Parameters
    ----------
    f: string
        The fluorescence to be corrected. For example, ['mCherry'].
    ref_strain: string
        The reference strain. For example, 'WT'.
    figs: boolean
        If True, display fits of the reference strain's fluorescence.
    experiment: string
        The experiment to be corrected.
    condition: string
        The condition to be corrected.

    Returns
    -------
    ref_str_fn: function
        The reference strain's fluorescence as a function of OD.
    """
    e, c = experiment, condition
    print(f"{e}: Processing reference strain {ref_strain} for {f[0]} in {c}.")
    _, (od, fl) = sunder.extract_wells(
        self.r, self.s, e, c, ref_strain, ["OD", f[0]]
    )
    if od.size == 0 or fl.size == 0:
        raise errors.CorrectAuto(f"{e}: {ref_strain} not found in {c}.")
    else:
        od_flat = od.flatten("F")
        fl_flat = fl.flatten("F")
        if ~np.any(fl_flat[~np.isnan(fl_flat)]):
            return None
        # smooth fluorescence as a function of OD using lowess to minimize
        # ref_strain's autofluorescence

        def choose_frac(frac):
            res = lowess(fl_flat, od_flat, frac=frac)
            ref_str_fn = interp1d(
                res[:, 0],
                res[:, 1],
                fill_value=(res[0, 1], res[-1, 1]),
                bounds_error=False,
            )
            # max gives smoother fits than mean
            return np.max(np.abs(fl_flat - ref_str_fn(od_flat)))

        res = minimize_scalar(
            choose_frac, bounds=(0.1, 0.99), method="bounded"
        )
        # choose the optimum frac
        frac = res.x if res.success else 0.33
        res = lowess(fl_flat, od_flat, frac=frac)
        ref_str_fn = interp1d(
            res[:, 0],
            res[:, 1],
            fill_value=(res[0, 1], res[-1, 1]),
            bounds_error=False,
        )
        if figs:
            # plot fit
            plt.figure()
            plt.plot(od_flat, fl_flat, ".", alpha=0.5)
            plt.plot(res[:, 0], res[:, 1])
            plt.xlabel("OD")
            plt.ylabel(f[0])
            plt.title(e + ": " + ref_strain + " for " + c)
            plt.show(block=False)
        return ref_str_fn


def correct_auto2(
    self,
    f,
    ref_strain,
    experiments,
    experiment_includes,
    experiment_excludes,
    conditions,
    condition_includes,
    condition_excludes,
    strains,
    strain_includes,
    strain_excludes,
    **kwargs,
):
    """
    Correct autofluorescence for measurements with two emission wavelengths.

    Corrects for autofluorescence using spectral unmixing for data with
    measured emissions at two wavelengths.

    References
    ----------
    CA Lichten, R White, IB Clark, PS Swain (2014). Unmixing of fluorescence
    spectra to resolve quantitative time-series measurements of gene
    expression in plate readers.
    BMC Biotech, 14, 1-11.
    """
    # correct for autofluorescence
    print("Using two fluorescence wavelengths.")
    print(f"Correcting autofluorescence using {f[0]} and {f[1]}.")
    for e in sunder.get_set(
        self,
        experiments,
        experiment_includes,
        experiment_excludes,
        "experiment",
        no_null=True,
    ):
        for c in sunder.get_set(
            self,
            conditions,
            condition_includes,
            condition_excludes,
            label_type="condition",
            no_null=True,
            no_media=True,
        ):
            # local r data frame for media corrections
            local_rdf = self.r[
                (self.r.experiment == e) & (self.r.condition == c)
            ].copy()
            # correct for background fluorescence using Null strain
            print("Correcting for background fluorescence of media.")
            for fl in f:
                neg_values = find_Null_and_correct(
                    self,
                    local_rdf,
                    fl,
                    e,
                    c,
                    kwargs["figs"],
                    kwargs["frac"],
                    kwargs["null_dict"],
                )
                if neg_values:
                    print("Warning: negative values for\n", neg_values)
            # process reference strain
            ref_qr_fn = process_ref2(
                self, local_rdf, f, ref_strain, kwargs["figs"], e, c
            )
            if ref_qr_fn is None:
                # too many NaNs in reference strain
                continue
            # process other strains
            for s in sunder.get_set(
                self,
                strains,
                strain_includes,
                strain_excludes,
                label_type="strain",
                no_null=True,
            ):
                if (
                    s != ref_strain
                    and f"{s} in {c}" in self.all_strains_conditions[e]
                ):
                    t, (fl_0, fl_1, od) = sunder.extract_wells(
                        local_rdf, self.s, e, c, s, f.copy() + ["OD"]
                    )
                    if fl_0.size == 0 or fl_1.size == 0:
                        print(f"Warning: No data found for {e}: {s} in {c}.")
                        continue
                    # set negative values to NaNs
                    fl_0[fl_0 < 0] = np.nan
                    fl_1[fl_1 < 0] = np.nan
                    # use mean OD for predicting ra from ref_strain
                    od_mean = np.nanmean(od, axis=1)
                    # correct autofluorescence
                    ra = ref_qr_fn(od_mean)
                    fl = apply_auto_fl_correction(self, ra, fl_0, fl_1)
                    fl[fl < 0] = np.nan
                    if kwargs["use_gps"]:
                        # sample to estimate errors
                        fl_per_od = sample_flperod_with_GPs(
                            self,
                            f[0],
                            t,
                            fl,
                            od,
                            kwargs["fl_cv_fn"],
                            kwargs["bd"],
                            kwargs["no_samples"],
                            e,
                            c,
                            s,
                            kwargs["max_data_pts"],
                            kwargs["figs"],
                        )
                    else:
                        # use the replicates
                        fl_per_od = fl / od
                        fl_per_od[fl_per_od < 0] = np.nan
                    # store results
                    autof_dict = {
                        "experiment": e,
                        "condition": c,
                        "strain": s,
                        "time": t,
                        f"c{f[0]}": np.nanmean(fl, 1),
                        f"c{f[0]}_err": nan_iqr_zeros_to_nan(fl, 1),
                        f"c{f[0]}perOD_err": nan_iqr_zeros_to_nan(
                            fl_per_od, 1
                        ),
                        f"c{f[0]}perOD": np.nanmean(fl_per_od, 1),
                    }
                    # add to data frames
                    add_to_dataframes(self, autof_dict)
                    print("---")


def process_ref2(self, local_rdf, f, ref_strain, figs, experiment, condition):
    """
    Process reference strain for spectral unmixing.

    Requires data with two fluorescence measurements.

    Use lowess to smooth the ratio of emitted fluorescence measurements
    so that the reference strain's data is corrected to zero as best
    as possible.

    Parameters
    ----------
    local_rdf: pd.DataFrame
        A copy of the r data frame with fluorescence corrected for media.
    f: list of strings
        The fluorescence measurements. For example, ['GFP', 'AutoFL'].
    ref_strain: string
        The reference strain. For example, 'WT'.
    figs: boolean
        If True, display fits of the fluorescence ratios.
    experiment: string
        The experiment to be corrected.
    condition: string
        The condition to be corrected.

    Returns
    -------
    qr_fn: function
        The ratio of the two fluorescence values for the reference strain
        as a function of OD.
    """
    e, c = experiment, condition
    print(f"{e}: Processing reference strain {ref_strain} for {f[0]} in {c}.")
    # ref_strain data
    t, (f0, f1, od) = sunder.extract_wells(
        local_rdf, self.s, e, c, ref_strain, f.copy() + ["OD"]
    )
    if f0.size == 0 or f1.size == 0 or od.size == 0:
        raise errors.CorrectAuto(f"{e}: {ref_strain} not found in {c}.")
    else:
        f0[f0 < 0] = np.nan
        f1[f1 < 0] = np.nan
        od_flat = od.flatten("F")
        od_ref_mean = np.mean(od, 1)
        qr_flat = (f1 / f0).flatten("F")
        if np.all(np.isnan(qr_flat)):
            print(f"{e}: {ref_strain} in {c} has too many NaNs.")
            return
        # smooth to minimise autofluorescence in ref_strain

        def choose_frac(frac):
            qr_fn, _ = find_qr_fn(qr_flat, od_flat, frac)
            fl_ref = apply_auto_fl_correction(self, qr_fn(od_ref_mean), f0, f1)
            return np.max(np.abs(fl_ref))

        res = minimize_scalar(
            choose_frac, bounds=(0.1, 0.99), method="bounded"
        )
        # calculate the relationship between qr and OD
        frac = res.x if res.success else 0.95
        # apply lowess and find qr_fn
        qr_fn, res = find_qr_fn(qr_flat, od_flat, frac)
        if figs:
            plt.figure()
            plt.plot(od_flat, qr_flat, ".", alpha=0.5)
            plt.plot(res[:, 0], res[:, 1])
            plt.xlabel("OD")
            plt.ylabel(f[1] + "/" + f[0])
            plt.title(e + ": " + ref_strain + " in " + c)
            plt.show(block=False)
        # check autofluorescence correction for reference strain
        fl_ref = apply_auto_fl_correction(self, qr_fn(od_ref_mean), f0, f1)
        fl_ref_per_od = fl_ref / od
        # set negative values to NaNs
        fl_ref[fl_ref < 0] = np.nan
        fl_ref_per_od[fl_ref_per_od < 0] = np.nan
        # store results
        autof_dict = {
            "experiment": e,
            "condition": c,
            "strain": ref_strain,
            "time": t,
            f"c{f[0]}": np.nanmean(fl_ref, 1),
            f"c{f[0]}perOD": np.nanmean(fl_ref_per_od, 1),
            f"c{f[0]}_err": nan_std_zeros_to_nan(fl_ref, 1),
            f"c{f[0]}perOD_err": nan_std_zeros_to_nan(fl_ref_per_od, 1),
        }
        add_to_dataframes(self, autof_dict)
        return qr_fn


def find_qr_fn(qr_flat, od_flat, frac):
    """Use lowess and then interpolation to find qr_fn."""
    res = lowess(qr_flat, od_flat, frac)
    qr_fn = interp1d(
        res[:, 0],
        res[:, 1],
        fill_value=(res[0, 1], res[-1, 1]),
        bounds_error=False,
    )
    return qr_fn, res


def apply_auto_fl_correction(self, ra, f0data, f1data):
    """Correct for autofluorescence returning an array of replicates."""
    nr = f0data.shape[1]
    raa = np.reshape(np.tile(ra, nr), (np.size(ra), nr), order="F")
    return (raa * f0data - f1data) / (
        raa - self._gamma * np.ones(np.shape(raa))
    )


def add_to_dataframes(self, datadict):
    """Added dict of data to s data frame."""
    newdf = pd.DataFrame(datadict)
    key_cols = ["experiment", "condition", "strain", "time"]
    self.s = gu.merge_df_into(self.s, newdf, key_cols)


def nan_std_zeros_to_nan(a, axis=None):
    """Like nanstd but setting zeros to nan."""
    err = np.nanstd(a, axis)
    err[err == 0] = np.nan
    return err


def nan_iqr_zeros_to_nan(a, axis=None):
    """Interquartile range but setting zeros to nan."""
    iqr = np.nanquantile(a, 0.75, axis) - np.nanquantile(a, 0.25, axis)
    iqr[iqr == 0] = np.nan
    return iqr


def get_hypers(self, exp, con, s, dtype="gr"):
    """Find parameters for GP from sc data frame."""
    sdf = self.sc[
        (self.sc.experiment == exp)
        & (self.sc.condition == con)
        & (self.sc.strain == s)
    ]
    if sdf.empty:
        return None, None
    else:
        try:
            cvfn = sdf[f"gp_for_{dtype}"].values[0]
            hypers = [
                sdf[col].values[0]
                for col in sorted(sdf.columns)
                if ("hyper" in col and dtype in col)
            ]
            if np.any(np.isnan(hypers)):
                return None, None
            else:
                return hypers, cvfn
        except KeyError:
            return None, None


def instantiate_GP(hypers, cvfn, x, y, max_data_pts):
    """Instantiate a Gaussian process."""
    xa, ya, _, _ = preprocess_data(x, y, merrors=[], max_data_pts=max_data_pts)
    # bounds are irrelevant because parameters are optimal
    go = getattr(gp, cvfn + "GP")(
        {0: (-5, 5), 1: (-4, 4), 2: (-5, 2)}, xa, ya, warnings=False
    )
    go.lth_opt = hypers
    go.success = True
    # make predictions so that samples can be generated
    go.predict(x, derivs=2)
    return go


def sample_ODs_with_GP(
    self, experiment, condition, strain, t, od, no_samples, max_data_pts
):
    """Instantiate Gaussian process for log OD and sample."""
    hypers, cvfn = get_hypers(self, experiment, condition, strain, dtype="gr")
    if hypers is None or cvfn is None:
        raise SystemExit(
            f"You first must run get_stats for {strain} in {condition} "
            f"for {experiment} unless use_gps=False."
        )
    od[od < 0] = np.nan
    # initialise GP for log ODs
    go = instantiate_GP(hypers, cvfn, t, np.log(od), max_data_pts)
    # sample
    lod_samples = go.sample(no_samples)
    return lod_samples


def sample_flperod_with_GPs(
    self,
    fl_name,
    t,
    fl,
    od,
    fl_cv_fn,
    bd,
    no_samples,
    e,
    c,
    s,
    max_data_pts=None,
    figs=True,
    logs=True,
    negs_to_nan=True,
):
    """
    Generate samples of fluorescence per OD.

    Smooth and sample fluorescence using a Gaussian process.
    Sample ODs using the Gaussian process generated by get_stats.
    """
    if np.any(fl[~np.isnan(fl)]):
        # run GP for fluorescence or log fluorescence
        # omfitderiv deals with NaNs
        if logs:
            fitvar = f"log_{fl_name}"
        else:
            fitvar = fl_name
        f_fitderiv = run_fit_deriv(
            t,
            fl,
            fitvar,
            f"d/dt_{fitvar}",
            experiment=e,
            condition=c,
            strain=s,
            bd=bd,
            cvfn=fl_cv_fn,
            logs=logs,
            negs_to_nan=negs_to_nan,
            max_data_pts=max_data_pts,
            plot_local_max=False,
        )
        if not f_fitderiv.success:
            print(f"-> Fitting fluorescence failed for {e}: {s} in {c}.")
            return np.nan * np.ones((t.size, no_samples))
        # samples
        lod_samples = sample_ODs_with_GP(
            self, e, c, s, t, od, no_samples, max_data_pts
        )
        f_samples = f_fitderiv.fit_deriv_sample(no_samples)[0]
        if logs:
            fl_per_od_samples = np.exp(f_samples - lod_samples)
        else:
            fl_per_od_samples = f_samples * np.exp(-lod_samples)
    else:
        print("No positive data.")
        # all NaN
        fl_per_od_samples = np.nan * np.ones((t.size, no_samples))
    return fl_per_od_samples

"""Function to estimate promoter activity as a time derivative."""

import numpy as np

import omniplate.corrections as omcorr
import omniplate.sunder as sunder
from omniplate.omfitderiv import run_fit_deriv


def get_promoter_activity(
    self,
    f="GFP",
    figs=True,
    fl_cvfn="matern",
    bd=None,
    no_samples=1000,
    max_data_pts=None,
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
    Estimate the promoter activity from the corrected fluorescence.

    A Gaussian process is run on the corrected fluorescence, and
    the results from get_stats are used.

    Arguments
    --
    f: string
        The fluorescence measurement, typically either 'GFP or 'mCherry'.
    figs: boolean
        If True, display plots showing the fits to the corrected fluorescence.
    fl_cvfn: str, optional
        The covariance function to use for the Gaussian process applied
        to the logarithm of the corrected fluorescence.
    bd: dict, optional
        Specifies the bounds on the hyperparameters for the Gaussian
        process applied to the logarithm of the corrected fluorescence,
        e.g. {2: (-2, 0)}.
    no_samples: int, optional
        The number of samples to take when using Gaussian processes.
    max_data_pts: int, optional
        The maximum number of data points to use for the Gaussian process.
        Too many data points, over 1500, can be slow.
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
    """
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
            for s in sunder.get_set(
                self,
                strains,
                strain_includes,
                strain_excludes,
                label_type="strain",
                no_null=True,
            ):
                if f"{s} in {c}" in self.all_strains_conditions[e]:
                    choose = (
                        (self.s.experiment == e)
                        & (self.s.condition == c)
                        & (self.s.strain == s)
                    )
                    if f"c{f}" in self.s.columns:
                        cfl = self.s[choose][f"c{f}"].values
                        cfls = np.array(
                            [
                                cfl,
                                cfl + self.s[choose][f"c{f}_err"].values,
                                cfl - self.s[choose][f"c{f}_err"].values,
                            ]
                        ).T
                        t = self.s[choose].time.values
                        if cfl.size == 0:
                            print(
                                f"Warning: No corrected {f} found for"
                                f" {e}: {s} in {c}."
                            )
                            continue
                        fitvar = f"log_c{f}"
                        derivname = f"d/dt_{fitvar}"
                        f_fitderiv = run_fit_deriv(
                            t=t,
                            d=cfls,
                            fitvar=fitvar,
                            derivname=derivname,
                            experiment=e,
                            condition=c,
                            strain=s,
                            bd=bd,
                            cvfn=fl_cvfn,
                            logs=True,
                            max_data_pts=max_data_pts,
                        )
                        if not f_fitderiv.success:
                            print(
                                "\n-> Fitting corrected fluorescence failed"
                                f" for {e}: {s} in {c}.\n"
                            )
                            continue
                        if figs:
                            f_fitderiv.plot_fit(
                                e, c, s, fitvar, derivname, logs=True
                            )
                        # samples
                        t_od, od = sunder.extract_wells(
                            self.r, self.s, e, c, s, ["OD"]
                        )
                        lod_samples = omcorr.sample_ODs_with_GP(
                            self, e, c, s, t_od, od, no_samples
                        )
                        lfl_samples, lfl_deriv_samples = (
                            f_fitderiv.fit_deriv_sample(no_samples)[:2]
                        )
                        # promoter activity samples
                        pa_samples = lfl_deriv_samples * np.exp(
                            lfl_samples - lod_samples
                        )
                        # store results
                        resdict = {
                            "experiment": e,
                            "condition": c,
                            "strain": s,
                            "time": t,
                            f"promoter_activity_{f}_err": omcorr.nan_iqr_zeros_to_nan(
                                pa_samples, 1
                            ),
                            f"promoter_activity_{f}": np.nanmean(
                                pa_samples, 1
                            ),
                        }
                        # add to data frames
                        omcorr.add_to_dataframes(
                            self, resdict, "promoter_activity_{f}"
                        )
                else:
                    print(
                        "No corrected fluorescence found for "
                        f"{e}: {s} in {c}."
                    )

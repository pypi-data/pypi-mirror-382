"""Functions to display the contents of wells."""

import omniplate.admin as admin
import omniplate.clogger as clogger
import omniplate.omerrors as errors
import omniplate.omgenutils as gu
import omniplate.sunder as sunder


def contents_of_wells(self, wlist):
    """
    Display contents of wells.

    Parameters
    ----------
    wlist: string or list of string
        Specifies the well or wells of interest.

    Examples
    --------
    >>> p.contents_of_wells(['A1', 'E4'])
    """
    wlist = gu.make_list(wlist)
    for w in wlist:
        print("\n" + w + "\n--")
        print(
            self.wellsdf.query("well == @w")
            .drop(["well"], axis=1)
            .to_string(index=False)
        )


def show_wells(
    self,
    concise=False,
    sort_by=True,
    experiments="all",
    conditions="all",
    strains="all",
    experiment_includes=False,
    experiment_excludes=False,
    condition_includes=False,
    condition_excludes=False,
    strain_includes=False,
    strain_excludes=False,
):
    """
    Display wells for specified experiments, conditions, and strains.

    Parameters
    ----------
    concise: boolean
        If True, display as experiment: condition: strain.
    sort_by: boolean or list of strings, optional
        If True, a default sort will be used.
        If list of column names, sort on these names.
        If False, no sorting will occur.
    experiments: string or list of strings
        The experiments to include.
    conditions: string or list of strings
        The conditions to include.
    strains: string or list of strings
        The strains to include.
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
    strain_includes: string, optional
        Selects only strains that include the specified string in their
        name.
    strain_excludes: string, optional
        Ignores strains that include the specified string in their name.

    Examples
    --------
    >>> p.show_wells()
    >>> p.show_wells(strains= 'Mal12:GFP', conditions= '1% Mal')
    """
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
        no_null=False,
    )
    if not hasattr(self, "wellsdf"):
        self.wellsdf = admin.make_wells_df(self.r)
    df = self.wellsdf.query(
        "experiment == @exps and condition == @cons and strain == @strs"
    ).copy()
    print()
    if concise:
        sdf = df[["experiment", "condition", "strain"]]
        ndf = (
            sdf.groupby(sdf.columns.tolist())
            .size()
            .reset_index(name="replicates")
        )
        df = ndf
    if isinstance(sort_by, list) or isinstance(sort_by, str):
        df = df.sort_values(by=gu.make_list(sort_by))
    elif sort_by:
        # default sort
        df[["new1", "new2"]] = df.condition.str.split("%", expand=True)[[0, 1]]
        # sort by nutrient then by its concentration then by strain
        if df.new1.str.isnumeric().any():
            df = df.sort_values(by=["new2", "new1", "strain"])
        else:
            df = df.sort_values(by=["new1", "new2", "strain"])
        df.drop(columns=["new1", "new2"], inplace=True)
    for e in exps:
        print(df.query("experiment == @e").to_string(index=False))
        print()


@clogger.log
def ignore_wells(self, ignore=None):
    """
    Ignore the wells specified in any future processing.

    If called several times, the default behaviour is for any previously
    ignored wells not to be re-instated.

    Parameters
    ---------
    ignore: list of strings or dict
        If there is only a single experiment, ignore is a list of labels
        of wells to be ignored.
        If there are multiple experiments, ignore is a dict with experiment
        names as keys and a list of wells as items.

    Example
    -------
    >>> p.ignore_wells(['A1', 'C2'])
    >>> p.ignore_wells({"exp1" : ["A1"], "exp2": ["C3", "C4"]})
    """
    if ignore is None:
        return
    else:
        if len(self.all_experiments) == 1 and not isinstance(ignore, dict):
            # make exclude a dict
            if isinstance(ignore, str):
                ignore = {self.all_experiments[0]: gu.make_list(ignore)}
            elif isinstance(ignore, list):
                ignore = {self.all_experiments[0]: ignore}
            else:
                raise errors.IgnoreWells(f"{ignore} is in the wrong format.")
        if isinstance(ignore, dict):
            # make each value a list
            ignore = {
                key: [value] if isinstance(value, str) else value
                for key, value in ignore.items()
            }
            if self.all_experiments == self.combined:
                ignore = convert_wells_for_combined(self, ignore)
            # drop wells
            for exp, wells in ignore.items():
                # wells cannot be ignored twice
                wex = list(
                    set(wells) - set(self.progress["ignored_wells"][exp])
                )
                # drop data from ignored wells
                df = self.r
                filt = (df["experiment"] == exp) & df["well"].isin(wex)
                df = df.loc[~filt]
                df = df.reset_index(drop=True)
                self.r = df
                # store ignored_wells
                self.progress["ignored_wells"][exp] += wex
                # remove any duplicates
                self.progress["ignored_wells"][exp] = list(
                    set(self.progress["ignored_wells"][exp])
                )
            # remake s data frame
            admin.update_s(self)
        else:
            raise errors.IgnoreWells(f"{ignore} is in the wrong format.")


def convert_wells_for_combined(self, ignore: dict):
    """Convert ignore into a dict with one key for a combined experiment."""
    if self.all_experiments != self.combined:
        return ignore
    else:
        emap = self.experiment_map
        cignore = {
            self.combined: [
                f"{emap[key]}_{well}" for key in ignore for well in ignore[key]
            ]
        }
        return cignore

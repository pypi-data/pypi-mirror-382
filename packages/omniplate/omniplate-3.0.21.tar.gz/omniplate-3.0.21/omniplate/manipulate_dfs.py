"""Functions to manipulate the dataframes."""

import re

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

import omniplate.admin as admin
import omniplate.clogger as clogger
import omniplate.omerrors as errors
import omniplate.sunder as sunder


@clogger.log
def rename_combined(self, new_name):
    """Rename a combined experiment."""
    if self.all_experiments == [self.combined]:
        for df in [self.r, self.s, self.sc]:
            df["experiment"] = df.experiment.replace({self.combined: new_name})
        self.all_experiments = [new_name]
        self.combined = new_name


@clogger.log
def rename_replicates(self, replicate_suffices=("_A", "_B")):
    """Rename replicate strains to have the same strain name."""
    for e in self.all_experiments:
        strain_dict = {
            strain: strain[:-2]
            for strain in self.all_strains[e]
            if strain.endswith(replicate_suffices)
        }
    self.rename(strain_dict)


def search(self, list_of_strings):
    """
    Search self.all_strains_conditions.

    Example
    -------
    >>> p.search(["HXT6", "Glu"])
    """
    if isinstance(list_of_strings, str):
        list_of_strings = [list_of_strings]
    for e in self.all_strains_conditions:
        for sc in self.all_strains_conditions[e]:
            hits = [q for q in list_of_strings if q in sc]
            if len(hits) == len(list_of_strings):
                print(f"{e}: {sc}")


@clogger.log
def rename(self, translate_dict, regex=True, **kwargs):
    """
    Rename strains or conditions.

    Uses a dictionary to replace all occurrences of a strain or a condition
    with an alternative.

    Note that instances of self.progress will not be updated.

    Parameters
    ----------
    translatedict: dictionary
        A dictionary of old name - new name pairs
    regex: boolean (optional)
        Value of regex to pass to panda's replace.
    kwargs: keyword arguments
        Passed to panda's replace.

    Example
    -------
    >>> p.rename({'77.WT' : 'WT', '409.Hxt4' : 'Hxt4'})
    """
    # check for duplicates
    if (
        len(translate_dict.values())
        != np.unique(list(translate_dict.values())).size
    ):
        print("Warning: new names are not unique.")
        # replace in dataframes
        for df in [self.r, self.sc]:
            exps = df.experiment.copy()
            df.replace(translate_dict, inplace=True, regex=regex, **kwargs)
            # do not change names of experiments
            df["experiment"] = exps
        # remake s so that strains with the same name are combined
        self.s = admin.make_s(self)
        # remake sc
        self.sc = self.sc.drop_duplicates().reset_index(drop=True)
    else:
        # replace in dataframes
        for df in [self.r, self.s, self.sc]:
            exps = df.experiment.copy()
            df.replace(translate_dict, inplace=True, regex=regex, **kwargs)
            df["experiment"] = exps
    self.wellsdf = admin.make_wells_df(self.r)
    # replace in attributes - all_strains and all_conditions
    for e in self.all_experiments:
        for list_attr in [self.all_conditions[e], self.all_strains[e]]:
            for i, list_item in enumerate(list_attr):
                for key in translate_dict:
                    if key in list_item:
                        list_attr[i] = list_item.replace(
                            key, translate_dict[key]
                        )
        # unique values in case two strains have been renamed to one
        self.all_conditions[e] = sorted(
            np.unique(self.all_conditions[e]).tolist()
        )
        self.all_strains[e] = sorted(np.unique(self.all_strains[e]).tolist())
        self.all_strains_conditions[e] = list(
            (self.r.strain + " in " + self.r.condition).dropna().unique()
        )


@clogger.log
def add_column(self, new_column_name, old_column, new_column_values):
    """
    Add a new column to all dataframes by parsing an existing column.

    All possible entries for the new column are specified as strings and
    the entry in the new column will be whichever of these strings is
    present in the entry of the existing column.

    Parameters
    ----------
    new_column_name: string
        The name of the new column.
    old_column: string
        The name of the column to be parsed to create the new column.
    new_column_values: list of strings
        All of the possible values for the entries in the new column.

    Example
    -------
    >>> p.add_column('medium', 'condition', ['Raffinose',
    ...                                     'Geneticin'])

    will parse each entry in 'condition' to create a new column called
    'medium' that has either a value 'Raffinose' if 'Raffinose' is in the
    entry from 'condition' or a value 'Geneticin' if 'Geneticin' is in the
    entry from 'condition'.
    """
    for dftype in ["r", "s", "sc"]:
        df = getattr(self, dftype)
        old_col = df[old_column].to_numpy()
        new_col = np.array(("none",) * old_col.size, dtype="object")
        for i, old_col_value in enumerate(old_col):
            for new_col_value in new_column_values:
                if new_col_value in old_col_value:
                    new_col[i] = new_col_value
        new_col_series = pd.Series(
            new_col, index=df.index, name=new_column_name
        )
        setattr(self, dftype, pd.concat([df, new_col_series], axis=1))


@clogger.log
def add_numeric_column(
    self,
    new_column_name,
    old_column,
    pick_number=0,
    left_split_str=None,
    right_split_str=None,
    as_str=False,
):
    """
    Add a new numeric column.

    Parse the numbers from the entries of an existing column.

    Run only after the basic analyses - ignorewells, correct_OD, and
    correctmedia - have been performed because addnumericolumn changes
    the structure of the dataframes.

    Parameters
    ----------
    new_column_name: string
        The name of the new column.
    old_column: string
        The name of column to be parsed.
    pick_number: integer
        The number to pick from the list of numbers extracted from the
        existing column's entry.
    left_split_str: string, optional
        Split the entry of the column using whitespace and parse numbers
        from the substring to the immediate left of left_split_str rather
        than the whole entry.
    right_split_str: string, optional
        Split the entry of the column using whitespace and parse numbers
        from the substring to the immediate right of right_split_str rather
        than the whole entry.
    as_str: boolean
        If True, convert the numeric value to a string to improve plots
        with seaborn.

    Examples
    --------
    To extract concentrations from conditions use

    >>> p.add_numeric_column('concentration', 'condition')

    For a condition like '0.5% Raf 0.05ug/mL Cycloheximide', use

    >>> p.add_numeric_column('raffinose', 'condition',
    ...                     pick_number=0)
    >>> p.add_numeric_column('cycloheximide', 'condition',
    ...                     pick_number=1)
    """
    # process split_strs
    if left_split_str or right_split_str:
        split_str = left_split_str if left_split_str else right_split_str
        loc_no = -1 if left_split_str else 1
    else:
        split_str = False
    # change each dataframe
    for dftype in ["r", "s", "sc"]:
        df = getattr(self, dftype)
        if as_str:
            # new column of strings
            new_col = np.full_like(
                df[old_column].to_numpy(), "", dtype="object"
            )
        else:
            # new column of floats
            new_col = np.full_like(
                df[old_column].to_numpy(), np.nan, dtype="float"
            )
        # parse old column
        for i, old_col_value in enumerate(df[old_column].to_numpy()):
            if old_col_value:
                # split string first on spaces and then find substring
                # adjacent to specified split_string
                if split_str:
                    if split_str in old_col_value:
                        # old_col_value contains left_split_string or
                        # right_split_string
                        bits = old_col_value.split()
                        for k, bit in enumerate(bits):
                            if split_str in bit:
                                loc = k + loc_no
                                break
                        # adjacent string
                        old_col_value = bits[loc]
                    else:
                        # old_col_value does not contain left_split_string
                        # or right_split_string
                        old_col_value = ""
                # loop through all floats in old_col_value
                no_count = 0
                for ci in re.split(
                    r"[+-]?([0-9]+(?:[.][0-9]*)?|[.][0-9]+)", old_col_value
                ):
                    try:
                        no = float(ci)
                        if no_count == pick_number:
                            new_col[i] = ci if as_str else no
                            break
                        no_count += 1
                    except ValueError:
                        pass
        new_col_series = pd.Series(
            new_col, index=df.index, name=new_column_name
        )
        setattr(self, dftype, pd.concat([df, new_col_series], axis=1))


@clogger.log
def add_to_sc(
    self,
    new_column=None,
    s_column=None,
    func=None,
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
    Apply func to a column in the s dataframe.

    The results are stored in the sc dataframe.

    Parameters
    ----------
    new_column:  string
        The name of the new column in the sc dataframe
    s_column:   string
        The name of the column in s dataframe from which the
        data is to be processed
    func:   function
        The function to be applied to the data in the s dataframe.

    Examples
    --------
    >>> p.add_to_sc(new_column="max_GFP", s_column="mean_GFP",
    ...             func=np.nanmax)
    >>> p.add_to_sc(new_column="lower_quartile_GFP", s_column="mean_GFP",
    ...             func=lambda x: np.nanquantile(x, 0.25))
    """
    # extract data
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
    )
    self.sc[new_column] = np.nan
    for e in exps:
        for c in cons:
            for s in strs:
                d = self.s.query(
                    "experiment == @e and condition == @c and strain == @s"
                )[s_column].values
                res = np.asarray(func(d))
                if res.size == 1:
                    self.sc.loc[
                        (self.sc.experiment == e)
                        & (self.sc.condition == c)
                        & (self.sc.strain == s),
                        new_column,
                    ] = func(d)
                else:
                    print("func must return a single value.")
                    return False


@clogger.log
def add_common_variable(
    self,
    var="time",
    d_var=None,
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
):
    """
    Add a common variable to all time-dependent dataframes.

    The common variable allows averaging across experiments
    and typically is time.

    A common variable is added to time-dependent dataframes. This
    variable's values only come from a fixed array so that they are
    from the same array for all experiments.

    For example, the plate reader often does not perfectly increment time
    between measurements and different experiments can have slightly
    different time points despite the plate reader having the same
    settings. These unique times prevent seaborn from taking averages.

    If experiments have measurements that start at the same time point and
    have the same interval between measurements, then setting a common time
    for all experiments will allow seaborn to perform averaging.

    The array of the common variable has an interval d_var, which is
    automatically calculated, but may be specified.

    Each instance of var is assigned a common value - the closest instance
    of the common variable to the instance of var. Measurements are assumed
    to the same for the true instance of var and for the assigned common
    value, which may generate errors if these two are sufficiently
    distinct.

    An alternative method is average_over_expts.

    Parameters
    ----------
    var: string
        The variable from which the common variable is generated,
        typically 'time'.
    d_var: float, optional
        The interval between the values comprising the common array.
    figs: boolean
        If True, generate plot to check if the variable and the common
        variable generated from it are sufficiently close in value.
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

    Example
    -------
    To plot averages of time-dependent variables over experiments, use for
    example

    >>> p.add_common_variable('time')
    >>> p.plot(x= 'common_time', y= 'cGFPperOD', hue= 'condition')
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
    for i, df in enumerate([self.r, self.s]):
        if var in df:
            loc = (
                df.experiment.isin(exps)
                & df.condition.isin(cons)
                & df.strain.isin(strs)
            )
            if d_var is None and df.equals(self.r):
                # group data by experiment generating average time
                mean_df = (
                    df[loc]
                    .sort_values(by=["experiment", "well", var])[
                        ["experiment", "well", var, "OD"]
                    ]
                    .groupby(["experiment", var])
                    .mean(numeric_only=True)
                ).reset_index()[["experiment", var]]
                # find experiment with longest duration
                longest_i = np.argmax(
                    [mean_df[mean_df.experiment == e][var].size for e in exps]
                )
                # chose the var for this longest experiment
                common_var = mean_df[mean_df.experiment == exps[longest_i]][
                    var
                ].values
            elif d_var is not None:
                common_var = np.arange(
                    df[loc][var].min(), df[loc][var].max(), d_var
                )
            # define common var
            df.loc[loc, f"common_{var}"] = df[loc][var].apply(
                lambda x: common_var[np.argmin((x - common_var) ** 2)]
            )
            if figs and i == 0:
                plt.figure()
                sl = np.linspace(
                    df[loc][var].min(), 1.05 * df[loc][var].max(), 100
                )
                plt.plot(sl, sl, alpha=0.4)
                plt.plot(
                    df[loc][var].to_numpy(),
                    df[loc][f"common_{var}"].to_numpy(),
                    ".",
                )
                plt.xlabel(var)
                plt.ylabel(f"common_{var}")
                title = "r dataframe" if df.equals(self.r) else "s dataframe"
                plt.title(title)
                plt.suptitle(
                    f"comparing {var} with common_{var} – "
                    "the line y= x is expected."
                )
                plt.tight_layout()
                plt.show(block=False)


@clogger.log
def restrict_time(self, tmin=None, tmax=None):
    """
    Restrict the processed data to a range of time.

    Points outside this time range are ignored.

    Note that data in the dataframes outside the time range is lost.
    Exporting the dataframes before running restrict_time is recommended.

    Parameters
    ----------
    tmin: float
        The minimum value of time, with data kept only for t >= tmin.
    tmax: float
        The maximum value of time, with data kept only for t <= tmax.

    Example
    -------
    >>> p.restrict_time(tmin= 5)
    """
    if tmin is None:
        tmin = self.r.time.min()
    if tmax is None:
        tmax = self.r.time.max()
    if tmax > tmin:
        self.r = self.r[(self.r.time >= tmin) & (self.r.time <= tmax)]
        self.s = self.s[(self.s.time >= tmin) & (self.s.time <= tmax)]
    else:
        print("tmax or tmin is not properly defined.")


@clogger.log
def get_dataframe(
    self,
    df_name="s",
    experiments="all",
    conditions="all",
    strains="all",
    experiment_includes=False,
    experiment_excludes=False,
    condition_includes=False,
    condition_excludes=False,
    strain_includes=False,
    strain_excludes=False,
    no_null=True,
):
    """
    Obtain a subset of the data in a dataframe.

    This data can be used plotted directly.

    Parameters
    ---------
    df_name: string
        The dataframe of interest either 'r' (raw data),
        's' (default; processed data),
        or 'sc' (summary statistics).
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
    no_null: boolean, optional
        If True, ignore 'Null' strains

    Returns
    -------
    new_df: dataframe

    Example
    -------
    >>> new_df = p.get_dataframe('s', conditions=['2% Glu'],
    ...                          no_null=True)
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
        no_null,
    )
    if hasattr(self, df_name):
        df = getattr(self, df_name)
        new_df = df.query(
            "experiment == @exps and condition == @cons " "and strain == @strs"
        )
        if new_df.empty:
            print("No data found.")
        else:
            return new_df.copy()
    else:
        raise errors.UnknownDataFrame(
            "Dataframe " + df_name + " is not recognised."
        )

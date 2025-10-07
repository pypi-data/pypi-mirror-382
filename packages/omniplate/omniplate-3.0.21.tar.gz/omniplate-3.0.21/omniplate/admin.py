"""Functions for general administration, mostly of data frames."""

import numpy as np
import pandas as pd

import omniplate.omgenutils as gu


def initialise_progress(self, experiment):
    """Initialise progress dictionary."""
    self.progress["ignored_wells"][experiment] = []
    self.progress["negative_values"][experiment] = False


def make_wells_df(df_r):
    """Make a dataframe with the contents of the wells."""
    df = df_r[["experiment", "condition", "strain", "well"]].drop_duplicates()
    df = df.reset_index(drop=True)
    return df


def drop(self, experiments, conditions, strains):
    """
    Drop strains from s and sc data frames.

    Variables
    ---------
    experiments: string or list of strings
        The experiments to include.
    conditions: string or list of strings
        The conditions to include.
    strains: string or list of strings
        The strains to include.
    """
    experiments = gu.make_list(experiments)
    conditions = gu.make_list(conditions)
    strains = gu.make_list(strains)
    for attr in ["s", "sc"]:
        df = getattr(self, attr)
        indices_to_drop = [
            df[
                (df.experiment == e) & (df.condition == c) & (df.strain == s)
            ].index
            for e, c, s in zip(experiments, conditions, strains)
        ]
        if indices_to_drop and any(len(idx) > 0 for idx in indices_to_drop):
            getattr(self, attr).drop(
                pd.Index(np.concatenate(indices_to_drop)), inplace=True
            )


def make_s(self, tmin=None, tmax=None, rdf=None):
    """
    Generate s dataframe.

    Calculates means and variances of all data types from raw data.

    Drop "original_experiment" and "experiment_id" because there should
    be one mean_OD for all experiment_ids.
    """
    if rdf is None:
        # restrict time
        if tmin and not tmax:
            rdf = self.r[self.r.time >= tmin]
        elif tmax and not tmin:
            rdf = self.r[self.r.time <= tmax]
        elif tmin and tmax:
            rdf = self.r[(self.r.time >= tmin) & (self.r.time <= tmax)]
        else:
            rdf = self.r
    # find indices to use for s dataframe
    df_indices = self.r.select_dtypes(include=["object"]).columns.tolist()
    for column in ["well", "original_experiment", "experiment_id"]:
        if column in df_indices:
            df_indices.remove(column)
    # classify columns
    groupby_columns = df_indices + ["time"]
    numeric_columns = self.r.select_dtypes(include="number").columns.tolist()
    good_columns = groupby_columns + ["well"] + numeric_columns
    # for common variables
    good_columns += [field for field in rdf.columns if "common" in field]
    # find and drop remaining columns
    bad_columns = [col for col in rdf.columns if col not in good_columns]
    if bad_columns:
        rdf = rdf.drop(columns=bad_columns)
    # find means
    df1 = rdf.groupby(groupby_columns).mean(numeric_only=True).reset_index()
    for exp in self.all_experiments:
        for dtype in self.data_types[exp]:
            df1 = df1.rename(columns={dtype: "mean_" + dtype})
    # find std
    df2 = rdf.groupby(groupby_columns).std(numeric_only=True).reset_index()
    for exp in self.all_experiments:
        for dtype in self.data_types[exp]:
            df2 = df2.rename(columns={dtype: dtype + "_err"})
    return pd.merge(df1, df2)


def update_s(self):
    """Update means and errors of all data_types from raw data."""
    # find tmin and tmax in case restrict_time has been called
    tmin = self.s.time.min()
    tmax = self.s.time.max()
    # recalculate s dataframe
    self.s = make_s(self, tmin, tmax)


def add_to_s(self, deriv_name, out_df):
    """
    Add dataframe of time series to s dataframe.

    Parameters
    ----------
    deriv_name: str
        Root name for statistic described by dataframe, such as "gr".
    out_df: dataframe
        Data to add.
    """
    self.s = gu.merge_df_into(
        self.s, out_df, ["experiment", "condition", "strain", "time"]
    )


def add_dict_to_sc(self, stats_dict):
    """Add one-line dict to sc dataframe."""
    stats_df = pd.DataFrame(stats_dict, index=pd.RangeIndex(0, 1, 1))
    self.sc = gu.merge_df_into(
        self.sc, stats_df, ["experiment", "condition", "strain"]
    )


def check_kwargs(kwargs):
    """Stop if final s missing from experiments, conditions, or strains."""
    if "condition" in kwargs:
        raise SystemExit("Use conditions not condition as an argument.")
    elif "strain" in kwargs:
        raise SystemExit("Use strains not strain as an argument.")
    elif "experiment" in kwargs:
        raise SystemExit("Use experiments not experiment as an argument.")


@property
def cols_to_underscore(self):
    """Replace spaces in column names of all dataframes with underscores."""
    for df in [self.r, self.s, self.sc]:
        df.columns = df.columns.str.replace(" ", "_")

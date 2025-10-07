"""Functions to import and export."""

from pathlib import Path

import numpy as np
import pandas as pd

import omniplate.admin as admin
import omniplate.clogger as clogger
import omniplate.omgenutils as gu
from omniplate.load_data import sort_attributes


def save_log(self, fname=None):
    """
    Save log to file.

    Parameters
    --
    fname: string, optional
        The name of the file. If unspecified, the name of the experiment.

    Example
    -------
    >>> p.save_log()
    """
    # export log
    if fname:
        fnamepath = self.datadir_path / (fname + ".log")
    else:
        fnamepath = self.wdir_path / ("".join(self.all_experiments) + ".log")
    with fnamepath.open("w") as f:
        f.write(self.log_stream.getvalue())
    print(f"Exported {fnamepath.name}.")


@clogger.log
def export_df(self, fname=False, type="tsv", l_direc=False):
    """
    Export the dataframes.

    The exported data may either be tab-delimited or csv or json files.
    Dataframes for the (processed) raw data, for summary data, and for
    summary statistics and corrections, as well as a log file, are
    exported.

    Parameters
    ----------
    fname: string, optional
        The name used for the output files.
        If unspecified, the experiment or experiments is used.
    type: string
        The type of file for export, either 'json' or 'csv' or 'tsv'.
    l_direc: string, optional
        The directory to write. If False, the working directory is used.

    Examples
    --------
    >>> p.export_df()
    >>> p.export_df('processed', type= 'json')
    """
    if not fname:
        fname = "".join(self.all_experiments)
    if l_direc:
        l_direc = Path(l_direc)
        fullfname = str(l_direc / fname)
    else:
        fullfname = str(self.wdir_path / fname)
    # export data
    if type == "json":
        self.r.to_json(fullfname + "_r.json", orient="split")
        self.s.to_json(fullfname + "_s.json", orient="split")
        self.sc.to_json(fullfname + "_sc.json", orient="split")
    else:
        sep = "\t" if type == "tsv" else ","
        self.r.to_csv(fullfname + "_r." + type, sep=sep, index=False)
        self.s.to_csv(fullfname + "_s." + type, sep=sep, index=False)
        self.sc.to_csv(fullfname + "_sc." + type, sep=sep, index=False)
    print(f"Exported {Path(fullfname).stem}.")
    # export log to file
    self.save_log(fname)


def load_json_csv_tsv(rootname):
    """Load exported file and convert into dataframe."""
    experiment_name = Path(rootname).name
    try:
        # json files
        impdf = pd.read_json(f"{rootname}.json", orient="split")
        print(f"Imported {experiment_name}.json")
    except FileNotFoundError:
        try:
            # csv files
            impdf = pd.read_csv(f"{rootname}.csv", sep=",")
            print(f"Imported {experiment_name}.csv")
        except FileNotFoundError:
            try:
                # tsv files
                impdf = pd.read_csv(f"{rootname}.tsv", sep="\t")
                print(f"Imported {experiment_name}.tsv")
            except FileNotFoundError:
                print(
                    f"No file called {rootname}.json " "or .csv or .tsv found."
                )
                return
    # ensure all are imported as strings
    for var in ["experiment", "condition", "strain"]:
        impdf[var] = impdf[var].astype(str)
    return impdf


@clogger.log
def import_df(self, common_names, info=True, sep="\t"):
    """
    Import dataframes saved as either json or csv or tsv files.

    Parameters
    ----------
    common_names: list of strings
        A list of names for the files to be imported with one string for
        each experiment.

    Examples
    --------
    >>> p.import_df('Gal')
    >>> p.import_df(['Gal', 'Glu', 'Raf'])
    """
    common_names = gu.make_list(common_names)
    for commonname in common_names:
        commonname = str(self.datadir_path / commonname)
        for df in ["r", "s", "sc"]:
            impdf = load_json_csv_tsv(f"{commonname}_{df}")
            # merge dataframes
            if hasattr(self, df):
                setattr(
                    self, df, pd.merge(getattr(self, df), impdf, how="outer")
                )
            else:
                setattr(self, df, impdf)
        print()
    # update attributes
    self.all_experiments = list(self.s.experiment.unique())
    self.all_conditions.update(
        {
            e: list(self.s[self.s.experiment == e].condition.unique())
            for e in self.all_experiments
        }
    )
    self.all_strains.update(
        {
            e: list(self.s[self.s.experiment == e].strain.unique())
            for e in self.all_experiments
        }
    )
    for e in self.all_experiments:
        rdf = self.r[self.r.experiment == e]
        res = list((rdf.strain + " in " + rdf.condition).dropna().unique())
        res = [r for r in res if r != "nan in nan"]
        self.all_strains_conditions.update({e: res})
    # find data_types with mean in self.s
    dtypdict = {}
    for e in self.all_experiments:
        # drop columns of NaNs - these are created by merge if a datatype
        # is in one experiment but not in another
        tdf = self.s[self.s.experiment == e].dropna(axis=1, how="all")
        dtypdict[e] = list(tdf.columns[tdf.columns.str.contains("mean")])
    self.data_types.update(
        {e: [dt.split("mean_")[1] for dt in dtypdict[e]] for e in dtypdict}
    )
    # to reduce fragmentation
    self.r = self.r.copy()
    self.s = self.s.copy()
    self.sc = self.sc.copy()
    # initialise progress
    for e in self.all_experiments:
        admin.initialise_progress(self, e)
    # display info on import
    if info:
        self.info
    # display warning if duplicates created
    if len(self.all_experiments) != np.unique(self.all_experiments).size:
        print(
            "\nLikely ERROR: data with the same experiment, condition, "
            "strain, and time now appears twice!!"
        )
    sort_attributes(self)


def save(self, name=None):
    """Remind user that save is undefined."""
    print("You probably mean export_df.")

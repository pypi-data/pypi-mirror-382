"""Define the platereader class."""

import warnings
from pathlib import Path

import omniplate
import omniplate.clogger as clogger


class PlateReader:
    """
    To analyse plate-reader data.

    Data are corrected for autofluorescence and growth rates found using
    a Gaussian process.

    All data is stored used Panda's dataframes and plotted using Seaborn.

    Three dataframes are created. If p is an instance of the platereader class,
    then p.r contains the raw data for each well in the plate; p.s contains the
    processed time-series using the data from all relevant wells; and p.sc
    contains any summary statistics, such as 'max gr'.

    For time series sampled from a Gaussian process, the mean is used as the
    statistics and errors are estimated by the standard deviation.
    For statistics calculated from time series, the median is used and errors
    are estimated by half the interquartile range, with the distribution of
    the statistic calculated by sampling time series.

    Examples
    -------
    A typical work flow is:

    >>> from omniplate import PlateReader

    then either

    >>> p= PlateReader('GALdata.xlsx', 'GALcontents.xlsx',
    ...                    wdir= 'data/')

    or

    >>> p= PlateReader()
    >>> p.load('GALdata.xls', 'GALcontents.xlsx')

    and to analyse OD data

    >>> p.plot('OD', plate= True)
    >>> p.correct_OD()
    >>> p.correct_media()
    >>> p.plot(y= 'OD')
    >>> p.plot(y= 'OD', hue= 'strain',
    ...        condition_includes= ['Gal', 'Glu'],
    ...        strain_excludes= 'HXT7')
    >>> p.get_stats('OD')

    and for fluorescence data

    >>> p.correct_auto(['GFP', 'AutoFL'])
    >>> p.plot(y= 'cGFPperOD', hue= 'condition')

    and to save the results

    >>> p.save_figs()
    >>> p.export_df()

    General properties of the data and of previous processing are shown with:

    >>> p.info
    >>> p.attributes()
    >>> p.corrections()
    >>> p.log

    See also
        http://swainlab.bio.ed.ac.uk/software/omniplate/index.html
    for a tutorial, which can be opened directly using

    >>> p.webhelp()
    """

    # ratio of fluorescence emission at 585nm to emiisions at 525nm for eGFP
    _gamma = 0.114  # TODO delete

    def __init__(
        self,
        d_names=None,
        a_names=None,
        experiment_type=None,
        wdir=".",
        datadir=".",
        plate_reader_type="Tecan",
        d_sheets=False,
        a_sheets=False,
        od_fname=None,
        info=True,
        ls=True,
    ):
        """
        Initiate and potentially immediately load data for processing.

        Parameters
        ----------
        d_names: string or list of strings, optional
            The name of the file containing the data from the plate reader or
            a list of file names.
        a_names: string or list of strings, optional
            The name of file containing the corresponding annotation or a list
            of file names.
        experiment_type: string or list of strings, optional
            If specified, creates a new experiment_type column in each
            dataframe.
        wdir: string, optional
            The working directory where new files should be saved.
        datadir: string, optional
             The directory containing the data files.
        plate_reader_type: string
            The type of plate reader, currently either "Tecan" or "tidy" for
            data parsed into a tsv file of columns, with headings "time",
            "well", "OD", "GFP", and any other measurements taken.
        d_sheets: list of integers or strings, optional
            The relevant sheets of the Excel files storing the data.
        a_sheets: list of integers or strings, optional
            The relevant sheets of the corresponding Excel files for the
            annotation.
        info: boolean
            If True (default), display summary information on the data once
            loaded.
        ls: boolean
            If True (default), display contents of working directory.
        """
        # absolute path
        self.wdir_path = Path(wdir)
        self.datadir_path = Path(datadir)
        # enable logging
        self.logger, self.log_stream = clogger.init_log(omniplate.__version__)
        if True:
            # warning generated occasionally when sampling from the Gaussian
            # process likely because of numerical errors
            warnings.simplefilter("ignore", RuntimeWarning)
        # dictionary recording extent of analysis
        self.progress = {
            "ignored_wells": {},
            "negative_values": {},
        }
        self.all_experiments = []
        self.all_conditions = {}
        self.all_strains = {}
        self.data_types = {}
        self.all_strains_conditions = {}
        self.find_available_data
        if d_names is None:
            # list all files in current directory
            if ls:
                self.ls
        else:
            # immediately load data
            self.load(
                d_names=d_names,
                a_names=a_names,
                experiment_type=experiment_type,
                plate_reader_type=plate_reader_type,
                d_sheets=d_sheets,
                a_sheets=a_sheets,
                info=info,
            )
        self.combined = "__combined__"

    ###
    # import methods
    ###
    from .admin import cols_to_underscore, drop
    from .omcheck import check
    from .corrections import (
        correct_auto,
        correct_auto_l,
        correct_OD_for_media,
        correct_OD,
    )
    from .get_stats import get_stats
    from .load_data import load
    from .manipulate_dfs import (
        add_to_sc,
        add_column,
        add_common_variable,
        add_numeric_column,
        get_dataframe,
        rename,
        rename_combined,
        rename_replicates,
        restrict_time,
        search,
    )
    from .midlog import get_midlog
    from .misc import average_over_expts, get_fitness_penalty
    from .ominfo import (
        change_wdir,
        change_datadir,
        find_available_data,
        info,
        log,
        ls,
        help,
        experiment_map,
    )
    from .omio import export_df, import_df, save_log, save
    from .omplot import close, plot, save_figs, inspect
    from .omwells import contents_of_wells, ignore_wells, show_wells
    from .promoter_activity import get_promoter_activity

    def __repr__(self):
        """Give standard representation."""
        repstr = f"omniplate.{self.__class__.__name__}: "
        if self.all_experiments:
            for e in self.all_experiments:
                repstr += e + " ; "
            if repstr[-2:] == "; ":
                repstr = repstr[:-3]
        else:
            repstr += "no experiments"
        return repstr


if __name__ == "__main__":
    print(PlateReader.__doc__)

"""Miscellaneous general purpose functions."""

import numpy as np


def merge_df_into(df, newdf, key_cols):
    """
    Add newdf to df using key_cols and updating where necessary.

    New values always overwrite old values, even if NaN.
    """
    # create a copy of the original dataframe
    result = df.copy()
    # update existing rows and add new ones with combine_first
    # first, set the index to key_cols
    result.set_index(key_cols, inplace=True)
    newdf_indexed = newdf.set_index(key_cols)
    # update with combine_first (opposite direction from update())
    updated = newdf_indexed.combine_first(result)
    # add any missing columns from original df
    for col in result.columns:
        if col not in updated.columns:
            updated[col] = result[col]
    # reset index and return
    return updated.reset_index()


@property
def cols_to_underscore(self):
    """Replace spaces in column names of all dataframes with underscores."""
    for df in [self.r, self.s, self.sc]:
        df.columns = df.columns.str.replace(" ", "_")


def rm_under(str):
    """Replace underscore in a string with a space."""
    return str.replace("_", " ")


def merge_dicts(original, update):
    """
    Merge two dicts into one.

    Parameters
    --
    original: first dict
    update: second dict
    """
    if update is not None:
        z = original | update
        return z
    else:
        return original


def find_smooth_variance(y, filt_sig=0.1, no_pts=False):
    """
    Estimate and then smooth the variance over replicates of data.

    Parameters
    --
    y: data - one column for each replicate
    filt_sig: sets the size of the Gaussian filter used to smooth the variance
    no_pts: if set, uses estimateerrorbar to estimate the variance
    """
    from scipy.ndimage import filters

    if y.ndim == 1:
        # one dimensional data
        v = estimate_error_bar(y, no_pts) ** 2
    else:
        # multi-dimensional data
        v = np.var(y, 1)
    # apply Gaussian filter
    vs = filters.gaussian_filter1d(v, int(len(y) * filt_sig))
    return vs


def estimate_error_bar(y, no_pts=False):
    """
    Estimate measurement error for each data point.

    The errors found by calculating the standard deviation of the nopts
    data points closest to that data point.

    Parameters
    --
    y: data - one column for each replicate
    no_pts: number of points used to estimate error bars
    """
    y = np.asarray(y)
    if y.ndim == 1:
        ebar = np.empty(len(y))
        if not no_pts:
            no_pts = np.round(0.1 * len(y))
        for i in range(len(y)):
            ebar[i] = np.std(np.sort(np.abs(y[i] - y))[:no_pts])
        return ebar
    else:
        print("estimate_error_bar: works for 1-d arrays only.")


def natural_keys(text):
    """
    Find a set of keys.

    These keys can be used to sort a list of strings by the numeric
    values in the list entries.

    Eg sorted(list, key= natural_keys)

    Parameters
    ---------
    text: a string (but see above example)
    """
    import re

    def atof(text):
        try:
            retval = float(text)
        except ValueError:
            retval = text
        return retval

    return [
        atof(c)
        for c in re.split(r"[+-]?([0-9]+(?:[.][0-9]*)?|[.][0-9]+)", text)
    ]


def is_list_empty(ell):
    """
    Check if a list of lists is empty, e.g. [[]].

    Parameters
    --
    ell: list
    """
    if isinstance(ell, list):  # Is a list
        return all(map(is_list_empty, ell))
    return False  # Not a list


def make_list(c):
    """
    Ensure that a variable is a list.

    Parameters
    --
    c: variable to be made into a list
    """
    import numpy as np

    if isinstance(c, np.ndarray):
        return list(c)
    elif type(c) is not list:
        return [c]
    else:
        return c


def figs_to_pdf(savename):
    """Save all open figures to a pdf file."""
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_pdf import PdfPages

    if "." not in savename:
        savename += ".pdf"
    with PdfPages(savename) as pp:
        for i in plt.get_fignums():
            plt.figure(i)
            pp.savefig()

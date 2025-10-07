"""Functions to plot from the data frames."""

import colorcet
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

import omniplate.admin as admin
import omniplate.clogger as clogger
import omniplate.omerrors as errors
import omniplate.omgenutils as gu
import omniplate.sunder as sunder


@clogger.log
def plot(
    self,
    x="time",
    y="OD",
    hue="strain",
    style="condition",
    size=None,
    kind="line",
    col=None,
    row=None,
    height=5,
    aspect=1,
    xlim=None,
    ylim=None,
    figsize=False,
    return_facet_grid=False,
    title=None,
    plate=False,
    wells=False,
    no_null=False,
    messages=False,
    sort_by=False,
    distinct_colours=False,
    tmin=None,
    tmax=None,
    prettify_dict=None,
    experiments="all",
    conditions="all",
    strains="all",
    experiment_includes=False,
    experiment_excludes=False,
    condition_includes=False,
    condition_excludes=False,
    strain_includes=False,
    strain_excludes=False,
    **kwargs,
):
    """
    Plot from the underlying dataframes (chosen automatically).

    Seaborn's relplot is used, which is described at
    https://seaborn.pydata.org/generated/seaborn.relplot.html

    Parameters
    ----------
    x: string
        The variable - column of the dataframe - for the x-axis.
    y: string
        The variable - column of the dataframe - for y-axis.
    hue: string
        The variable whose variation will determine the colours of the
        lines plotted. From Seaborn.
    style: string
        The variable whose variation will determine the style of each line.
        From Seaborn.
    size: string
        The variable whose vairation will determine the size of each
        marker. From Seaborn.
    kind: string
        Either 'line' or 'scatter', which determines the type of plot.
        From Seaborn.
    col: string, optional
        The variable that varies over the columns in a multipanel plot.
        From Seaborn.
    row: string, optional
        The variable that varies over the rows in a multipanel plot.
        From Seaborn.
    height: float, optional
        The height of the individual panels in a multipanel plot.
        From Seaborn.
    aspect: float, optional
        The aspect ratio of the individual panels in a multipanel plot.
        From Seaborn.
    xlim: list of two floats, optional
        The minimal and maximal x-value, such as [0, None]
    ylim: list of two floats, optional
        The minimal and maximal y-value, such as [0, None]
    figsize: tuple, optional
        A tuple of (width, height) for the size of figure.
        Ignored if wells= True or plate= True.
    return_facet_grid: boolean, optional
        If True, return Seaborn's facetgrid object created by relplot
    title: float, optional
        The title of the plot (overwrites any default titles).
    plate: boolean, optional
        If True, data for each well for a whole plate are plotted in one
        figure.
    wells: boolean, optional
        If True, data for the individual wells is shown.
    no_null: boolean, optional
        If True, 'Null' strains are not plotted.
    sort_by: list of strings, optional
        A list of columns to sort the data in the dataframe and passed to
        pandas sort_values.
    messsages: boolean, optional
        If True, print warnings for any data requested but not found.
    distinct_colours: boolean, optional
        If True, try to make neighbouring colours in the plot distinct
        rather than graded.
    tmin: float, optional
        If specifed, restrict the data to times greater than tmin.
    tmax: float, optional
        If specifed, restrict the data to times less than tmax.
    prettify_dict: dict, optional
        To replace the x- and y-axis labels:
            e.g., {"time": "time (h)", "OD": "optical density"}
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
    kwargs: for Seaborn's relplot
        https://seaborn.pydata.org/generated/seaborn.relplot.html

    Returns
    -------
    sfig: Seaborn's facetgrid object generated by relplot if
    return_facet_grid= True

    Examples
    --------
    >>> p.plot(y= 'OD', plate= True)
    >>> p.plot(y= 'OD', wells= True, strainincludes= 'Gal10:GFP')
    >>> p.plot(y= 'OD')
    >>> p.plot(x= 'OD', y= 'gr')
    >>> p.plot(y= 'cGFPperOD', no_null= True, ymin= 0)
    >>> p.plot(y= 'cGFPperOD', conditionincludes= '2% Mal',
    ...        hue= 'strain')
    >>> p.plot(y= 'cmCherryperOD', conditions= ['0.5% Mal',
    ...        '1% Mal'], hue= 'strain', style= 'condition',
    ...         no_null= True, strainincludes= 'mCherry')
    >>> p.plot(y= 'cGFPperOD', col= 'experiment')
    >>> p.plot(y= 'max gr')
    """
    admin.check_kwargs(kwargs)
    # choose the correct dataframe
    basedf, dfname = plot_find_df(self, x, y, tmin, tmax)
    # get experiments, conditions and strains
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
    # check if default prettify_dict
    if prettify_dict is None and hasattr(self, "prettify_dict"):
        prettify_dict = getattr(self, "prettify_dict")
    # choose the right type of plot
    if plate:
        dtype = y if x == "time" else x
        plot_plate(self, basedf, exps, dtype)
    elif wells:
        plot_wells(
            x,
            y,
            basedf,
            exps,
            cons,
            strs,
            style=style,
            size=size,
            kind=kind,
            col=col,
            row=row,
            xlim=xlim,
            ylim=ylim,
            title=title,
            figsize=figsize,
            messages=messages,
            distinct_colours=distinct_colours,
            prettify_dict=prettify_dict,
            **kwargs,
        )
    elif dfname == "s" or dfname == "r":
        sfig = plot_rs(
            x,
            y,
            basedf,
            exps,
            cons,
            strs,
            hue=hue,
            style=style,
            size=size,
            kind=kind,
            col=col,
            row=row,
            height=height,
            aspect=aspect,
            xlim=xlim,
            ylim=ylim,
            title=title,
            figsize=figsize,
            sort_by=sort_by,
            return_facet_grid=return_facet_grid,
            distinct_colours=distinct_colours,
            prettify_dict=prettify_dict,
            **kwargs,
        )
        if return_facet_grid:
            return sfig
    elif dfname == "sc":
        plot_sc(
            x,
            y,
            basedf,
            exps,
            cons,
            strs,
            hue=hue,
            style=style,
            size=size,
            kind=kind,
            col=col,
            row=row,
            height=height,
            aspect=aspect,
            xlim=xlim,
            ylim=ylim,
            figsize=figsize,
            title=title,
            sort_by=sort_by,
            distinct_colours=distinct_colours,
            prettify_dict=prettify_dict,
            **kwargs,
        )
    else:
        raise errors.PlotError("omplot: No data found")


def plot_plate(self, basedf, exps, dtype):
    """
    Plot the data for each well following the layout of a 96-well plate.

    Parameters
    ----------
    self: platereader object
    basedf: DataFrame
        The r dataframe.
    exps: float
        The name of the experiments.
    dtype: float
        The data type to be plotted: 'OD', 'GFP', etc.
    """
    if exps == self.combined:
        exps = list(self.r.original_experiment.unique())
        experiment_column = "original_experiment"
    else:
        experiment_column = "experiment"
    for e in exps:
        plt.figure()
        # first create an empty plate - in case of missing wells
        ax = []
        for rowl in range(8):
            for coll in np.arange(1, 13):
                sindex = coll + 12 * rowl
                axi = plt.subplot(8, 12, sindex)
                ax.append(axi)
                plt.tick_params(labelbottom=False, labelleft=False)
                # label well locations
                for j in range(12):
                    if sindex == j + 1:
                        plt.title(j + 1)
                for j, k in enumerate(np.arange(1, 96, 12)):
                    if sindex == k:
                        plt.ylabel("ABCDEFGH"[j] + " ", rotation=0)
        # fill in the wells that have been measured
        for pl in basedf.query(f"{experiment_column} == @e")["well"].unique():
            if experiment_column == "experiment":
                well_loc = pl
            else:
                well_loc = pl.split("_")[1]
            rowl = "ABCDEFGH".index(well_loc[0])
            coll = int(well_loc[1:])
            sindex = coll + 12 * rowl
            wd = basedf.query(f"{experiment_column} == @e and well == @pl")
            ax[sindex - 1].plot(
                wd["time"].to_numpy(), wd[dtype].to_numpy(), "-"
            )
        plt.suptitle(e + ": " + dtype)
        plt.show(block=False)


def plot_wells_facet_grid(
    basedf,
    x,
    y,
    row,
    col,
    e,
    cons,
    strs,
    prettify_dict,
    title,
    xlim,
    ylim,
    figsize,
):
    """Use facetgrid to show multiple plots simultaneously."""
    df = basedf.query(
        "experiment == @e and condition == @cons and strain == @strs"
    )
    if row is not None and col is not None:
        groups = [row, col]
    elif row is not None:
        groups = [row]
    elif col is not None:
        groups = [col]
    sfig = sns.FacetGrid(df, row=row, col=col)
    for var, facet_df in df.groupby(groups):
        if row is not None and col is not None:
            row_var, col_var = var
            ax = sfig.axes[
                sfig.row_names.index(row_var),
                sfig.col_names.index(col_var),
            ]
        elif row is not None:
            ax = sfig.axes[sfig.row_names.index(var[0])][0]
        elif col is not None:
            ax = sfig.axes[sfig.col_names.index(var[0])][0]
        sns.lineplot(x=x, y=y, hue="well", data=facet_df, ax=ax)
        ax.set(xlabel="", ylabel="")
    sfig.set_titles()
    if title is None:
        title = e
    set_labels_limits(sfig, x, y, title, xlim, ylim, prettify_dict)
    if figsize and len(figsize) == 2:
        sfig.fig.set_figwidth(figsize[0])
        sfig.fig.set_figheight(figsize[1])
    plt.tight_layout()
    plt.show(block=False)


def plot_wells_multiple(
    basedf,
    x,
    y,
    kind,
    style,
    size,
    e,
    cons,
    strs,
    prettify_dict,
    xlim,
    ylim,
    distinct_colours,
    messages,
    kwargs,
):
    """Create plots for each strain and condition."""
    for c in cons:
        for s in strs:
            df = basedf.query(
                "experiment == @e and condition == @c and strain == @s"
            )
            if df.empty:
                if messages:
                    print(e + ":", "No data found for", s, "in", c)
            else:
                if distinct_colours:
                    palette = sns.color_palette(
                        colorcet.glasbey, df.well.unique().size
                    )
                else:
                    palette = None
                sfig = sns.relplot(
                    x=x,
                    y=y,
                    data=df,
                    hue="well",
                    kind=kind,
                    style=style,
                    size=size,
                    palette=palette,
                    **kwargs,
                )
                title = e + ": " + s + " in " + c
                set_labels_limits(sfig, x, y, title, xlim, ylim, prettify_dict)
                plt.show(block=False)


def plot_wells(
    x,
    y,
    basedf,
    exps,
    cons,
    strs,
    style="condition",
    size=None,
    kind="line",
    col=None,
    row=None,
    xlim=None,
    ylim=None,
    title=None,
    figsize=None,
    messages=False,
    distinct_colours=False,
    prettify_dict=None,
    **kwargs,
):
    """
    Plot data from the individual wells.

    Data for each experiment, condition, and strain are plotted in
    a separate figure unless row and col are specified.
    """
    for e in exps:
        if row or col:
            plot_wells_facet_grid(
                basedf=basedf,
                x=x,
                y=y,
                row=row,
                col=col,
                e=e,
                cons=cons,
                strs=strs,
                prettify_dict=prettify_dict,
                title=title,
                xlim=xlim,
                ylim=ylim,
                figsize=figsize,
            )
        else:
            plot_wells_multiple(
                basedf=basedf,
                x=x,
                y=y,
                kind=kind,
                style=style,
                size=size,
                e=e,
                cons=cons,
                strs=strs,
                prettify_dict=prettify_dict,
                xlim=xlim,
                ylim=ylim,
                distinct_colours=distinct_colours,
                messages=messages,
                kwargs=kwargs,
            )


def print_plot_warnings(hue, style, size, col, x, df):
    """Print warnings if user's choices seem off."""
    if hue == style:
        print(
            f'Warning: "hue" and "style" have both been set to {hue}"'
            '" and there may be unintended averaging.'
        )
    if (
        x != "commontime"
        and len(df["experiment"].unique()) > 1
        and hue != "experiment"
        and size != "experiment"
        and style != "experiment"
        and col != "experiment"
    ):
        print(
            "Warning: there are multiple experiments, but neither "
            '"hue", "style", nor "size" is set to "experiment" and there'
            " may be averaging over experiments."
        )


def plot_rs(
    x,
    y,
    basedf,
    exps,
    cons,
    strs,
    hue="strain",
    style="condition",
    size=None,
    kind="line",
    col=None,
    row=None,
    height=5,
    aspect=1,
    xlim=None,
    ylim=None,
    title=None,
    figsize=None,
    sort_by=False,
    return_facet_grid=False,
    distinct_colours=False,
    prettify_dict=None,
    **kwargs,
):
    """Plot time-series data from the .r or .s dataframes."""
    # plot time series
    df = basedf.query(
        "experiment == @exps and condition == @cons and strain == @strs"
    )
    if df.empty or df.isnull().all().all():
        # no data or data all NaN
        print("omplot: No data found.")
    else:
        if sort_by:
            df = df.sort_values(by=gu.make_list(sort_by))
        # warn if poor choice of seaborn's parameters
        print_plot_warnings(hue, style, size, col, x, df)
        if kind == "line" and "units" not in kwargs:
            # augment df to allow seaborn to estimate errors
            df = augment_df(df, y)
            kwargs["errorbar"] = "sd"
        else:
            errors.PlotError(f"omplot: kind={kind} is not recognised.")
        # plot
        if distinct_colours:
            palette = sns.color_palette(
                colorcet.glasbey, df[hue].unique().size
            )
            kwargs["palette"] = palette
        # remove conditions and strains that are all nan
        cdf = (
            df.groupby(["experiment", "condition", "strain"])[y]
            .apply(np.nanmean)
            .reset_index()
        )
        keep_conditions = list(cdf.dropna().condition.values)
        keep_strains = list(cdf.dropna().strain.values)
        # use seaborn to plot
        tdf = df[
            df.condition.isin(keep_conditions) & df.strain.isin(keep_strains)
        ]
        if not tdf.empty:
            sfig = sns.relplot(
                x=x,
                y=y,
                data=tdf,
                hue=hue,
                kind=kind,
                style=style,
                size=size,
                col=col,
                row=row,
                aspect=aspect,
                height=height,
                **kwargs,
            )
            set_labels_limits(sfig, x, y, title, xlim, ylim, prettify_dict)
            if figsize and len(figsize) == 2:
                sfig.fig.set_figwidth(figsize[0])
                sfig.fig.set_figheight(figsize[1])
            plt.show(block=False)
            if return_facet_grid:
                return sfig
            else:
                return None
        else:
            print("omplot: No data found.")


def plot_sc(
    x,
    y,
    basedf,
    exps,
    cons,
    strs,
    hue="strain",
    style="condition",
    size=None,
    kind="scatter",
    col=None,
    row=None,
    height=5,
    aspect=1,
    xlim=None,
    ylim=None,
    figsize=None,
    title=None,
    sort_by=False,
    distinct_colours=False,
    prettify_dict=None,
    **kwargs,
):
    """Plot summary statistics from the .sc dataframe."""
    # plot summary stats
    df = basedf.query(
        "experiment == @exps and condition == @cons and strain == @strs"
    )
    xcols = df.columns[df.columns.str.startswith(x)]
    ycols = df.columns[df.columns.str.startswith(y)]
    cols_to_keep = (
        ["experiment", "condition", "strain"] + list(xcols) + list(ycols)
    )
    sort_by = gu.make_list(sort_by) if sort_by else []
    for field in [hue, style, size, *sort_by, col, row]:
        if isinstance(field, str):
            cols_to_keep += [field]
    df = df[np.unique(cols_to_keep)].dropna()
    if df.empty or df.isnull().all().all():
        # no data or data all NaN:
        print("omplot: No data found.")
    else:
        if sort_by:
            df = df.sort_values(by=gu.make_list(sort_by))
        if distinct_colours:
            kwargs["palette"] = sns.color_palette(
                colorcet.glasbey, df[hue].unique().size
            )
        sfig = sns.relplot(
            x=x,
            y=y,
            data=df,
            hue=hue,
            style=style,
            size=size,
            col=col,
            row=row,
            aspect=aspect,
            height=height,
            **kwargs,
        )
        set_labels_limits(sfig, x, y, title, xlim, ylim, prettify_dict)
        if row is None and col is None:
            # add error bars
            # find coordinates of points in relplot
            xc, yc = [], []
            for point_pair in sfig.ax.collections:
                for xp, yp in point_pair.get_offsets():
                    xc.append(xp)
                    yc.append(yp)
            # add error bars
            xerr = df[x + "_err"] if x + "_err" in df.columns else None
            yerr = df[y + "_err"] if y + "_err" in df.columns else None
            sfig.ax.errorbar(
                xc,
                yc,
                xerr=xerr,
                yerr=yerr,
                fmt=" ",
                ecolor="dimgray",
                alpha=0.5,
            )
        plt.show(block=False)


def plot_find_df(self, x, y, tmin, tmax):
    """
    Find the correct dataframe for plotting y versus x.

    Parameters
    ----------
    self: a platereader instance
    x: string
        Name of x-variable.
    y: string
        Name of y-variable.
    tmin: float
        If specifed, restrict the data to times greater than tmin.
    tmax: float
        If specifed, restrict the data to times less than tmax.

    Returns
    -------
    basedf: dataframe
        The dataframe that contains the x and y variables.
    dfname: string
        The name of the dataframe.
    """
    # choose the correct dataframe
    if hasattr(self, "r") and x in self.r.columns and y in self.r.columns:
        # raw data (with wells)
        basedf = self.r
        dfname = "r"
    elif x in self.s.columns and y in self.s.columns:
        # processed data (no wells)
        basedf = self.s
        dfname = "s"
    elif x in self.sc.columns and y in self.sc.columns:
        # summary stats
        basedf = self.sc
        dfname = "sc"
    else:
        raise errors.PlotError(
            f"The variables x= {x}"
            + f" and y= {y}"
            + " cannot be plotted against each other because they are not in "
            + " the same dataframe"
        )
    if (tmin or tmax) and "time" in basedf.columns:
        if tmin is not None and tmax is None:
            basedf = basedf[basedf.time >= tmin]
        elif tmin is None and tmax is not None:
            basedf = basedf[basedf.time <= tmax]
        elif tmin is not None and tmax is not None:
            basedf = basedf[(basedf.time >= tmin) & (basedf.time <= tmax)]
    return basedf, dfname


def augment_df(df, datatype):
    """
    Augment dataframe to allow Seaborn to generate errors.

    Use 'err' (if present in the dataframe) to allow Seaborn to generate
    errors in relplot, otherwise returns original dataframe.

    Note we call seaborn with errorbar = "sd" and so use sqrt(3/2) * error
    because seaborn calculates the standard deviation from the augmented data
    (the mean, the mean + std, and the mean - std) and so gets
    std/sqrt(3/2) otherwise because there are three data points.
    """
    if datatype + "_err" in df:
        derr = datatype + "_err"
    elif "mean" in datatype and datatype.split("mean_")[1] + "_err" in df:
        derr = datatype.split("mean_")[1] + "_err"
    else:
        derr = None
        # return if df is df_r
        return df
    if derr:
        df.insert(0, "augtype", "mean")
        # add errors
        mn = df[datatype].to_numpy()
        err = df[derr].to_numpy()
        # add std
        dfp = df.copy()
        dfp[datatype] = mn + np.sqrt(3 / 2) * err
        dfp["augtype"] = "+err"
        # minus std
        dfm = df.copy()
        dfm[datatype] = mn - np.sqrt(3 / 2) * err
        dfm["augtype"] = "-err"
        # concat
        df = pd.concat([df, dfp, dfm], ignore_index=True)
    return df


def save_figs(self, fname=None, one_file=True):
    """
    Save all current figures to PDF.

    Either all figures save to one file or each to a separate one.

    Parameters
    ----------
    fname: string, optional
        Name of file. If unspecified, the name of the experiment is used.
    one_file: boolean, optional
        If False, each figures is save to its own PDF file.

    Example
    -------
    >>> p.save_figs()
    >>> p.save_figs('figures.pdf')
    """
    if fname:
        if ".pdf" not in fname:
            fname += ".pdf"
        fname = str(self.wdir_path / fname)
    else:
        fname = str(self.wdir_path / ("".join(self.all_experiments) + ".pdf"))
    if one_file:
        gu.figs_to_pdf(fname)
    else:
        for i in plt.get_fignums():
            plt.figure(i)
            savename = str(plt.getp(plt.gcf(), "axes")[0].title).split("'")[1]
            savename = savename.replace(" ", "_")
            if savename == "":
                savename = "Whole_plate_Figure_" + str(i)
            print("Saving", savename)
            plt.savefig(str(self.wdir_path / (savename + ".pdf")))


@property
def close(self):
    """
    Close all figures.

    Example
    -------
    >>> p.close
    """
    plt.close("all")


def set_labels_limits(sfig, x, y, title, xlim, ylim, prettify_dict):
    """Set axes labels and limits and set title."""
    if prettify_dict is not None:
        sfig.set_axis_labels(prettify_dict.get(x, x), prettify_dict.get(y, y))
    else:
        sfig.set_axis_labels(x, y)
    if xlim is not None:
        plt.xlim(xlim)
    if ylim is not None:
        plt.ylim(ylim)
    if title:
        sfig.fig.suptitle(title)


def inspect(
    self,
    xlabel="time",
    ylabel="bcGFPperOD",
    refstrain="WT",
    fl="GFP",
    max_xy=None,
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
    Plot growth and fluorescence data in one plot per strain per condition.

    Parameters
    ----------
    xlabel: string
        Variable to plot on the x-axis.
    ylabel: string
        Variable to plot on the y-axis.
    refstrain: string
        The reference strain used to correct autofluorescence.
    fl: string
        The name of the fluorescence channel.
    max_xy: (float, float)
        A maximum to show on the plot of xlabel versus ylabel.
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
    flperod = f"flperOD_raw_{fl}"
    for exp in exps:
        for con in cons:
            for strain in strs:
                sdf, x, y, midlog_times, n_plots, ref_df = set_up_inspect(
                    self, exp, con, strain, xlabel, ylabel, flperod, refstrain
                )
                if x.size == 0 or y.size == 0:
                    print(
                        f"{strain} in {con}: No data found for"
                        f" {xlabel} and {ylabel}."
                    )
                    continue
                # begin plot
                curr_plot = 1
                plt.figure(figsize=(5, 7))
                # plot OD
                ax1 = plt.subplot(n_plots, 1, curr_plot)
                plt.plot(x, sdf["mean_OD"].values, "m")
                plt.plot(
                    ref_df["time"].values,
                    ref_df["mean_OD"].values,
                    "k--",
                    alpha=0.5,
                    label=refstrain,
                )
                if midlog_times is not None and xlabel == "time":
                    add_midlog_lines(
                        x,
                        midlog_times,
                        sdf["mean_OD"].values,
                    )
                plt.ylabel("OD")
                plt.legend()
                plt.grid()
                curr_plot += 1
                # plot growth rate
                if "gr" in sdf.columns:
                    # growth rate
                    plt.subplot(n_plots, 1, curr_plot, sharex=ax1)
                    plt.plot(x, sdf["gr"].values, "m")
                    if midlog_times and xlabel == "time":
                        add_midlog_lines(x, midlog_times, sdf["gr"].values)
                    plt.ylabel("gr")
                    plt.grid()
                    curr_plot += 1
                # ylabel plot
                plt.subplot(n_plots, 1, curr_plot, sharex=ax1)
                # add inferred GFP per OD if present
                if ylabel == f"bc{fl}perOD" and flperod in sdf.columns:
                    plt.plot(x, sdf[flperod].values, "g.")
                # plot ylabel vs. xlabel
                plt.plot(x, y, "r")
                if max_xy is not None and max_xy[0] is not None:
                    plt.plot(max_xy[0], max_xy[1], "ro")
                if midlog_times and xlabel == "time":
                    add_midlog_lines(x, midlog_times, y)
                plt.ylabel(ylabel)
                plt.grid()
                curr_plot += 1
                # plot bulk GFP
                plt.subplot(n_plots, 1, curr_plot, sharex=ax1)
                plot_bulk_GFP(
                    self,
                    xlabel,
                    fl,
                    strain,
                    con,
                    exp,
                    refstrain,
                    midlog_times,
                )
                # tidy up
                plt.grid()
                plt.xlabel(xlabel)
                plt.suptitle(f"{exp}: {strain} in {con}")
                plt.tight_layout()
                plt.show(block=False)


def set_up_inspect(self, exp, con, strain, xlabel, ylabel, flperod, refstrain):
    """Get data for inspect."""
    sdf = self.s[
        (self.s.experiment == exp)
        & (self.s.strain == strain)
        & (self.s.condition == con)
    ]
    x = sdf[xlabel].values
    y = sdf[ylabel].values
    if "min_midlog_time" in self.sc.columns:
        midlog_times = get_midlog_times(self, strain, con, sdf)
    else:
        midlog_times = None
    # find number of plots
    n_plots = 2
    if flperod in sdf.columns:
        n_plots += 1
    if "gr" in sdf.columns:
        n_plots += 1
    # reference strain
    ref_df = self.s[
        (self.s.experiment == sdf.experiment.unique()[0])
        & (self.s.strain == refstrain)
        & (self.s.condition == sdf.condition.unique()[0])
    ]
    return sdf, x, y, midlog_times, n_plots, ref_df


def plot_bulk_GFP(
    self, xlabel, fl, strain, condition, experiment, refstrain, midlog_times
):
    """Plot bulk GFP for strain of interest and refstrain."""
    rdf = self.r[
        (self.r.experiment == experiment)
        & self.r.strain.isin(["Null", refstrain, strain])
        & (self.r.condition == condition)
    ]
    # GFP-tagged strain
    plt.plot(
        rdf[rdf.strain == strain][xlabel].values,
        rdf[rdf.strain == strain][f"{fl}"].values,
        "g.",
    )
    plt.plot(
        rdf[rdf.strain == refstrain][xlabel].values,
        rdf[rdf.strain == refstrain][f"{fl}"].values,
        "kx",
        alpha=0.5,
        label=refstrain,
    )
    # background - Null wells
    plt.plot(
        rdf[rdf.strain == "Null"][xlabel].values,
        rdf[rdf.strain == "Null"][f"{fl}"].values,
        "m*",
        label="Null",
    )
    if midlog_times and xlabel == "time":
        add_midlog_lines(
            rdf[rdf.strain == strain][xlabel].values,
            midlog_times,
            rdf[rdf.strain == strain][f"{fl}"].values,
        )
    plt.ylabel(fl)
    plt.legend()


def get_midlog_times(p, strain, condition, sdf):
    """Find start and end times of midlog growth."""
    sscdf = p.sc[(p.sc.strain == strain) & (p.sc.condition == condition)]
    t0 = sscdf.min_midlog_time.values[0]
    t1 = sscdf.max_midlog_time.values[0]
    i_t0 = np.argmin((sdf.time.values - t0) ** 2)
    i_t1 = np.argmin((sdf.time.values - t1) ** 2)
    if i_t0 == i_t1:
        print(
            f"inspect: {strain} in {condition} has a "
            "midlog region of size zero."
        )
    return i_t0, i_t1


def add_midlog_lines(x, midlog_times, y):
    """Bound midlog region with dashed lines."""
    i_t0 = midlog_times[0]
    i_t1 = midlog_times[1]
    plt.plot([x[i_t0], x[i_t0]], [0, np.nanmax(y)], "k:")
    plt.plot([x[i_t1], x[i_t1]], [0, np.nanmax(y)], "k:")

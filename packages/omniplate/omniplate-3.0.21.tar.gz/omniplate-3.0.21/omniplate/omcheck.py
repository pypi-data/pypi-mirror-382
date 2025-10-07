"""Functions for checking data consistency."""

import matplotlib.pylab as plt


def check(self, type, style_order=None, sort_by=False, **kwargs):
    """
    Run check for consistency among strains and replicates.

    Arguments
    ---------
    type: str
        Either "max_gr" to plot maximum growth rates, or another variable from
        the sc dataframe, or "midlog_times" to plot the midlog intervals.
    """
    if type in self.sc.columns:
        _check_sc_stat(self, type, style_order, sort_by, **kwargs)
    elif type == "midlog_times":
        _check_midlog_times(self)
    else:
        print(f"{type} unrecognised.")


def _check_sc_stat(self, type, style_order, sort_by, **kwargs):
    """Plot all maximum growth rates for comparison."""
    self.plot(
        x=type,
        y="condition",
        style="strain",
        hue="experiment",
        distinct_colours=True,
        height=12,
        aspect=0.6,
        s=100,
        sort_by=sort_by,
        style_order=style_order,
        title=type,
        no_null=True,
        **kwargs,
    )
    plt.grid()


def _check_midlog_times(self):
    """Show all max and min midlog times, with one plot per condition."""
    if "min_midlog_time" not in self.sc.columns:
        print("Run get_midlog first.")
        return
    cols = [
        "experiment",
        "condition",
        "strain",
        "min_midlog_time",
        "max_midlog_time",
    ]
    df = self.sc[cols].copy()
    df = df[df.strain != "Null"]
    df["key"] = df.experiment + "____" + df.strain
    df["start"] = df.min_midlog_time
    df["end"] = df.min_midlog_time + df.max_midlog_time
    df = df.drop([col for col in cols if col != "condition"], axis=1)
    df = df.reset_index(drop=True)
    # plot
    for condition in df.condition.unique():
        sdf = df[df.condition == condition].reset_index(drop=True)
        plt.figure(figsize=(12, 6))
        labels = sdf.key.values
        for i, row in sdf.iterrows():
            plt.plot(
                [row["start"], row["end"]],
                [i, i],
                "o-",
                linewidth=2,
                label=labels[i],
                markersize=8,
            )
        plt.yticks(range(len(sdf)), labels)
        plt.xlabel("midlog interval")
        plt.xlim(-0.5, max(sdf["end"]) + 0.5)
        plt.title(condition)
        plt.tight_layout()
        plt.show(block=False)

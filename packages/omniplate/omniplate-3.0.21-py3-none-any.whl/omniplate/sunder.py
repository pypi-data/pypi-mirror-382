"""Functions for extracting subsets of the data."""

import numpy as np

import omniplate.omerrors as errors
import omniplate.omgenutils as gu


def get_all_labels(self, label_type, no_null, no_media):
    """List all the labels available for a given label type."""
    if label_type == "experiment":
        all_labels = self.all_experiments
    elif label_type == "condition":
        all_labels = list(
            set(
                [
                    con
                    for e in self.all_conditions
                    for con in self.all_conditions[e]
                ]
            )
        )
        if no_media and "media" in all_labels:
            all_labels.pop(all_labels.index("media"))
    elif label_type == "strain":
        all_labels = list(
            set(
                [
                    strain
                    for e in self.all_strains
                    for strain in self.all_strains[e]
                ]
            )
        )
        if no_null and "Null" in all_labels:
            all_labels.pop(all_labels.index("Null"))
    else:
        raise errors.GetSubset("Nothing found.")
    return all_labels


def get_set(
    self,
    label,
    label_includes,
    label_excludes,
    label_type,
    no_null,
    no_media=True,
):
    """Find user-specified list of experiments, conditions, or strains."""
    all_labels = get_all_labels(self, label_type, no_null, no_media)
    if label != "all":
        # prioritise explicitly specified labels
        labels = gu.make_list(label)
        # check user's choice exists
        bad_labels = [label for label in labels if label not in all_labels]
        # keep only good labels
        labels = [label for label in labels if label not in bad_labels]
    else:
        labels = all_labels
        if label_includes:
            # find those items containing keywords given in 'includes'
            includes = gu.make_list(label_includes)
            newset = []
            for s in all_labels:
                gotone = 0
                for item in includes:
                    if item in s:
                        gotone += 1
                if gotone == len(includes):
                    newset.append(s)
            labels = newset
        if label_excludes:
            # remove any items containing keywords given in 'excludes'
            excludes = gu.make_list(label_excludes)
            exs = []
            for s in all_labels:
                for item in excludes:
                    if item in s:
                        exs.append(s)
                        break
            for ex in exs:
                if ex in labels:
                    labels.pop(labels.index(ex))
    if labels:
        # sort by numeric values in list entries
        return sorted(labels, key=gu.natural_keys)
    else:
        raise errors.GetSubset("No data found.")


def get_all(
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
    no_media=True,
):
    """Return experiments, conditions, and strains."""
    exps = get_set(
        self,
        experiments,
        experiment_includes,
        experiment_excludes,
        "experiment",
        no_null,
        no_media,
    )
    cons = get_set(
        self,
        conditions,
        condition_includes,
        condition_excludes,
        "condition",
        no_null,
        no_media,
    )
    strs = get_set(
        self,
        strains,
        strain_includes,
        strain_excludes,
        "strain",
        no_null,
        no_media,
    )
    return exps, cons, strs


def extract_wells(r_df, s_df, experiment, condition, strain, datatypes):
    """
    Extract a list of data matrices from the r dataframe.

    Each column in each matrix contains the data
    from one well.

    Data is returned for each dtype in datatypes, which may include "time", for
    the given experiment, condition, and strain.
    """
    datatypes = gu.make_list(datatypes)
    # restrict time if necessary
    lrdf = r_df[
        (r_df.time >= s_df.time.min()) & (r_df.time <= s_df.time.max())
    ]
    df = lrdf.query(
        "experiment == @experiment and condition == @condition "
        "and strain == @strain"
    )
    if df.empty:
        return None, None
    else:
        # extract time
        dfw_time = (
            df[["time", "well"]]
            .groupby("well", group_keys=True)["time"]
            .apply(list)
        )
        well_times = [dfw_time[well] for well in dfw_time.index]
        # data may have different durations
        longest_i = np.argmax([len(dfw_time[well]) for well in dfw_time.index])
        t = np.array(well_times[longest_i])
        # extract data
        matrices = []
        for dtype in datatypes:
            dfw_dtype = (
                df[[dtype, "well"]]
                .groupby("well", group_keys=True)[dtype]
                .apply(list)
            )
            data = np.nan * np.ones((len(t), dfw_dtype.shape[0]))
            for i, well in enumerate(dfw_dtype.index):
                data[: len(dfw_dtype[well]), i] = np.array(dfw_dtype[well])
            matrices.append(data)
        if len(datatypes) == 1:
            # return array
            return t, matrices[0]
        else:
            # return list of arrays
            return t, matrices

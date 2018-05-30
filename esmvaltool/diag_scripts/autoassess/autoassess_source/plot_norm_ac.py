#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-

"""
(C) Crown Copyright 2017, the Met Office

Create normalised assessment criteria plot (NAC plot).
"""

from __future__ import division, print_function

import os
import os.path
import sys
import argparse
import csv
import matplotlib.pyplot as plt
import errno
import numpy as np
import matplotlib as mpl
mpl.use('Agg')

# Define some colours
BLACK = '#000000'
RED = '#FF0000'
AMBER = '#FF8C00'
GREEN = '#7CFC00'
OBS_GREY = '#000000'
ACC_GREY = '#00FFFF'
STD_GREY = '#EEEEEE'
NOOBS_GREY = '#A9A9A9'

# Set available markers
# Those towards end of list are not really suitable but do extend list
# - How about custom symbols?
MARKERS = 'ops*dh^v<>+xDH.,'

# Create fakelines for legend using MARKERS above
FAKELINES = [
    plt.Line2D([0, 0], [0, 1], marker=marker, color=BLACK, linestyle='')
    for marker in MARKERS
]

# List of TODO:
#
#  1) What if we want acceptable range only? i.e. no trusted obs but a
#     sensible idea of what the range should be.
#  2) How to get plots to display nicely in matplotlib viewer and non-png
#     images. Issue is legend external to plot falling off screen.


class CommentedFile:
    '''Class to help deal with comments in CSV files'''

    def __init__(self, f, commentstring="#"):
        self.f = f
        self.commentstring = commentstring

    def next(self):
        line = self.f.next()
        while line.startswith(self.commentstring):
            line = self.f.next()
        return line

    def __iter__(self):
        return self


def merge_obs_acc(obs, acc):
    '''
    Routine to merge observational uncertainty and acceptable range
    dictionaries into one dictionary. Returned dictionary will only
    contain metrics from the obs dictionary.

    :param dict obs: Dictonary of observational uncertainties
    :param dict acc: Dictonary of acceptable ranges
    :returns: A merge of the obs and acc dictionaries
    :rtype: dict
    '''
    metrics = {}
    for metric in obs.keys():
        values = list(obs[metric])
        if metric in acc:
            values += list(acc[metric])
        metrics[metric] = tuple(values)
    return metrics


def write_order_metrics(csvfile, metrics):
    '''
    Routine to write out an ordered list of metrics csv file

    Not really csv but easily written out by csv package. This is a line by
    line ordered list of the metrics that will be plotted on a NAC plot. It
    should be read in and out of a list object.

    :param str csvfile: CSV file name
    :param list metrics: Ordered list of metrics
    '''
    if metrics:
        try:
            outf = open(csvfile, 'w')
        except IOError as e:
            if e.errno == errno.EACCES:
                pass  # Raise Error
        else:
            with outf:
                writer = csv.writer(outf, delimiter=',', quotechar='"')
                for metric in metrics:
                    writer.writerow([metric])


def write_model_metrics(csvfile, metrics):
    '''
    Routine to write out model metrics csv file

    An unordered list of metrics with a single value metric that are obtained
    from processing model output. Note that the model uncertainty also fits
    this description. This should be read in and out of a dictionary object
    with metric name as key and single float as value.

    :param str csvfile: CSV file name
    :param dict metrics: Dictionary containing metric values
    '''
    if metrics:
        try:
            outf = open(csvfile, 'w')
        except IOError as e:
            if e.errno == errno.EACCES:
                pass  # Raise Error
        else:
            with outf:
                writer = csv.writer(outf, delimiter=',', quotechar='"')
                for metric in metrics.items():
                    writer.writerow(metric)


def write_obs_metrics(csvfile, obs, acc):
    '''
    Routine to read in observation metrics csv file

    An unordered list of metrics with either 2 or 4 values. The first 2 vals
    are the observation range and must exist for any entry. The second 2 vals,
    if they exist, are for the acceptable range of the metric. The observation
    metrics can either be generated through the same process as the model or
    set as fixed reference values. Note that if the metric is a relative
    metric (e.g. error) then the first value of a pair should always be zero.
    These should be read in and out of two dictionary objects (one for obs and
    one for acc) with metric name as key and a tuple of two floats as the val.

    :param str csvfile: CSV file name
    :param dict obs: Dictonary of observational uncertainties
    :param dict acc: Dictonary of acceptable ranges
    '''
    metrics = merge_obs_acc(obs, acc)
    if metrics:
        try:
            outf = open(csvfile, 'w')
        except IOError as e:
            if e.errno == errno.EACCES:
                pass  # Raise Error
        else:
            with outf:
                writer = csv.writer(outf, delimiter=',', quotechar='"')
                for (metric, values) in metrics.items():
                    writer.writerow([metric] + list(values))


def read_order_metrics(csvfile, required=False):
    '''
    Routine to read in ordered list of metrics csv file

    Not really csv but easily read in by csv package. This is a line by line
    ordered list of the metrics that will be plotted on a NAC plot. It should
    be read in and out of a list object.

    :param str csvfile: CSV file name containing an ordered list of metrics
    :param bool required: If True then raise error if file does not exist
    :returns: An ordered list containing metric names
    :rtype: list
    '''
    metrics = []
    if csvfile is not None:
        try:
            inf = open(csvfile, 'rb')
        except IOError as e:
            if e.errno == errno.EACCES:
                if required:
                    pass  # Raise Error
                else:
                    pass  # Raise Warning
        else:
            with inf:
                reader = csv.reader(
                    CommentedFile(inf), delimiter=',', quotechar='"')
                # TODO: Must be a better way of unpacking data that does not
                #       rely on testing number of elements on line
                for row in reader:
                    if len(row) == 1:
                        metrics.append(row[0])
                    else:
                        msg = "Ordered metrics file is not properly configured"
                        raise ValueError(msg)

    return metrics


def read_model_metrics(csvfile, required=False):
    '''
    Routine to read in model metrics csv file

    An unordered list of metrics with a single value metric that are obtained
    from processing model output. Note that the model uncertainty also fits
    this description. This should be read in and out of a dictionary object
    with metric name as key and single float as value.

    :param str csvfile: CSV file name containing model data
    :param bool required: If True then raise error if file does not exist
    :returns: Dictionary containing metric values
    :rtype: dict
    '''
    metrics = {}
    if csvfile is not None:
        try:
            inf = open(csvfile, 'rb')
        except IOError as e:
            if e.errno == errno.EACCES:
                if required:
                    pass  # Raise Error
                else:
                    pass  # Raise Warning
        else:
            with inf:
                reader = csv.reader(
                    CommentedFile(inf), delimiter=',', quotechar='"')
                # TODO: Must be a better way of unpacking data that does not
                #       rely on testing number of elements on line
                for row in reader:
                    metric = row.pop(0)
                    if len(row) == 1:
                        metrics[metric] = float(row[0])
                    else:
                        msg = "Model metrics file is not properly configured"
                        raise ValueError(msg)

    return metrics


def read_obs_metrics(csvfile, required=False):
    '''
    Routine to read in observation metrics csv file

    An unordered list of metrics with either 2 or 4 values. The first 2 values
    are the observation range and must exist for any entry. The second 2 value
    if they exist, are for the acceptable range of the metric. The observation
    metrics can either be generated through the same process as the model or
    set as fixed reference values. Note that if the metric is a relative metri
    (e.g. error) then the first value of a pair should always be zero. These
    should be read in and out of two dictionary objects (one for obs and one
    for acc) with metric name as key and a tuple of two floats as the value.

    :param str csvfile: CSV file name containing observational data
    :param bool required: If True then raise error if file does not exist
    :returns: A pair of metric dictionaries containing observational
              uncertainties and acceptable ranges
    :rtype: tuple
    '''
    obs = {}
    acc = {}
    if csvfile is not None:
        try:
            inf = open(csvfile, 'rb')
        except IOError as e:
            if e.errno == errno.EACCES:
                if required:
                    pass  # Raise Error
                else:
                    pass  # Raise Warning
        else:
            with inf:
                reader = csv.reader(
                    CommentedFile(inf), delimiter=',', quotechar='"')
                # TODO: Must be a better way of unpacking data that does not
                #       rely on testing number of elements on line
                for row in reader:
                    metric = row.pop(0)
                    # Contrary to documentation, allowing a single entry when
                    #  there is only a single observation value. Will
                    #  ultimately want to remove this as all observations
                    #  should be uncertainty ranges (i.e. multiple obs sources)
                    if len(row) == 1:
                        obs[metric] = tuple(
                            sorted([float(row[0]),
                                    float(row[0])]))
                    elif len(row) == 2:
                        obs[metric] = tuple(
                            sorted([float(row[0]),
                                    float(row[1])]))
                    elif len(row) == 4:
                        obs[metric] = tuple(
                            sorted([float(row[0]),
                                    float(row[1])]))
                        acc[metric] = tuple(
                            sorted([float(row[2]),
                                    float(row[3])]))
                    else:
                        msg = "Obs metrics file is not properly configured"
                        raise ValueError(msg)

    return (obs, acc)


def metric_colour(test, ref=1.0, var=None, obs=None, acc=None):
    '''
    Routine to determine whether to colour metric as:

    GREEN = test within observational uncertainty or acceptable range
    AMBER = within model uncertainty, or better than reference but neither ref
            or test within observational bounds or acceptable range
    RED = worse than reference and outside model uncertainty
    GREY = no observational uncertainty or acceptable range

    In a lot of instances test/var/obs/acc will have been normalised by ref, so
    ref=1.0.
    obs and acc should be 2 element tuples that indicate the range of
    uncertainty that is acceptable.
    The model uncertainty is defined as (ref-var, ref+var)

    :param float test: Test metric value
    :param float ref: Reference metric value
    :param float var: Model uncertainty value
    :param tuple obs: Observational uncertainty as (min, max)
    :param tuple acc: Acceptable range as (min, max)
    :returns: Colour to use in plot indicating performance of metric
    :rtype: str
    '''

    # Default colour to NOOBS_GREY indicating no observational uncertainty
    colour = NOOBS_GREY

    # If specified, find if test within model uncertainty
    is_test_in_var = False
    if var is not None:
        is_test_in_var = (ref - var <= test <= ref + var)
        # Get AMBER automatically if test within model uncertainty, or RED if
        #  not within model uncertainty
        if is_test_in_var:
            colour = AMBER
        else:
            colour = RED

    # If using acceptable ranges, use as proxy for observational uncertainty
    if acc is not None:
        obs = acc

    # Only do the rest if observational uncertainty is specified
    if obs is not None:

        # Turn data into logicals:

        # Find if reference and test within observational uncertainty
        is_ref_in_obs = (obs[0] <= ref <= obs[1])
        is_test_in_obs = (obs[0] <= test <= obs[1])

        # Is test better than reference, judge by which is closer to
        # observational uncertainty.
        # NOTE: Don't worry here about whether reference or test are within
        #       observational uncertainty as logic for colours precludes that
        #       situation.
        ref_err = min(abs(ref - obs[0]), abs(ref - obs[1]))
        test_err = min(abs(test - obs[0]), abs(test - obs[1]))
        is_test_better = (test_err <= ref_err)

        # Now for colour logic:

        # Default to RED (if not already set) for if test definitely worse,
        #  will try to turn it into a different colour
        if colour == NOOBS_GREY:
            colour = RED
        # Get GREEN automatically if test within observational uncertainty
        if is_test_in_obs:
            colour = GREEN
        else:
            # If test outside model uncertainty, but reference outside
            #  observational uncertainty and test is better than reference
            #  then get AMBER.
            if not is_test_in_var:
                if (not is_ref_in_obs) and is_test_better:
                    colour = AMBER

    return colour


def metric_colours(test, ref=None, var=None, obs=None, acc=None):
    '''
    Routine to loop over metrics and generate list of colours

    :param dict test: Dictionary of test metrics
    :param dict ref: Dictionary of reference metrics
    :param dict var: Dictionary of model uncertainties as single values
    :param dict obs: Dictionary of observation uncertainties as (min, max)
    :param dict acc: Dictionary of acceptable ranges as (min, max)
    :returns: Dictionary of colours for test metrics
    :rtype: dict
    '''

    # initialize
    if ref is None:
        ref = {}
    if var is None:
        var = {}
    if obs is None:
        obs = {}
    if acc is None:
        acc = {}
    colours = {}

    if ref:
        # Test to make sure if reference metrics dictionary not empty then it
        #  contains the same metrics as test metrics dictionary
        assert sorted(test.keys()) == sorted(ref.keys()), \
            "If supplying ref it must have same metrics as test"
    else:
        # Create reference metrics dictionary with values of 1.0 to match
        #  test metrics dictionary
        ref = {metric: 1.0 for metric in test.keys()}

    for metric in test.keys():
        colours[metric] = metric_colour(
            test[metric],
            ref=ref[metric],
            var=var.get(metric, None),
            obs=obs.get(metric, None),
            acc=acc.get(metric, None))

    return colours


def normalise(test, ref, strict=False):
    '''
    Routine to normalise contents of test by contents of ref

    :param dict test: Dictionary of test metrics
    :param dict ref: Dictionary of reference metrics
    :param bool strict: if True then test and ref must have same metrics
    :returns: Dictionary of normalised test metrics
    :rtype: dict
    '''

    if strict:
        # Test to make sure reference metrics dictionary contains the same
        # metrics as test metrics dictionary
        assert sorted(test.keys()) == sorted(ref.keys()), \
            "ref and test must have same set of metrics"

    norm = {}
    for metric in test.keys():
        if metric in ref:
            if len(test[metric]) == 1:  # try
                norm[metric] = test[metric] / ref[metric]
            else:  # except
                norm[metric] = tuple(x / ref[metric] for x in test[metric])

    return norm


def plot_std(ax, metrics, data, color=STD_GREY, zorder=0):
    '''
    Plot model uncertainty as filled bars about nac=1 line

    :param axes ax: ``matplotlib.axes`` to plot data in
    :param list metrics: List of metrics to plot in order
    :param dict data: Metrics dictionary
    :param str color: Colour to plot bars
    :param int zorder: Matplotlib plot layer
    '''

    # Extract metric data and line up with requested metrics
    coord = [i + 1 for (i, metric) in enumerate(metrics) if metric in data]
    std = [data[metric] for metric in metrics if metric in data]

    # Convert to numpy arrays
    coord = np.array(coord)
    std = np.array(std)

    # Create plot
    ax.barh(
        coord,
        2.0 * std,
        left=1.0 - std,
        height=1.0,
        align='center',
        color=color,
        linewidth=0,
        zorder=zorder)


def plot_obs(ax, metrics, data, color=OBS_GREY, zorder=1):
    '''
    Plot obs range as error bars

    :param axes ax: ``matplotlib.axes`` to plot data in
    :param list metrics: List of metrics to plot in order
    :param dict data: Metrics dictionary
    :param str color: Colour to plot error bars
    :param int zorder: Matplotlib plot layer
    '''

    # Extract metric data and line up with requested metrics
    coord = [i + 1 for (i, metric) in enumerate(metrics) if metric in data]
    obsmin = [data[metric][0] for metric in metrics if metric in data]
    obsmax = [data[metric][1] for metric in metrics if metric in data]

    # Convert to numpy arrays
    coord = np.array(coord)
    obsmin = np.array(obsmin)
    obsmax = np.array(obsmax)

    # Calculate inputs for plotting
    orig = 0.5 * (obsmax + obsmin)
    err = 0.5 * (obsmax - obsmin)

    # Create plot
    ax.errorbar(
        orig,
        coord,
        xerr=err,
        fmt='none',
        ecolor=color,
        capsize=5,
        zorder=zorder)


def plot_metrics(ax, metrics, data, cols, marker, zorder=3):
    '''
    Plot metrics using symbols

    :param axes ax: ``matplotlib.axes`` to plot data in
    :param list metrics: List of metrics to plot in order
    :param dict data: Metrics dictionary
    :param dict cols: Metric colours dictionary
    :param str marker: Matplotlib symbol to use in plot
    :param int zorder: Matplotlib plot layer
    '''

    # Extract metric data and line up with requested metrics
    coord = [i + 1 for (i, metric) in enumerate(metrics) if metric in data]
    pdata = [data[metric] for metric in metrics if metric in data]
    pcols = [cols[metric] for metric in metrics if metric in data]

    # Convert to numpy arrays
    coord = np.array(coord)
    pdata = np.array(pdata)
    pcols = np.array(pcols)

    # Create plot
    ax.scatter(
        pdata,
        coord,
        s=50,
        edgecolors=BLACK,
        c=pcols,
        marker=marker,
        zorder=zorder)


def plot_get_limits(tests, obs, acc, extend_y=False):
    '''
    Determine data axis limits

    :param list tests: Test experiment metrics dictionary list
    :param dict obs: Observational uncertainty metrics dictionary
    :param dict acc: Acceptable range metrics dictionary
    :param bool extend_y: Extend y-axis to include obs/acc ranges
    '''

    # Calculate absmax/max/min for experiments
    minval = min([min(test.values()) for test in tests])
    maxval = max([max(test.values()) for test in tests])
    maxabs = max([abs(x) for x in test.values() for test in tests])

    # If want to extend beyond range of observations
    if extend_y:
        if obs:
            ominval = min([min(x, y) for (x, y) in obs.values()])
            omaxval = max([max(x, y) for (x, y) in obs.values()])
            omaxabs = max([max(abs(x), abs(y)) for (x, y) in obs.values()])
            maxabs = max(maxabs, omaxabs)
            minval = min(minval, ominval)
            maxval = max(maxval, omaxval)
        if acc:
            aminval = min([min(x, y) for (x, y) in acc.values()])
            amaxval = max([max(x, y) for (x, y) in acc.values()])
            amaxabs = max([max(abs(x), abs(y)) for (x, y) in acc.values()])
            maxabs = max(maxabs, amaxabs)
            minval = min(minval, aminval)
            maxval = max(maxval, amaxval)

    # Add/Subtract a little bit extra to fully contain plot
    extend = 0.05
    extra = maxabs * extend
    minval -= extra
    maxval += extra

    # Make range no less than (0, 2)
    maxval = max(maxval, 2.0)
    minval = min(minval, 0.0)

    return (minval, maxval)


def plot_nac(cref,
             ctests,
             ref,
             tests,
             metrics=None,
             var=None,
             obs=None,
             acc=None,
             extend_y=False,
             title=None,
             ofile=None):
    '''
    Routine to produce NAC plot

    :param str cref: Reference experiment name
    :param list ctests: Test experiment names list
    :param dict ref: Reference experiment metric dictionary
    :param list tests: Test experiment metrics dictionary list
    :param list metrics: List of metrics to plot in order
    :param dict var: Model uncertainty metrics dictionary
    :param dict obs: Observational uncertainty metrics dictionary
    :param dict acc: Acceptable range metrics dictionary
    :param bool extend_y: Extend y-axis to include obs/acc ranges
    :param str title: Plot title
    :param str ofile: Plot file name
    '''

    # initialize
    if metrics is None:
        metrics = []
    if var is None:
        var = {}
    if obs is None:
        obs = {}
    if acc is None:
        acc = {}

    # Create plot figure and axes
    (fig, ax) = plt.subplots()

    # If metrics haven't been supplied then generate from reference metrics
    if not metrics:
        metrics = sorted(ref.keys())

    # Normalise obs/acc/var by ref
    n_var = normalise(var, ref)
    n_obs = normalise(obs, ref)
    n_acc = normalise(acc, ref)

    # Plot obs/acc/var
    plot_std(ax, metrics, n_var, color=STD_GREY, zorder=0)
    plot_obs(ax, metrics, n_acc, color=ACC_GREY, zorder=1)
    plot_obs(ax, metrics, n_obs, color=OBS_GREY, zorder=2)

    # Plot metric data
    n_tests = []
    for (test, marker) in zip(tests, MARKERS):

        # Normalise test by ref
        n_test = normalise(test, ref, strict=True)

        # Check for green/amber/red/grey
        colours = metric_colours(n_test, var=n_var, obs=n_obs, acc=n_acc)

        # Plot test
        plot_metrics(ax, metrics, n_test, colours, marker, zorder=3)

        # Keep normalised test data to help configure plot
        n_tests.append(n_test)

    # Find plot limits
    limits = plot_get_limits(n_tests, n_obs, n_acc, extend_y=extend_y)

    # Set limits, label axes and add norm=0 & 1 lines
    ax.axvline(0.0, color=BLACK, linestyle='dotted')
    ax.axvline(1.0, color=BLACK)
    ax.set_yticks(np.arange(len(metrics)) + 1)
    ax.set_yticklabels(metrics, ha='right', fontsize='x-small')
    ax.set_ylim(len(metrics) + 0.5, 0.5)
    ax.set_xlim(limits)
    ax.set_xlabel('Normalised Assessment Criteria', fontsize='small')
    ax.tick_params(axis='x', labelsize='small')
    if title is not None:
        ax.set_title(title)

    # Add plot legend
    legend = ax.legend(
        FAKELINES[0:len(ctests)],
        ctests,
        bbox_to_anchor=(1, 1),
        loc=2,
        numpoints=1,
        fancybox=True,
        fontsize='small')
    legend.set_title('Vs %s' % cref, prop={'size': 'small'})

    # Display or produce file
    if ofile:
        # Create directory to write file to
        odir = os.path.dirname(ofile)
        if not os.path.isdir(odir):
            os.makedirs(odir)
        # Note that bbox_inches only works for png plots
        plt.savefig(ofile, bbox_extra_artists=(legend, ), bbox_inches='tight')
    else:
        # Need the following to attempt to display legend in frame
        # TODO: Is there a better way of doing this?
        fig.subplots_adjust(right=0.85)
        plt.show()
    plt.close()


def parse_args(cli_args):
    """
    Parse arguments in a function to facilitate testing. Contains all command
    line options.

    :param list cli_args: Command line arguments from sys.argv.
    :returns: Checked command line arguments.
    :rtype: argparse.Namespace
    """

    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument(
        '--exp',
        required=True,
        help='Test experiment names (commma separated)')
    parser.add_argument(
        '--ref', required=True, help='Reference experiment name')
    parser.add_argument(
        '--file-exp',
        required=True,
        help='Experiment metric files (commma separated)')
    parser.add_argument(
        '--file-ref', required=True, help='Reference metric file')
    parser.add_argument('--file-ord', default=None, help='Metric order file')
    parser.add_argument(
        '--file-var', default=None, help='Model uncertainty metric file')
    parser.add_argument(
        '--file-obs', default=None, help='Observations metric file')
    parser.add_argument('--plot', default=None, help='Plot file to be created')
    parser.add_argument('--title', default=None, help='Plot title')
    parser.add_argument(
        '--exty',
        default=False,
        action='store_true',
        help='Extend y axis to include observation uncertainties')

    # Return parsed args
    return parser.parse_args(cli_args)


def main():
    '''Creating plots from existing metrics files at the command line'''

    # Parse script arguments
    args = parse_args(sys.argv[1:])
    if args.plot:
        args.plot = os.path.abspath(args.plot)

    # Check size of experiment inputs
    expt_files = args.file_exp.split(',')
    expt_names = args.exp.split(',')
    assert len(expt_files) == len(expt_names), \
        'Number of experiments and experiment files must be the same'

    # Read metrics files
    metrics = read_order_metrics(args.file_ord)
    ref = read_model_metrics(args.file_ref)
    tests = [read_model_metrics(expt_file) for expt_file in expt_files]
    var = read_model_metrics(args.file_var)
    (obs, acc) = read_obs_metrics(args.file_obs)

    # Produce plot
    plot_nac(
        args.ref,
        expt_names,
        ref,
        tests,
        metrics=metrics,
        var=var,
        obs=obs,
        acc=acc,
        extend_y=args.exty,
        title=args.title,
        ofile=args.plot)


if __name__ == '__main__':
    main()

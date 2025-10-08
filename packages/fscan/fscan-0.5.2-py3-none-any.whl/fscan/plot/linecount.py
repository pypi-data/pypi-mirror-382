# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) Taylor Starkman (2024)
#               Ansel Neunzert (2024)
#               Evan Goetz (2025)
#
# This file is part of fscan

from matplotlib import pyplot as plt
from ..utils import dtutils as dtl
from ..utils import io
import numpy as np
import argparse
import matplotlib.dates as mdates
import matplotlib as mpl
from pathlib import Path
mpl.use("Agg")


def linecount_plots(autolinesType, f_bins, segtypePath, outfile_heatmap,
                    outfile_countplot, channel, numSFTsCutoff,
                    dataPtsInHistory, analysisStart, analysisEnd,
                    analysisDuration, averageDuration, snapToLast, all_dates):
    """
    This function generates two plots: a heatmap plot of the line density per
    Hz per root (number of SFTs), and a simple count of the lines over time.
    It pulls from the Fscan auto-generated lines files.
    """

    # A default set of bands
    if f_bins is None:
        f_bins = [
            '0-200Hz', '200-400Hz', '(Violin Mode) 400-600Hz',
            '600-900Hz', '(Violin Mode) 900-1100Hz',
            '1100-1400Hz', '(Violin Mode) 1400-1600Hz',
            '1600-1800Hz', '1800-2000Hz',
        ]

    # Produces list of dictionaries containing all the metadata for every day
    # that data exists
    data = dtl.metadata_where_fields_exist_in_range(
                segtype_path=segtypePath,
                fields=[f"autolines-{autolinesType}-path"],
                only_channels=[channel],
                analysisStart=analysisStart,
                analysisEnd=analysisEnd,
                analysisDuration=analysisDuration,
                averageDuration=averageDuration,
                snapToLast=snapToLast)
    for d in data:
        d['heatmap_index'] = all_dates.index(d['epoch-label'])

    # Take the f_bins specified in args, split into bin max and min values,
    # and remove any non-digit characters in string to allow labeling of
    # frequency bins of interest through the command line input
    split_bands = [f_bins[i].split('-') for i in range(len(f_bins))]
    high_freqs = [split_bands[i][1] for i in range(len(f_bins))]
    low_freqs = [split_bands[i][0] for i in range(len(f_bins))]
    bin_maxs = np.array([''.join(ch for ch in high_freqs[i] if
                         ch.isdigit()) for i in
                         range(len(high_freqs))]).astype(int)
    bin_mins = np.array([''.join(ch for ch in low_freqs[i]
                         if ch.isdigit()) for i in
                         range(len(low_freqs))]).astype(int)
    bin_widths = bin_maxs - bin_mins

    # Define array to be filled with the number of lines per square root num
    # sfts per frequency bin values
    heatmap_values = np.zeros((len(f_bins), len(all_dates)))
    count_values = np.zeros(len(all_dates))
    sufficient = np.full(len(all_dates), False)

    # Open file containing all lines detected on a given day, ensure that the
    # given day has data, and count the number of lines per frequency bin
    for epoch_data in data:
        n_sfts = epoch_data['num-sfts-expected-per-channel']
        if n_sfts >= numSFTsCutoff:
            sufficient[epoch_data['heatmap_index']] = True
            linesfile = epoch_data[f"autolines-{autolinesType}-path"]
            lines, _ = io.load_lines_from_linesfile(linesfile)
            num_lines_per_freq_band = np.array([len(lines[(lines <=
                                                bin_maxs[j]) &
                                                (lines > bin_mins[j])])
                                                for j in
                                                range(len(f_bins))])
            heatmap_values[:, epoch_data['heatmap_index']] = np.array(
                num_lines_per_freq_band/np.sqrt(n_sfts)/bin_widths)
            count_values[epoch_data['heatmap_index']] = len(lines)

    # Create "history" arrays that don't include the most recent epoch
    # (to establish threshold values)
    sufficient_history = sufficient[:-1]
    count_history = count_values[:-1][sufficient_history]
    count_history = count_history[-1*dataPtsInHistory:]
    # Avoiding numpy warnings, just be clear that we need at least 2
    # values to determine mean and std deviation
    if len(count_history) > 1:
        count_mean = np.mean(count_history)
        count_std = np.std(count_history)
    else:
        count_mean = np.nan
        count_std = np.nan

    # Define array to create an alert tag on a frequency bin if value is above
    # threshold
    alerts = np.zeros(len(heatmap_values[:, -1])).astype(str)

    # Loop through all frequency bins and determine if the most recent date is
    # above the threshold defined as mean + 2 * standard deviation
    for i in range(len(alerts)):
        heatmap_history = heatmap_values[i, :-1][sufficient_history]
        heatmap_history = heatmap_history[-1*dataPtsInHistory:]
        # Avoiding numpy warnings, just be clear that we need at least 2
        # values to determine mean and std deviation
        if len(heatmap_history) > 1:
            mean = np.mean(heatmap_history)
            std = np.std(heatmap_history)
        else:
            mean = np.nan
            std = np.nan
        thresh = mean + std * 2

        if heatmap_values[i, -1] >= thresh:
            alerts[i] = 'ALERT'

    # Define location of frequency bin ticks and use tick locations to produce
    # an array containing only the values necessary to place ticks on bins
    # where the value is above the threshold
    y_tick_locations = np.arange(0, len(f_bins), 1)

    if sufficient[-1]:
        alert_loc = y_tick_locations[alerts != '0.0']
        alerts = alerts[alerts != '0.0']
    else:
        alerts = np.array(['INSUFFICIENT DATA'])
        if len(f_bins) % 2 == 1:
            alert_loc = np.array([np.ceil(len(f_bins)/2)])
        else:
            alert_loc = np.array([len(f_bins)/2])
    y_tick_locations = np.arange(0, len(f_bins), 1)

    # Create datetime objects with the start and end dates
    startDate = dtl.datestr_to_datetime(all_dates[0])
    endDate = dtl.datestr_to_datetime(all_dates[-1])

    # Calculate the length of the analysis in seconds, then determine how often
    # to include date labels on the x-axis to avoid overcrowding and create the
    # necessary 'days' object to input into matplotlib later
    sduration = (endDate - startDate).total_seconds()
    if sduration <= 31*24*60*60:  # one month
        days = mdates.DayLocator(interval=1)
    elif sduration <= 3*31*24*60*60:  # three months
        days = mdates.DayLocator(interval=7)
    else:  # anything longer than three months
        days = mdates.DayLocator(interval=30)

    # Determine if a cutoff is necessary due to saturation. If a day in the
    # analysis is saturated, then the max value displayed on the colorbar
    # will be 3 * median of all values.
    # If no days are saturated, then the max value for the colorbar will
    # be the max value present in the heatmap
    total_mean = np.mean(heatmap_values)
    median = np.median(heatmap_values)

    # Handle case where there's no data at all above zero in the heatmap
    if np.all(heatmap_values <= 0):
        cutofflow = 1
        cutoffhigh = 2

    # Handle normal cases where there's data
    else:
        cutofflow = np.min(heatmap_values[heatmap_values > 0])
        if np.absolute(total_mean - median) > 10:
            cutoffhigh = 3 * median
        else:
            cutoffhigh = np.max(heatmap_values)

    # Convert date strings from entire analysis duration to datetime objects
    # for effective plotting
    dates_as_datetime = np.array(
        [dtl.datestr_to_datetime(x) for x in all_dates])

    plt.clf()
    cmap = plt.cm.viridis.copy()
    norm = mpl.colors.Normalize(vmin=cutofflow, vmax=cutoffhigh)

    # Create figure to make heatmap within
    fig, ax1 = plt.subplots()
    fig.subplots_adjust(wspace=1)

    # Set up axes and labels for the heatmap
    ax1.xaxis.set_major_locator(days)
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y%m%d'))
    ax1.xaxis.set_tick_params(rotation=-90, size=8)
    ax1.set_xlabel("Date")
    ax1.set_yticks(y_tick_locations,
                   labels=f_bins,
                   fontsize=8)
    ax1.set_title("Line density per Hz per sqrt(# of SFTs)")

    # Define the heatmap
    im1 = ax1.pcolormesh(dates_as_datetime, f_bins, heatmap_values,
                         norm=norm,
                         cmap=cmap)
    # Tell matplotlib that if the value is below the minimum heatmap value, it
    # should be gray (this grays out any days where data is not present)
    im1.cmap.set_under('#C0C0C0')

    # If any days are saturated, colorbar will have an upward pointing arrow
    # If no days are saturated, there will be no arrow on the colorbar
    if cutoffhigh == np.max(heatmap_values):
        cbar_extend = 'min'
    else:
        cbar_extend = 'both'
    cbar = fig.colorbar(im1,
                        ax=ax1,
                        extend=cbar_extend,
                        location='bottom',
                        pad=0.3,
                        )

    num_ticks = 8  # number of ticks on colorbar

    # Define the values to be shown on the colorbar, create the arrays
    # needed to label the colorbar, and set the tick locations/labels
    numerical_cbar_labels = np.linspace(cutofflow, cutoffhigh, num_ticks - 1)
    numerical_cbar_labels = np.trunc(numerical_cbar_labels * 100)/100
    cbar_labels = np.concatenate((['Insufficient\ndata'],
                                  numerical_cbar_labels))
    cbar.ax.set_xticks(ticks=np.linspace(cutofflow, cutoffhigh, num_ticks),
                       labels=cbar_labels,
                       )
    cbar.ax.set_ylabel(r"$\frac{N_{\mathrm{lines}}}"
                       r"{\sqrt{N_{\mathrm{SFTs}}} \cdot \mathrm{Hz}}$",
                       rotation=0,
                       size=15,
                       )
    cbar.ax.yaxis.set_label_position("left")
    cbar.ax.yaxis.set_label_coords(-0.2, -0.1)

    # Define second axis to display alert labels
    ax2 = ax1.twinx()

    # Set up second axis and plot alerts
    if sufficient[-1]:
        color = 'red'
        size = 8
        offset = 0.4
    else:
        color = 'orange'
        size = 12
        offset = 0.8

    ax2.set_yticks(alert_loc + offset, labels=alerts, color=color, size=size)
    ax2.tick_params(right=False,
                    rotation=-90,
                    pad=0.01
                    )
    ax2.pcolormesh(dates_as_datetime, f_bins, heatmap_values,
                   norm=norm,
                   cmap=cmap)

    # Save the heatmap figure and make it look nice
    plt.tight_layout()
    plt.savefig(outfile_heatmap,
                dpi=250)

    # =========================
    # Line count over time plot
    # =========================

    # Set up a new figure to plot the total line count over time
    plt.figure()

    # Plot the total line counts for dates where sufficient data exists
    plt.scatter(dates_as_datetime[sufficient], count_values[sufficient],
                color="deepskyblue",
                )

    # Either mark the latest epoch's data point, or make a note on
    # the title indicating why no data point is marked
    if sufficient[-1]:
        plt.scatter(dates_as_datetime[-1], count_values[-1],
                    color="deepskyblue",
                    linewidth=2,
                    edgecolor='black',
                    label="This epoch",
                    zorder=2,
                    )
        plt.title("Line count over time")
    else:
        plt.title("Line count over time\n (insufficient data for this epoch)")

    # Determine which data points count as part of the history
    # and make a vertical line to mark that span
    dates_history = dates_as_datetime[:-1][
        sufficient_history][-1*dataPtsInHistory:]
    half_epoch = (endDate-startDate)/len(all_dates)/2.
    if len(dates_history) > 0:
        plt.axvspan(dates_history[0]-half_epoch, endDate+half_epoch,
                    color='orange', alpha=0.3,
                    label="Data used in\nthreshold calculation",
                    zorder=0)

    # Set up the horizontal lines to plot, as well as colors and line styles
    hvals = [
            count_mean+2*count_std,
            count_mean+count_std,
            count_mean,
            count_mean-count_std]
    hlabs = [
            "alert threshold\n(mean + 2*stddev)",
            "mean + stddev", "mean", "mean - stddev"]
    cols = ['red', 'orange', 'lightblue', 'lightgreen']
    lws = [3, 1, 1, 1]
    lss = ['solid', 'dotted', 'dotted', 'dotted']

    # Plot the horizontal lines
    for hval, hlab, col, lw, ls in zip(hvals, hlabs, cols, lws, lss):
        plt.axhline(hval, label=hlab,
                    zorder=1,
                    color=col,
                    linewidth=lw,
                    linestyle=ls)

    # Make a legend and plot title
    plt.legend(loc='lower left', bbox_to_anchor=(0, 0))
    plt.grid(visible=False)

    # Force the plot to display the full requested time period
    plt.xlim(startDate, endDate+half_epoch)

    # Format the date axis
    ax_tot = plt.gca()
    ax_tot.xaxis.set_major_locator(days)
    ax_tot.xaxis.set_major_formatter(mdates.DateFormatter('%Y%m%d'))
    ax_tot.xaxis.set_tick_params(rotation=-90, size=8)
    ax_tot.set_xlabel("Date")
    ax_tot.set_ylabel("Number of lines counted")

    # Save the figure
    plt.tight_layout()
    plt.savefig(outfile_countplot,
                dpi=250)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--autolinesType", type=str, default="complete",
                        choices=['complete', 'annotated'],
                        help="Choose 'complete' for all lines found by line "
                        "count. Choose 'annotated' to only plot lines "
                        "identified as belonging to combs")
    parser.add_argument("--fBins", type=str, nargs='*',
                        default=None,
                        help="Frequency bands for dividing up the full "
                        "band to count line artifacts '<fmin>-<fmax>Hz' in "
                        "ascending order")
    parser.add_argument("--segtypePath", type=Path,
                        help='Path to data used to create heatmap')
    parser.add_argument("--outfile-heatmap", type=Path,
                        help="Path to heatmap output image (.png)")
    parser.add_argument("--outfile-countplot", type=Path,
                        help="Path to line count vs time output image (.png)")
    parser.add_argument("--channel", type=str,
                        help="Channel of data to create heatmap of")
    parser.add_argument("--numSFTsCutoff", type=int,
                        help="Number of SFTs required for a day to be "
                        "considered to have sufficient data for analysis")
    parser.add_argument("--dataPtsInHistory", type=int, default=30,
                        help="Epochs to count as part of in recent history")
    parser = dtl.add_dtlargs(parser)
    args = parser.parse_args()

    if args.fBins is None:
        args.fBins = [
            '0-200Hz', '200-400Hz', '(Violin Mode) 400-600Hz',
            '600-900Hz', '(Violin Mode) 900-1100Hz',
            '1100-1400Hz', '(Violin Mode) 1400-1600Hz',
            '1600-1800Hz', '1800-2000Hz',
        ]

    # Get a list of all the days in the interval between analysisStart and
    # analysisEnd. Does not verify if data exists
    _, _, all_dates = dtl.args_to_intervals(args)

    linecount_plots(args.autolinesType,
                    args.fBins,
                    args.segtypePath,
                    args.outfile_heatmap,
                    args.outfile_countplot,
                    args.channel,
                    args.numSFTsCutoff,
                    args.dataPtsInHistory,
                    args.analysisStart,
                    args.analysisEnd,
                    args.analysisDuration,
                    args.averageDuration,
                    args.snapToLast,
                    all_dates)


if __name__ == "__main__":
    main()

"""Module to plot predicition, etc.

This file regroups all functions used to plot the input data or the regression results
"""

import json
import logging
import os

import matplotlib as mpl
import matplotlib.cm as cm
import matplotlib.pyplot as plt
import numpy as np
import rasterio
import seaborn as sns

# from matplotlib.colors import Normalize
from matplotlib.patches import PathPatch
from matplotlib.path import Path
from mpl_toolkits.axes_grid1 import make_axes_locatable
from rasterio.crs import CRS
from rasterio.transform import from_bounds
from rasterio.warp import transform

mpl.use("agg")

CM_PER_INCH = 1 / 2.54
CONSTANT_TIME_STEP = "constant"

# Global soil moisture value limits for consistent colormap scaling
SOIL_MOISTURE_VMIN = 0.1
SOIL_MOISTURE_VMAX = 0.6
SOIL_MOISTURE_UNIT = "g/g"
SCALE_FILE_NAME = "geotiff_scale.json"


def plot_selection(rfo_model):
    """
    Plot visualizations defined by the input selection.

    Parameters:
    - rfo_model (object): Random forest regression model and results.

    This function plots various visualizations based on the input selection
    defined in the rfo_model object. It plots predictors, prediction correlation
    matrix, measurements, model predictions, and predictor importance for each
    time step if specified in what_to_plot attribute of rfo_model. Additionally,
    it can plot predictor importance across all days if specified.
    """
    logging.info("Plotting selection")
    output_dir = rfo_model.work_dir
    what_to_plot = rfo_model.parameters.what_to_plot

    if rfo_model.input_data.all_predictors_constant():
        predictor_time_steps = [CONSTANT_TIME_STEP]
    else:
        predictor_time_steps = rfo_model.input_data.soil_moisture_data.time_steps

    for time_step in predictor_time_steps:
        if what_to_plot.predictors:
            plot_predictors(
                rfo_model,
                time_step,
                output_dir,
                add_measurments=True,
                show_mask=True,
            )

        if what_to_plot.pred_correlation:
            prediction_correlation_matrix(rfo_model, time_step, output_dir)

    for time_step in rfo_model.input_data.soil_moisture_data.time_steps:
        if what_to_plot.prediction_distance:
            logging.info("Plotting prediction distance")
            plot_prediction_distance(rfo_model, time_step, output_dir)

        if what_to_plot.day_measurements:
            plot_measurements(rfo_model, time_step, output_dir)

        if what_to_plot.day_prediction_map:
            plot_rfo_model(rfo_model, time_step, output_dir)

        if what_to_plot.soil_moisture_map_geotiff:
            export_geotiff_soil_moisture_map(rfo_model, time_step, output_dir)

        if what_to_plot.day_predictor_importance:
            plot_predictor_importance(rfo_model, time_step, output_dir)

        if what_to_plot.predictor_distance_map_geotiff:
            export_geotiff_prediction_distance_map(rfo_model, time_step, output_dir)

        if what_to_plot.predictor_maps_geotiff:
            export_geotiff_predictors_map(rfo_model, time_step, output_dir)

        if what_to_plot.measurments_geojson:
            export_geojson_measurements_map(rfo_model, time_step, output_dir)

    if what_to_plot.predictor_maps_geotiff:
        export_geotiff_predictors_map(rfo_model, CONSTANT_TIME_STEP, output_dir)

    if what_to_plot.alldays_predictor_importance:
        predictor_importance_along_days(rfo_model, output_dir)

    if what_to_plot.alldays_predictor_importance_csv:
        export_predictor_importance_csv(rfo_model, output_dir)

    if what_to_plot.pred_correlation_csv:
        export_correlation_matrix_csv(rfo_model, output_dir)


def plot_predictors(
    rfo_model,
    time_step,
    output_dir: str,
    add_measurments=True,
    show_mask=True,
):
    """
    Plot all predictors as color maps.

    Parameters:
    - output_dir (str/None): Directory path to save the plot image file. If None
     return the plot image as a base64 string.

    This function plots all predictors as color maps, with predictor name and
    unit displayed. It automatically adjusts the layout based on the number
    of predictors and shares the same axes for all subplots.
    """
    if show_mask:
        transparency = 0.6
    else:
        transparency = 0

    n_cols = np.ceil(len(rfo_model.input_data.predictors) / 2).astype(int)
    xaxis, yaxis = rfo_model.input_data.soil_moisture_data.geometry.get_axis()

    if CONSTANT_TIME_STEP == time_step:
        x = np.concatenate(list(rfo_model.input_data.soil_moisture_data.x.values()))
        y = np.concatenate(list(rfo_model.input_data.soil_moisture_data.y.values()))
    else:
        x = rfo_model.input_data.soil_moisture_data.x[time_step]
        y = rfo_model.input_data.soil_moisture_data.y[time_step]

    fig, ax = plt.subplots(
        nrows=2,
        ncols=n_cols,
        sharex=True,
        sharey=True,
        figsize=(17 * CM_PER_INCH, 9 * CM_PER_INCH),
    )

    fig.subplots_adjust(wspace=0.4)
    plt.rcParams.update({"font.size": 5})
    axes_count = 0

    nan_mask = rfo_model.input_data.get_nan_mask(time_step)

    for pred_name, pred_data in rfo_model.input_data.predictors.items():
        values_on_nodes = pred_data.values_on_nodes[time_step]

        im = ax.flat[axes_count].pcolormesh(
            xaxis,
            yaxis,
            values_on_nodes,
            shading="auto",
            cmap="viridis",
            alpha=1 - nan_mask.astype(float) * transparency,
        )
        if add_measurments:
            ax.flat[axes_count].scatter(x, y, color="black", s=1, alpha=0.5)

        ax.flat[axes_count].set_title(pred_name)
        ax.flat[axes_count].set_aspect(1)

        divider = make_axes_locatable(ax.flat[axes_count])
        cax = divider.append_axes("right", size="5%", pad=0.15)
        cbar = plt.colorbar(im, cax=cax)
        cbar.ax.set_title(pred_data.information.unit)
        axes_count += 1

    # Hide any remaining empty subplots
    for i in range(axes_count, ax.size):
        fig.delaxes(ax.flat[i])

    if time_step == CONSTANT_TIME_STEP:
        fig_file_path = os.path.join(output_dir, "predictors.png")
    else:
        fig_file_path = os.path.join(output_dir, f"predictors_{time_step}.png")

    plt.savefig(fig_file_path, dpi=300)
    plt.close()


def plot_prediction_distance(rfo_model, time_step, output_dir: str):
    """Plot the distance between predictions and measurements."""
    if len(rfo_model.input_data.prediction_distance) == 0:
        rfo_model.input_data.compute_prediction_distance()

    if rfo_model.input_data.prediction_distance[time_step] is None:
        plt.text(
            0.5,
            0.5,
            "Not enough measurements to construct predictor distance",
            fontsize=12,
            color="black",
            ha="center",
            va="center",
        )
        plt.axis("off")
    else:
        xaxis, yaxis = rfo_model.geometry.get_axis()
        plt.rcParams.update({"font.size": 6})
        fig, ax = plt.subplots(figsize=(16 * CM_PER_INCH, 14 * CM_PER_INCH))
        v_abs = np.max(np.abs(rfo_model.input_data.prediction_distance[time_step]))
        im = plt.pcolormesh(
            xaxis,
            yaxis,
            rfo_model.input_data.prediction_distance[time_step],
            vmin=-v_abs,
            vmax=v_abs,
            cmap="bwr",
            shading="nearest",
        )

        ax.set_title(time_step)
        ax.set_aspect(1)
        cbar = plt.colorbar(im)
        cbar.ax.tick_params(labelsize=14)

        # Add measurements
        plt.scatter(
            rfo_model.input_data.soil_moisture_data.x[time_step],
            rfo_model.input_data.soil_moisture_data.y[time_step],
            c="black",
            s=0.5,
        )
        # plt.figure(figsize=(8, 6))
        # plt.imshow(
        #     rfo_model.input_data.prediction_distance[time_step].T,
        #     cmap="bwr",
        #     norm=Normalize(
        #         vmin=-np.max(
        #             np.abs(rfo_model.input_data.prediction_distance[time_step])
        #         ),
        #         vmax=np.max(
        #             np.abs(rfo_model.input_data.prediction_distance[time_step])
        #         ),
        #     ),
        # )
        # plt.colorbar()
        # plt.gca().set_aspect("equal", adjustable="box")
        # plt.gca().invert_yaxis()

    fig_file_path = os.path.join(
        output_dir, "prediction_distance_" + time_step + ".png"
    )
    logging.info(f"Saving prediction distance plot to {fig_file_path}")
    plt.savefig(fig_file_path, dpi=300)
    plt.close()


def prediction_correlation_matrix(rfo_model, time_step, output_dir: str):
    """Plot the correlation matrix between all predictors, 2 by 2.

    Parameters:
    - rfo_model (object): Random forest regression model and results.
    - output_dir (str/None): Directory path to save the plot image file. If None
     return the plot image as a base64 string.

    This function plots the correlation matrix between all predictors as a heatmap.
    Each cell represents the correlation coefficient between two predictors.
    The x-axis and y-axis labels show the names of the predictors.
    The color intensity indicates the strength and direction of correlation,
    ranging from -1 (strong negative correlation) to 1 (strong positive correlation).
    """
    ticks = list(rfo_model.input_data.predictors.keys())
    plt.figure(figsize=(12 * CM_PER_INCH, 9 * CM_PER_INCH))
    plt.rcParams.update({"font.size": 5})
    correlation_matrix = rfo_model.input_data.compute_correlation_matrix(time_step)
    annot_array = np.vectorize(lambda x: "NaN" if np.isnan(x) else f"{x:.2f}")(
        correlation_matrix
    )
    correlation_matrix = np.nan_to_num(correlation_matrix)  # Replace NaNs with zeros

    sns.heatmap(
        correlation_matrix,
        annot=annot_array,
        fmt="",
        cmap="seismic",
        vmin=-1,
        vmax=1,
        xticklabels=ticks,
        yticklabels=ticks,
        cbar_kws={"label": "Correlation coefficient"},
    )

    if time_step == CONSTANT_TIME_STEP:
        fig_file_path = os.path.join(output_dir, "correlation_matrix.png")
    else:
        fig_file_path = os.path.join(output_dir, f"correlation_matrix_{time_step}.png")

    plt.savefig(fig_file_path, dpi=300)
    plt.close()


def export_correlation_matrix_csv(rfo_model, output_dir: str):
    """
    Export correlation matrices for all time steps as single CSV file.

    Creates a CSV file containing correlation matrices for all time steps in
    stacked format suitable for DataFrame analysis. Each row represents one
    feature's correlations with all other features for a specific time step.

    Parameters:
    - rfo_model (object): Random forest regression model and results.
    - output_dir (str): Directory path to save the CSV file.
    """
    logging.info("Exporting correlation matrix CSV for all time steps")

    # Get time steps and predictor names
    if rfo_model.input_data.all_predictors_constant():
        predictor_time_steps = [CONSTANT_TIME_STEP]
    else:
        predictor_time_steps = rfo_model.input_data.soil_moisture_data.time_steps

    predictor_names = list(rfo_model.input_data.predictors.keys())

    # Create CSV content
    csv_lines = []

    # Header row: time_step, feature, then all predictor names as columns
    header = ["time_step", "feature"] + predictor_names
    csv_lines.append(",".join(header))

    # Data rows for each time step
    for time_step in predictor_time_steps:
        correlation_matrix = rfo_model.input_data.compute_correlation_matrix(time_step)

        for i, row_name in enumerate(predictor_names):
            row_data = [str(time_step), str(row_name)]
            for j in range(len(predictor_names)):
                value = correlation_matrix[i, j]
                if np.isnan(value):
                    row_data.append("")
                else:
                    row_data.append(f"{value:.2f}")
            csv_lines.append(",".join(row_data))

    # Write single CSV file for all time steps
    csv_file_path = os.path.join(output_dir, "correlation_matrix.csv")
    with open(csv_file_path, "w") as f:
        f.write("\n".join(csv_lines))


def draw_error_band_path(x, y, error):
    """
    Calculate normals via centered finite differences.

    Parameters:
    - x (numpy.ndarray): Array of x-coordinates.
    - y (numpy.ndarray): Array of y-coordinates.
    - error (numpy.ndarray): Array of error values corresponding to each point.

    Returns:
    - matplotlib.path.Path: Path object representing the error band.

    This function calculates the normals of a path using centered finite differences.
    It computes the components of the normals and extends the path in both directions
    based on the error values. The resulting path forms an error band around the
    original path.
    """
    dist_to_next_point_x_component = np.concatenate(
        [[x[1] - x[0]], x[2:] - x[:-2], [x[-1] - x[-2]]]
    )
    dist_to_next_point_y_component = np.concatenate(
        [[y[1] - y[0]], y[2:] - y[:-2], [y[-1] - y[-2]]]
    )
    dist_to_next_point = np.hypot(
        dist_to_next_point_x_component, dist_to_next_point_y_component
    )
    normal_x_component = dist_to_next_point_y_component / dist_to_next_point
    normal_y_component = -dist_to_next_point_x_component / dist_to_next_point

    scale_error_vector = 3
    x_error_end_point = x + normal_x_component * error * scale_error_vector
    y_error_end_point = y + normal_y_component * error * scale_error_vector

    vertices = np.block([[x_error_end_point, x[::-1]], [y_error_end_point, y[::-1]]]).T
    codes = np.full(len(vertices), Path.LINETO)
    codes[0] = Path.MOVETO
    return Path(vertices, codes)


def plot_measurements(rfo_model, time_step, output_dir: str):
    """
    Plot measurements as scatter on a x-y map.

    Parameters:
    - rfo_model (object): Random forest regression model and results.
    - time_step (int): Index of the time step for which measurements are plotted.
    - output_dir (str/None): Directory path to save the plot image file. If None
     return the plot image as a base64 string.

    This function plots measurements as a scatter plot on an x-y map. It uses
    the soil moisture measurements from the specified time step of the input
    data. The measurements are colored according to their corresponding soil
    moisture values. If Monte Carlo simulations are enabled, error bands
    representing the standard deviations are overlaid on the scatter plot.
    """
    logging.debug(f"Plotting measurements for time step {time_step}")
    plt.figure()
    plt.gca().set_aspect(1)
    soil_moisture_data = rfo_model.input_data.soil_moisture_data
    x = soil_moisture_data.x[time_step]
    y = soil_moisture_data.y[time_step]
    sc = plt.scatter(
        x,
        y,
        c=soil_moisture_data.soil_moisture[time_step],
        cmap="Spectral",
        s=5,
        vmin=SOIL_MOISTURE_VMIN,
        vmax=SOIL_MOISTURE_VMAX,
        zorder=2,
        label="Measurements",
    )
    if soil_moisture_data.uncertainty:
        plt.gca().add_patch(
            PathPatch(
                draw_error_band_path(
                    x,
                    y,
                    -soil_moisture_data.soil_moisture_dev_low[time_step],
                ),
                alpha=0.3,
                color="purple",
                label="Lower/upper SD",
            )
        )
        plt.gca().add_patch(
            PathPatch(
                draw_error_band_path(
                    x,
                    y,
                    soil_moisture_data.soil_moisture_dev_high[time_step],
                ),
                alpha=0.3,
                color="purple",
            )
        )
    plt.xlabel("Easting (km)")
    plt.ylabel("Northing (km)")
    plt.legend(loc="upper left")
    cbar = plt.colorbar(sc, shrink=0.55)
    cbar.set_label(f"Gravimetric soil moisture ({SOIL_MOISTURE_UNIT})")

    fig_file_path = os.path.join(output_dir, f"measurements_{time_step}.png")
    plt.savefig(fig_file_path, dpi=300)
    plt.close()


def plot_rfo_model(rfo_model, time_step, *args, **kwargs):
    """Plot random forest prediction as a color map."""
    if (
        rfo_model.parameters.monte_carlo_soil_moisture
        or rfo_model.parameters.monte_carlo_predictors
    ):
        return plot_rfo_model_with_dispersion(rfo_model, time_step, *args, **kwargs)
    else:
        return plot_rfo_model_no_dispersion(rfo_model, time_step, *args, **kwargs)


def plot_rfo_model_no_dispersion(
    rfo_model,
    time_step,
    output_dir: str,
):
    """
    Plot soil moisture prediction as a color map.

    Parameters:
    - rfo_model (object): Random forest regression model and results.
    - time_step (int): Index of the time step for which predictions are plotted.
    - output_dir (str/None): Directory path to save the plot image file. If None
     return the plot image as a base64 string.
    """
    logging.debug(f"Plotting prediction no dispersion for time step {time_step}")
    xaxis, yaxis = rfo_model.geometry.get_axis()
    time_index = rfo_model.input_data.soil_moisture_data.time_steps.index(time_step)

    plt.rcParams.update({"font.size": 6})
    fig, ax = plt.subplots(figsize=(16 * CM_PER_INCH, 14 * CM_PER_INCH))
    im = plt.pcolormesh(
        xaxis,
        yaxis,
        rfo_model.prediction[0, time_index, :, :],
        vmin=SOIL_MOISTURE_VMIN,
        vmax=SOIL_MOISTURE_VMAX,
        cmap="Spectral",
    )

    plt.scatter(
        rfo_model.input_data.soil_moisture_data.x[time_step],
        rfo_model.input_data.soil_moisture_data.y[time_step],
        c="black",
        s=0.5,
    )
    ax.set_title(time_step)
    ax.set_aspect(1)
    cbar = plt.colorbar(im)
    cbar.ax.tick_params(labelsize=14)
    fig_file_path = os.path.join(output_dir, "prediction_" + time_step + ".png")
    plt.savefig(fig_file_path, dpi=300)
    plt.close()


def plot_rfo_model_with_dispersion(
    rfo_model,
    time_step,
    output_dir: str,
):
    """
    Plot soil moisture mean prediction and coefficient of dispersion maps.

    Parameters:
    - rfo_model (object): Random forest regression model and results.
    - time_step (int): Index of the time step for which predictions are plotted.
    - output_dir (str/None): Directory path to save the plot image file. If None
     return the plot image as a base64 string.

    This function plots the mean prediction and coefficient of dispersion maps
    for soil moisture predictions. It uses the data from the specified time
    step of the random forest model. Measurement locations are overlaid on the
    plots. The first subplot displays the mean prediction map, while the second
    subplot displays the coefficient of dispersion map.
    """
    logging.debug(f"Plotting prediction with dispersion for time step {time_step}")
    xaxis, yaxis = rfo_model.geometry.get_axis()
    time_index = rfo_model.input_data.soil_moisture_data.time_steps.index(time_step)

    plt.rcParams.update({"font.size": 7})

    fig, axes = plt.subplots(nrows=1, ncols=2, figsize=(16 / 2.54, 10 / 2.54))
    axes[0].set_aspect(1)
    axes[1].set_aspect(1)

    divider = make_axes_locatable(axes[0])
    cax = divider.append_axes("right", size="5%", pad=0.15)
    im = axes.flat[0].pcolormesh(
        xaxis,
        yaxis,
        rfo_model.MC_mean[time_index],
        shading="auto",
        vmin=SOIL_MOISTURE_VMIN,
        vmax=SOIL_MOISTURE_VMAX,
        cmap="Spectral",
    )
    axes.flat[0].scatter(
        rfo_model.input_data.soil_moisture_data.x[time_step],
        rfo_model.input_data.soil_moisture_data.y[time_step],
        c="black",
        s=1,
    )
    axes.flat[0].set_title("Mean")
    plt.colorbar(im, cax=cax)

    im1 = axes.flat[1].pcolormesh(
        xaxis,
        yaxis,
        rfo_model.dispersion_coefficient[time_index],
        shading="auto",
        vmin=0,
        vmax=0.15,
        cmap="Reds",
    )
    axes.flat[1].set_title("Coefficient of dispersion")
    axes.flat[1].tick_params(axis="y", left=False, labelleft=False)
    divider = make_axes_locatable(axes[1])
    cax = divider.append_axes("right", size="5%", pad=0.15)
    plt.colorbar(im1, cax=cax)

    fig.suptitle(time_step)

    fig_file_path = os.path.join(output_dir, "prediction_" + time_step + ".png")
    plt.savefig(fig_file_path, dpi=300)
    plt.close()


def plot_monte_carlo_iteration(
    rfo_model,
    time_step,
    iteration_index,
    output_dir: str,
):
    """Plot the Monte Carlo itration for the given RFO model and time step.

    Parameters:
    - rfo_model (object): The RFO model containing prediction data.
    - time_step (int): The time step index for plotting.
    - iteration_index (int): The iteration index for Monte Carlo simulation.
    - output_dir (str/None): Directory path to save the plot image file. If None
     return the plot image as a base64 string.
    """
    xaxis, yaxis = rfo_model.geometry.get_axis()
    time_step = rfo_model.input_data.soil_moisture_data.time_steps[time_step]

    plt.rcParams.update({"font.size": 6})
    fig, ax = plt.subplots(figsize=(16 * CM_PER_INCH, 14 * CM_PER_INCH))
    im = plt.pcolormesh(
        xaxis,
        yaxis,
        rfo_model.prediction[iteration_index, time_step, :, :],
        vmin=SOIL_MOISTURE_VMIN,
        vmax=SOIL_MOISTURE_VMAX,
        cmap="Spectral",
    )
    plt.scatter(
        rfo_model.input_data.soil_moisture_data.x[time_step],
        rfo_model.input_data.soil_moisture_data.y[time_step],
        c="black",
        s=0.5,
    )
    ax.set_title(time_step)
    ax.set_aspect(1)
    cbar = plt.colorbar(im)
    cbar.ax.tick_params(labelsize=14)

    fig_file_path = os.path.join(
        output_dir,
        "prediction_" + time_step + "_iteration_" + iteration_index + ".png",
    )
    plt.savefig(fig_file_path, dpi=300)
    plt.close()


def plot_predictor_importance(
    rfo_model,
    time_step,
    output_dir: str,
):
    """Plot predictor importance with bar charts and error bars.

    This function plots the predictor importance from the random forest model
    for the specified time step using bar charts with error bars (whiskers) showing
    variability from Monte Carlo iterations. The styling matches the time series
    predictor importance visualization.
    """
    time_index = rfo_model.input_data.soil_moisture_data.time_steps.index(time_step)
    predictor_names = list(rfo_model.input_data.predictors.keys())

    plt.rcParams.update({"font.size": 7})
    fig, ax = plt.subplots(figsize=(16 / 2.54, 7 / 2.54))

    # Create x positions for bars
    x_positions = np.arange(len(predictor_names))

    if (
        rfo_model.parameters.monte_carlo_soil_moisture
        or rfo_model.parameters.monte_carlo_predictors
    ):
        # Calculate mean and standard deviation for each predictor
        importance_data = rfo_model.predictor_importance[:, time_index, :]
        means = np.mean(importance_data, axis=0)
        stds = np.std(importance_data, axis=0)

        # Plot bars with error bars (whiskers) - matching time series style
        ax.bar(
            x_positions,
            means,
            yerr=stds,
            capsize=3,
            alpha=0.7,
            zorder=2,
            color="steelblue",
            edgecolor="darkblue",
            linewidth=0.5,
        )
    else:
        # Single simulation case - no error bars
        means = rfo_model.predictor_importance[0, time_index, :]

        ax.bar(
            x_positions,
            means,
            alpha=0.7,
            color="steelblue",
            edgecolor="darkblue",
            linewidth=0.5,
        )

    # Customize plot to match time series style
    ax.set_ylim(0, 1)
    ax.set_ylabel("Importance")
    ax.set_title(time_step, fontweight="bold")
    ax.grid(True, alpha=0.3, zorder=0)
    ax.set_axisbelow(True)

    # Set x-axis
    ax.set_xticks(x_positions)
    ax.set_xticklabels(predictor_names, rotation=45, ha="right")
    ax.set_xlabel("Predictors")

    plt.tight_layout()
    fig_file_path = os.path.join(output_dir, f"predictor_importance_{time_step}.png")
    plt.savefig(fig_file_path, dpi=300, bbox_inches="tight")
    plt.close()


def predictor_importance_along_days(
    rfo_model,
    output_dir: str,
):
    """
    Plot predictor importance from the RF model along the days with bar charts.

    This function plots the predictor importance from the random forest model
    over the days using bar charts with error bars showing variability from
    Monte Carlo iterations. Background trend lines connect the means.
    The x-axis shows actual time steps, and the y-axis shows importance values.
    """
    number_predictors = len(rfo_model.input_data.predictors)
    time_steps = rfo_model.input_data.soil_moisture_data.time_steps
    predictor_importance = rfo_model.predictor_importance
    predictors = rfo_model.input_data.predictors

    plt.rcParams.update({"font.size": 7})
    fig, ax = plt.subplots(
        number_predictors,
        sharex=True,
        # Slightly wider for better bar visibility
        figsize=(20 / 2.54, 16 / 2.54),
    )

    # Ensure ax is always a list for consistent handling
    if number_predictors == 1:
        ax = [ax]

    for pred_index, predictor_name in enumerate(predictors.keys()):
        # Calculate mean and standard deviation for each day
        means = np.mean(predictor_importance[:, :, pred_index], axis=0)
        stds = np.std(predictor_importance[:, :, pred_index], axis=0)

        # Create x positions for bars (numeric positions)
        x_positions = np.arange(len(time_steps))

        # Plot background trend line (light grey, behind bars)
        ax[pred_index].plot(
            x_positions, means, color="lightgray", alpha=0.6, linewidth=1.5, zorder=1
        )

        # Plot bars with error bars (whiskers)
        ax[pred_index].bar(
            x_positions,
            means,
            yerr=stds,
            capsize=3,
            alpha=0.7,
            zorder=2,
            color="steelblue",
            edgecolor="darkblue",
            linewidth=0.5,
        )

        # Customize subplot
        ax[pred_index].set_ylim(0, 1)
        ax[pred_index].set_ylabel("Importance")
        ax[pred_index].set_title(predictor_name, fontweight="bold")
        ax[pred_index].grid(True, alpha=0.3, zorder=0)
        ax[pred_index].set_axisbelow(True)

        # Set x-axis labels only on the bottom subplot
        if pred_index == number_predictors - 1:
            ax[pred_index].set_xticks(x_positions)
            ax[pred_index].set_xticklabels(time_steps, rotation=45, ha="right")
            ax[pred_index].set_xlabel("Time Steps")
        else:
            ax[pred_index].set_xticks(x_positions)
            ax[pred_index].set_xticklabels([])

    plt.tight_layout()
    fig_file_path = os.path.join(output_dir, "predictor_importance_vs_days.png")
    plt.savefig(fig_file_path, dpi=300, bbox_inches="tight")
    plt.close()


def export_predictor_importance_csv(rfo_model, output_dir: str):
    """
    Export predictor importance over time as CSV file.

    Creates a CSV file containing predictor importance values for each time step
    in long format suitable for DataFrame analysis. Includes error bounds when
    Monte Carlo simulations are enabled.

    Parameters:
    - rfo_model (object): Random forest regression model and results.
    - output_dir (str): Directory path to save the CSV file.
    """
    logging.info("Exporting predictor importance CSV")

    time_steps = rfo_model.input_data.soil_moisture_data.time_steps
    predictor_names = list(rfo_model.input_data.predictors.keys())
    predictor_importance = rfo_model.predictor_importance

    # Check if Monte Carlo is enabled
    monte_carlo_enabled = (
        rfo_model.parameters.monte_carlo_soil_moisture
        or rfo_model.parameters.monte_carlo_predictors
    )

    # Create CSV content
    csv_lines = []

    # Header row
    header = [
        "time_step",
        "predictor",
        "importance",
        "5th_percentile",
        "95th_percentile",
    ]
    csv_lines.append(",".join(header))

    # Data rows
    for time_index, time_step in enumerate(time_steps):
        for pred_index, predictor_name in enumerate(predictor_names):
            if monte_carlo_enabled:
                # Use median and percentiles for Monte Carlo data
                importance_data = predictor_importance[:, time_index, pred_index]
                importance = np.percentile(importance_data, 50)  # median
                lower_error = np.percentile(importance_data, 5)  # 5th percentile
                upper_error = np.percentile(importance_data, 95)  # 95th percentile

                row_data = [
                    str(time_step),
                    str(predictor_name),
                    f"{importance:.3f}",
                    f"{lower_error:.3f}",
                    f"{upper_error:.3f}",
                ]
            else:
                # Single simulation - no error bounds
                importance = predictor_importance[0, time_index, pred_index]

                row_data = [
                    str(time_step),
                    str(predictor_name),
                    f"{importance:.3f}",
                    "",  # Empty lower_error
                    "",  # Empty upper_error
                ]

            csv_lines.append(",".join(row_data))

    # Write CSV file
    csv_file_path = os.path.join(output_dir, "predictor_importance.csv")
    with open(csv_file_path, "w") as f:
        f.write("\n".join(csv_lines))


def export_geotiff_soil_moisture_map(rfo_model, time_step, output_dir: str):
    """Export soil moisture prediction as georeferenced GeoTIFF file.

    Parameters:
    - rfo_model (object): Random forest regression model and results.
    - time_step (str): Time step identifier for which to export the prediction.
    - output_dir (str): Directory path to save the GeoTIFF file.
    """
    logging.info(f"Exporting GeoTIFF prediction map for time step {time_step}")

    # Get geometry and coordinate system info
    geometry = rfo_model.geometry
    projection = rfo_model.parameters.projection
    time_index = rfo_model.input_data.soil_moisture_data.time_steps.index(time_step)

    # Determine which data to use based on Monte Carlo settings
    if (
        rfo_model.parameters.monte_carlo_soil_moisture
        or rfo_model.parameters.monte_carlo_predictors
    ):
        prediction_data = rfo_model.MC_mean[time_index]
    else:
        prediction_data = rfo_model.prediction[0, time_index, :, :]

    # Create transform from geometry bounds
    transform = from_bounds(
        geometry.xi,
        geometry.yi,
        geometry.xf,
        geometry.yf,
        prediction_data.shape[1],  # width
        prediction_data.shape[0],  # height
    )

    # Export raw prediction data as GeoTIFF (no matplotlib rendering)
    geotiff_path = os.path.join(output_dir, f"prediction_{time_step}.tif")
    with rasterio.open(
        geotiff_path,
        "w",
        driver="GTiff",
        height=prediction_data.shape[0],
        width=prediction_data.shape[1],
        count=1,
        dtype=prediction_data.dtype,
        crs=projection,
        transform=transform,
        nodata=None,  # No specific nodata value
    ) as dst:
        # Write raw prediction values directly (no rendering)
        # Transpose and flip upside down to match expected coordinate order
        dst.write(np.flipud(prediction_data.T), 1)


def export_geotiff_predictors_map(rfo_model, time_step, output_dir: str):
    """
    Export individual predictor maps as georeferenced GeoTIFF files.

    Creates properly georeferenced GeoTIFF files for each predictor containing raw data
    values without any matplotlib rendering. Also creates a predictor_scale.json file
    with min/max values for consistent scaling across time steps.

    Parameters:
    - rfo_model (object): Random forest regression model and results.
    - time_step (str): Time step identifier for which to export predictors.
    - output_dir (str): Directory path to save the GeoTIFF files.
    """
    logging.info(f"Exporting GeoTIFF predictor maps for time step {time_step}")

    # Get geometry and coordinate system info
    geometry = rfo_model.geometry
    projection = rfo_model.parameters.projection

    # Create/update geotiff_scale.json file
    scale_file_path = os.path.join(output_dir, SCALE_FILE_NAME)

    # Load existing scale data or create new one
    if os.path.exists(scale_file_path):
        with open(scale_file_path, "r") as f:
            scale_data = json.load(f)
    else:
        scale_data = {}

    # Add predictors scale data (only if not already present)
    for pred_name, pred_data in rfo_model.input_data.predictors.items():
        pred_name = pred_name.replace(" ", "_").replace("/", "_")
        if pred_name not in scale_data:
            all_values = []
            for ts in pred_data.values_on_nodes.keys():
                values = pred_data.values_on_nodes[ts]
                # Exclude NaN values
                all_values.append(values[~np.isnan(values)])

            if all_values:
                global_vmin = float(np.min(np.concatenate(all_values)))
                global_vmax = float(np.max(np.concatenate(all_values)))
            else:
                global_vmin, global_vmax = 0.0, 1.0

            scale_data[pred_name] = [
                global_vmin,
                global_vmax,
                pred_data.information.unit,
            ]

    # Write updated scale data
    with open(scale_file_path, "w") as f:
        json.dump(scale_data, f, indent=2)

    for pred_name, pred_data in rfo_model.input_data.predictors.items():
        if time_step == CONSTANT_TIME_STEP and pred_data.time_steps != [None]:
            continue  # Skip non-constant predictors for constant time step
        if time_step != CONSTANT_TIME_STEP and pred_data.time_steps == [None]:
            continue  # Skip constant predictors for time-varying time step

        safe_pred_name = pred_name.replace(" ", "_").replace("/", "_")
        values_on_nodes = pred_data.values_on_nodes[time_step]

        # Create transform from geometry bounds
        transform = from_bounds(
            geometry.xi,
            geometry.yi,
            geometry.xf,
            geometry.yf,
            values_on_nodes.shape[1],  # width
            values_on_nodes.shape[0],  # height
        )

        # Export raw predictor data as GeoTIFF
        geotiff_path = os.path.join(
            output_dir, f"predictor_{safe_pred_name}_{time_step}.tif"
        )
        with rasterio.open(
            geotiff_path,
            "w",
            driver="GTiff",
            height=values_on_nodes.shape[0],
            width=values_on_nodes.shape[1],
            count=1,
            dtype=values_on_nodes.dtype,
            crs=projection,
            transform=transform,
            nodata=None,
        ) as dst:
            # Write raw predictor values directly
            # Transpose and flip upside down to match expected coordinate order
            dst.write(np.flipud(values_on_nodes.T), 1)


def export_geojson_measurements_map(rfo_model, time_step, output_dir: str):
    """
    Export measurements as GeoJSON file for web mapping applications.

    Creates a GeoJSON file containing measurement points with coordinates
    transformed to EPSG:4326 (WGS84) and soil moisture values as properties.
    Perfect for use with Dash Leaflet and other web mapping libraries.

    Parameters:
    - rfo_model (object): Random forest regression model and results.
    - time_step (str): Time step identifier for which to export measurements.
    - output_dir (str): Directory path to save the GeoJSON file.
    """
    logging.info(f"Exporting GeoJSON measurements map for time step {time_step}")

    soil_moisture_data = rfo_model.input_data.soil_moisture_data
    x = soil_moisture_data.x[time_step]
    y = soil_moisture_data.y[time_step]
    soil_moisture_values = soil_moisture_data.soil_moisture[time_step]

    source_crs = CRS.from_string(str(rfo_model.parameters.projection))
    target_crs = CRS.from_epsg(4326)

    # Transform coordinates
    lon, lat = transform(source_crs, target_crs, x, y)

    # Check for uncertainty data
    has_uncertainty = soil_moisture_data.uncertainty
    uncertainty_low = None
    uncertainty_high = None

    if has_uncertainty:
        uncertainty_low = soil_moisture_data.soil_moisture_dev_low[time_step]
        uncertainty_high = soil_moisture_data.soil_moisture_dev_high[time_step]

    # Create GeoJSON features for each measurement point
    features = []
    for i in range(len(lon)):
        soil_moisture_val = float(soil_moisture_values[i])
        lon_val = float(lon[i])
        lat_val = float(lat[i])

        # Generate color based on soil moisture value using Spectral colormap
        # Normalize soil moisture to 0-1 range for color mapping
        normalized_value = (soil_moisture_val - SOIL_MOISTURE_VMIN) / (
            SOIL_MOISTURE_VMAX - SOIL_MOISTURE_VMIN
        )
        normalized_value = max(0, min(1, normalized_value))  # Clamp to 0-1

        # Convert to Spectral colormap (reversed to match existing usage)
        color_rgba = cm.Spectral_r(normalized_value)
        color_hex = f"#{int(color_rgba[0] * 255):02x}{int(color_rgba[1] * 255):02x}{int(color_rgba[2] * 255):02x}"  # noqa

        # Base properties
        properties = {
            "soil_moisture": soil_moisture_val,
            "time_step": time_step,
            "unit": SOIL_MOISTURE_UNIT,
            "coordinates": [lon_val, lat_val],
            "color": color_hex,
            "fillColor": color_hex,
            "has_uncertainty": has_uncertainty,
        }

        # Add uncertainty information if available
        if has_uncertainty and i < len(uncertainty_low) and i < len(uncertainty_high):
            uncertainty_low_val = float(uncertainty_low[i])
            uncertainty_high_val = float(uncertainty_high[i])

            # Calculate standard deviation (average of low and high deviations)
            std_dev = (abs(uncertainty_low_val) + abs(uncertainty_high_val)) / 2

            # Calculate circle radius based on uncertainty (scale factor for
            # visualization)
            base_radius = 8  # Base radius in pixels
            uncertainty_scale = 20  # Pixels per unit of uncertainty
            radius = base_radius + (std_dev * uncertainty_scale)
            # Clamp radius between 5 and 50 pixels
            radius = max(5, min(radius, 50))

            # Add uncertainty properties
            tooltip = f"Soil Moisture: {soil_moisture_val:.3f} ± {std_dev:.3f} {SOIL_MOISTURE_UNIT}<br>Measurement ID: {i}<br>Date: {time_step}"  # noqa
            popup = f"<b>Measurement Point {i}</b><br>Soil Moisture: {soil_moisture_val:.3f} {SOIL_MOISTURE_UNIT}<br>Uncertainty: -{uncertainty_low_val:.3f} / +{uncertainty_high_val:.3f}<br>Std Dev: ±{std_dev:.3f}<br>Date: {time_step}<br>Coordinates: [{lon_val:.6f}, {lat_val:.6f}]"  # noqa
            properties.update(
                {
                    "uncertainty_low": uncertainty_low_val,
                    "uncertainty_high": uncertainty_high_val,
                    "std_dev": std_dev,
                    "radius": radius,
                    "tooltip": tooltip,
                    "popup": popup,
                }
            )
        else:
            # No uncertainty data
            tooltip = f"Soil Moisture: {soil_moisture_val:.3f} {SOIL_MOISTURE_UNIT}<br>Measurement ID: {i}<br>Date: {time_step}"  # noqa
            popup = f"<b>Measurement Point {i}</b><br>Soil Moisture: {soil_moisture_val:.3f} {SOIL_MOISTURE_UNIT}<br>Date: {time_step}<br>Coordinates: [{lon_val:.6f}, {lat_val:.6f}]"  # noqa
            properties.update(
                {
                    "radius": 8,  # Default radius
                    "tooltip": tooltip,
                    "popup": popup,
                }
            )

        feature = {
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": [lon_val, lat_val]},
            "properties": properties,
        }
        features.append(feature)

    # Create complete GeoJSON structure (EPSG:4326 is default for GeoJSON)
    geojson_data = {
        "type": "FeatureCollection",
        "features": features,
        "crs": {"type": "name", "properties": {"name": "EPSG:4326"}},
    }

    # Export as GeoJSON file
    geojson_path = os.path.join(output_dir, f"measurements_{time_step}.geojson")
    with open(geojson_path, "w") as f:
        json.dump(geojson_data, f, indent=2)


def export_geotiff_prediction_distance_map(rfo_model, time_step, output_dir: str):
    """
    Export prediction distance map as georeferenced GeoTIFF file.

    Creates a properly georeferenced GeoTIFF file containing the raw prediction distance
    data without any matplotlib rendering, axes, padding, or legends.

    Parameters:
    - rfo_model (object): Random forest regression model and results.
    - time_step (str): Time step identifier for which to export prediction distance.
    - output_dir (str): Directory path to save the GeoTIFF file.
    """
    logging.info(f"Exporting GeoTIFF prediction distance map for time step {time_step}")

    # Ensure prediction distance is computed
    if len(rfo_model.input_data.prediction_distance) == 0:
        rfo_model.input_data.compute_prediction_distance()

    prediction_distance_data = rfo_model.input_data.prediction_distance[time_step]

    if prediction_distance_data is None:
        logging.warning(f"No prediction distance data for time step {time_step}")
        return

    # Get geometry and coordinate system info
    geometry = rfo_model.geometry
    projection = rfo_model.parameters.projection

    # Create transform from geometry bounds
    transform = from_bounds(
        geometry.xi,
        geometry.yi,
        geometry.xf,
        geometry.yf,
        prediction_distance_data.shape[1],  # width
        prediction_distance_data.shape[0],  # height
    )

    # Export raw prediction distance data as GeoTIFF
    geotiff_path = os.path.join(output_dir, f"prediction_distance_{time_step}.tif")
    with rasterio.open(
        geotiff_path,
        "w",
        driver="GTiff",
        height=prediction_distance_data.shape[0],
        width=prediction_distance_data.shape[1],
        count=1,
        dtype=prediction_distance_data.dtype,
        crs=projection,
        transform=transform,
        nodata=None,
    ) as dst:
        # Write raw prediction distance values directly
        # Transpose and flip upside down to match expected coordinate order
        dst.write(np.flipud(prediction_distance_data.T), 1)

    # Update geotiff_scale.json with prediction distance scale for this time step
    scale_file_path = os.path.join(output_dir, SCALE_FILE_NAME)

    # Load existing scale data or create new one
    if os.path.exists(scale_file_path):
        with open(scale_file_path, "r") as f:
            scale_data = json.load(f)
    else:
        scale_data = {}

    # Calculate scale for this prediction distance time step
    valid_values = prediction_distance_data[~np.isnan(prediction_distance_data)]
    if len(valid_values) > 0:
        vmin = float(np.min(valid_values))
        vmax = float(np.max(valid_values))
    else:
        vmin, vmax = 0.0, 1.0

    # Add to scale data with timestep-specific key
    scale_data[f"prediction_distance_{time_step}"] = [vmin, vmax, ""]

    # Write updated scale data
    with open(scale_file_path, "w") as f:
        json.dump(scale_data, f, indent=2)

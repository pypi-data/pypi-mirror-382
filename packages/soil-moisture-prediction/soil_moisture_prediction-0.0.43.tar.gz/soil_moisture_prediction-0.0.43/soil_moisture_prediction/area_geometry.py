"""This module contains the geometry classes for the area of interest."""

import logging

import numpy as np


class UnsupportedOperationError(Exception):
    """Exception raised if grid is not built."""

    pass


class RectGeom:
    """
    Rectangular geometry based on 4 corner points and a resolution step.

    Attributes:
    - xi (float): x-coordinate of the lower-left corner.
    - xf (float): x-coordinate of the upper-right corner.
    - yi (float): y-coordinate of the lower-left corner.
    - yf (float): y-coordinate of the upper-right corner.
    - resolution (float): resolution step for the grid.
    - grid_x (numpy.ndarray): 2D grid of x-coordinates.
    - grid_y (numpy.ndarray): 2D grid of y-coordinates.
    - dim_x (int): Number of cells along the x-axis.
    - dim_y (int): Number of cells along the y-axis.
    """

    xi: float
    xf: float
    yi: float
    yf: float
    resolution: float
    grid_x: np.ndarray
    grid_y: np.ndarray
    dim_x: int
    dim_y: int
    no_grid: bool = False

    def __init__(self, xi, xf, yi, yf, resolution, build_grid=True):
        """
        Initialize the geometry based on the 4 corners and the resolution.

        Parameters:
        - geometry_corners (list): List of 5 floats representing the 4 corner
        points (xi, xf, yi, yf) and the resolution step.

        This method initializes the rectangular geometry using the provided corner
        points and resolution step. It calculates the grid of x and y coordinates
        based on the corner points and resolution step. Additionally, it computes
        the dimensions of the grid.
        """
        self.xi = xi
        self.xf = xf
        self.yi = yi
        self.yf = yf
        self.resolution = resolution
        self.no_grid = not build_grid

        logging.debug("Create geometry with corners:")
        logging.debug(f"xi: {self.xi}, xf: {self.xf}, yi: {self.yi}, yf: {self.yf}")

        if build_grid:
            self.grid_x, self.grid_y = np.mgrid[
                self.xi : self.xf + self.resolution : self.resolution,  # noqa E203
                self.yi : self.yf + self.resolution : self.resolution,  # noqa E203
            ]

            if self.grid_x[-1, 0] > self.xf:
                self.xf = self.grid_x[-1, 0]
                logging.warning(
                    f"Adjusted x-coordinate of the upper-right corner to {self.xf}"
                )
            if self.grid_y[0, -1] > self.yf:
                self.yf = self.grid_y[0, -1]
                logging.warning(
                    f"Adjusted y-coordinate of the upper-right corner to {self.yf}"
                )

            self.dim_x = self.grid_x.shape[0]
            self.dim_y = self.grid_x.shape[1]
            logging.debug(f"Grid dimensions: {self.dim_x} x {self.dim_y}")

    def __str__(self):
        """Return a string representation of the geometry."""
        return (
            f"Geometry with: ({self.xi}, {self.xf}, {self.yi}, {self.yf}), "
            f"resolution: {self.resolution}"
        )

    def find_nearest_node(self, x, y):
        """
        Find the nearest node in the grid to the given coordinates.

        Parameters:
        - x (float): The x-coordinate of the point.
        - y (float): The y-coordinate of the point.

        Returns:
        - numpy.ndarray: An array containing the indices of the nearest node
        in the grid.

        This method calculates the indices of the nearest node in the grid to
        the given coordinates (x, y). It first computes the indices of the grid
        cell containing the point using floor division and adjusting for grid
        resolution and origin. The result is returned as a NumPy array with
        shape (2,) representing the row and column indices of the nearest node.
        """
        if self.no_grid:
            raise UnsupportedOperationError("Grid not built for this geometry.")

        idx_x = np.floor((x + self.resolution / 2 - self.xi) / self.resolution).astype(
            int
        )
        idx_y = np.floor((y + self.resolution / 2 - self.yi) / self.resolution).astype(
            int
        )
        return np.column_stack((idx_x, idx_y))

    def contain(self, x, y, margin_multi_resolution=0):
        """Check if a given point is inside this area.

        Parameters:
        - x: x-coordinate of the point.
        - y: y-coordinate of the point.

        Returns:
        - True if the point is inside this area, False otherwise.
        """
        margin = self.resolution * margin_multi_resolution
        return (
            self.xi - margin <= x <= self.xf + margin
            and self.yi - margin <= y <= self.yf + margin
        )

    def expand(self, x, y):
        """Expand the area to include a given point (x, y).

        Parameters:
        - x: x-coordinate of the point to be included in the expanded area.
        - y: y-coordinate of the point to be included in the expanded area.
        """
        self.xi = min(self.xi, x)
        self.xf = max(self.xf, x)
        self.yi = min(self.yi, y)
        self.yf = max(self.yf, y)

    def get_area(self):
        """Return the area of the geometry."""
        return (self.xf - self.xi) * (self.yf - self.yi)

    def get_axis(self):
        """
        Get the axis for plotting.

        Returns:
        - tuple: Tuple containing the x-axis and y-axis values for plotting.
        """
        return (
            self.grid_x,
            self.grid_y,
        )

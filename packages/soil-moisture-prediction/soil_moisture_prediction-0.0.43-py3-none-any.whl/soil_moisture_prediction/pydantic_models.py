"""Pydantic models for the input parameters of the model."""

import logging
from typing import Annotated, Dict, Union

from pydantic import AfterValidator, BaseModel, Field, field_validator
from pyproj import CRS
from pyproj.exceptions import CRSError

logger = logging.getLogger(__name__)


def pprint_pydantic_validation_error(validation_error):
    """Pretty print a Pydantic validation error."""
    errors = validation_error.errors()
    full_message = ""
    for error in errors:
        loc = " -> ".join(map(str, error["loc"]))
        msg = error["msg"]
        error_type = error["type"]
        full_message += f"Error in {loc}: {msg} (type={error_type})\n"

    return full_message


def check_projection_format(v):
    """Check that the projection starts with EPSG.

    If you ever want to include non euclidean coordinate systems, beware of the
    downstream concequences. This includes but is not limited in the time of writing
    DataStreamer.create_size().
    The function is used as a field validator in the InputParameters class and for a
    validator in the html form in the cosmopolitan web service.
    """
    if v is None:
        return v

    if not v.startswith("EPSG"):
        raise ValueError("Projection must start with EPSG")

    try:
        crs = CRS.from_user_input(v)
    except CRSError as e:
        raise ValueError(f"Invalid projection: {e}")

    if not crs.is_projected:
        raise ValueError("CRS must be an euclidean coordinate system")
    return v


class PredictorInformation(BaseModel):
    """Data model for the predictor data."""

    file_path: Union[str, None] = Field(
        default=None,
        description="The path to the csv file with the predictor data.",
    )
    unit: str = Field(
        ..., description="Unit of the predictor (can be an empty string)."
    )
    std_deviation: bool = Field(
        ...,
        description="Whether the csv has an addiational column with the standard deviation. If std_deviation is True and constant is False, the standard deviation will be assumed in the fourth column.",  # noqa
    )
    constant: bool = Field(
        ...,
        description="Whether the csv has no addiational column with the time. If std_deviation is True and constant is False, the standard deviation will be assumed in the fourth coclumn.",  # noqa
    )
    nan_value: str = Field(
        ...,
        description="The value that represents NaN in the csv file (can be an empty string).",  # noqa
    )


class PredictorInformationHeader(PredictorInformation):
    """Data model for the predictor data provide by the header."""

    predictor_name: str = Field(
        ..., description="The name of the predictor (e.g. 'elevation')."
    )


class WhatToPlot(BaseModel):
    """List of which plotting functions should be used."""

    alldays_predictor_importance: bool = Field(
        True,
        description="Whether to plot all predictor importance from the RF model along the days.",  # noqa
    )
    day_measurements: bool = Field(
        True,
        description="Whether to plot the measurements as scatter on a x-y map.",
    )
    day_prediction_map: bool = Field(
        True,
        description="Whether to plot the random forest prediction as a color map.",
    )
    day_predictor_importance: bool = Field(
        True,
        description="Whether to plot the predictor importance from the random forest model.",  # noqa
    )
    pred_correlation: bool = Field(
        True,
        description="Whether to plot the correlation matrix between all predictors, 2 by 2.",  # noqa
    )
    predictors: bool = Field(
        True,
        description="Whether to plot all predictors as color maps",
    )
    prediction_distance: bool = Field(
        True,
        description="Whether to plot the distance between the prediction and the measurements.",  # noqa
    )
    soil_moisture_map_geotiff: bool = Field(
        True,
        description="Whether to export soil moisture prediction maps as georeferenced GeoTIFF files.",  # noqa
    )
    predictor_maps_geotiff: bool = Field(
        True,
        description="Whether to export predictor maps as georeferenced GeoTIFF files.",  # noqa
    )
    predictor_distance_map_geotiff: bool = Field(
        True,
        description="Whether to export predictor distance maps as georeferenced GeoTIFF files.",  # noqa
    )
    measurments_geojson: bool = Field(
        True,
        description="Whether to export measurements as georeferenced GeoJSON files.",  # noqa
    )
    pred_correlation_csv: bool = Field(
        True,
        description="Whether to export correlation matrix as CSV for DataFrame analysis.",  # noqa
    )
    alldays_predictor_importance_csv: bool = Field(
        True,
        description="Whether to export predictor importance over time as CSV for DataFrame analysis.",  # noqa
    )


class InputParameters(BaseModel):
    """Data model for the input parameters."""

    # Geometry
    area_x1: Annotated[
        float,
        Field(
            632612.0,
            description="Defining the left boundrie of the area.",
            title="X1",
            json_schema_extra={"type": "float"},
        ),
    ]
    area_x2: Annotated[
        float,
        Field(
            634112.0,
            description="Defining the right boundrie of the area.",
            title="X2",
            json_schema_extra={"type": "float"},
        ),
    ]
    area_y1: Annotated[
        float,
        Field(
            5739607.0,
            description="Defining the lower boundrie of the area.",
            title="Y1",
            json_schema_extra={"type": "float"},
        ),
    ]
    area_y2: Annotated[
        float,
        Field(
            5741107.0,
            description="Defining the higher boundrie of the area.",
            title="Y2",
            json_schema_extra={"type": "float"},
        ),
    ]
    area_resolution: Annotated[
        float,
        Field(
            250.0,
            description="Defining the resolution of the area.",
            title="Resolution",
            json_schema_extra={"type": "float"},
        ),
    ]
    projection: Annotated[
        str,
        Field(
            "EPSG:25832",
            description="The projection of the bounding box e.g. EPSG:25832",
            title="Projection",
            json_schema_extra={"type": "text"},
        ),
        AfterValidator(check_projection_format),
    ]
    # Input data
    soil_moisture_data: Annotated[
        str,
        Field(
            "",
            description="The path to the soil moisture data.",
            title="Soil moisture data",
            json_schema_extra={"type": "text"},
        ),
    ]
    predictors: Annotated[
        Dict[str, Union[PredictorInformation, None]],
        Field(
            {},
            description=(
                "A dictionary of predictors. Either provide one of the predefined "
                "predictors (e.g. 'corine') with None or provide a predictor "
                "information model."
            ),
            title="predictors",
            json_schema_extra={"type": "text"},
        ),
    ]
    monte_carlo_soil_moisture: Annotated[
        bool,
        Field(
            False,
            description=(
                "Whether to use a Monte Carlo Simulation to predict "
                "uncertainty for soil moisture."
            ),
            title="Monte Carlo Simulation of CRNS Data",
            json_schema_extra={"type": "checkbox"},
        ),
    ]
    monte_carlo_predictors: Annotated[
        bool,
        Field(
            False,
            description=(
                "Whether to use a Monte Carlo Simulation to predict "
                "uncertainty for the predictors."
            ),
            title="Monte Carlo Simulation for Predictors",
            json_schema_extra={"type": "checkbox"},
        ),
    ]
    monte_carlo_iterations: Annotated[
        int,
        Field(
            10,
            ge=9,
            le=1000,
            description="Number of iterations for the Monte Carlo Simulation.",
            title="Monte Carlo Iterations",
            json_schema_extra={"type": "integer"},
        ),
    ]
    allow_nan_in_training: Annotated[
        bool,
        Field(
            False,
            description="Whether to allow NaN values in the training data.",
            title="Allow NaN in Training",
            json_schema_extra={"type": "checkbox"},
        ),
    ]
    predictor_qmc_sampling: Annotated[
        bool,
        Field(
            False,
            description="Whether to use Quasi-Monte Carlo sampling for the predictors.",
            title="Quasi-Monte Carlo Sampling",
            json_schema_extra={"type": "checkbox"},
        ),
    ]
    compute_slope: Annotated[
        bool,
        Field(
            False,
            description="Whether to compute the slope from elevation and use as predictor.",  # noqa
            title="Compute Slope",
            json_schema_extra={"type": "checkbox"},
        ),
    ]
    compute_aspect: Annotated[
        bool,
        Field(
            False,
            description="Whether to compute the aspect from elevation and use as predictor.",  # noqa
            title="Compute Aspect",
            json_schema_extra={"type": "checkbox"},
        ),
    ]
    past_prediction_as_feature: Annotated[
        bool,
        Field(
            False,
            description="Whether to use the past prediction as a feature.",
            title="Past Prediction as Feature",
            json_schema_extra={"type": "checkbox"},
        ),
    ]
    what_to_plot: Annotated[
        WhatToPlot,
        Field(
            WhatToPlot(),
            description="List of which plotting functions should be used.",
            title="What to Plot",
            json_schema_extra={"type": "text"},
        ),
    ]
    save_results: Annotated[
        bool,
        Field(
            False,
            description="Dump random forest model. Reload it and use it for predictions.",  # noqa
            title="Save Results",
            json_schema_extra={"type": "checkbox"},
        ),
    ]
    save_input_data: Annotated[
        bool,
        Field(
            True,
            description="Dump input data. Quicker to reload the data.",
            title="Save Input Data",
            json_schema_extra={"type": "checkbox"},
        ),
    ]

    @field_validator("area_x2")
    @classmethod
    def check_x_bounds(cls, x2, values):
        """Check that x2 is greater than x1."""
        try:
            x1 = values.data["area_x1"]
        except KeyError:
            return x2
        if x2 <= x1:
            raise ValueError(
                f"area_x2 must be greater than area_x1. Got x1={x1}, x2={x2}."
            )
        return x2

    @field_validator("area_y2")
    @classmethod
    def check_y_bounds(cls, y2, values):
        """Check that y2 is greater than y1."""
        try:
            y1 = values.data["area_y1"]
        except KeyError:
            return y2
        if y2 <= y1:
            raise ValueError(
                f"area_y2 must be greater than area_y1. Got y1={y1}, y2={y2}."
            )
        return y2

    @field_validator("area_resolution")
    @classmethod
    def check_resolution(cls, res, values):
        """Check that the resolution is a divisor of the area width and height."""
        try:
            x1, x2 = values.data["area_x1"], values.data["area_x2"]
            y1, y2 = values.data["area_y1"], values.data["area_y2"]
        except KeyError:
            raise ValueError("area_x1, area_x2, area_y1, area_y2 must be set.")

        dx = x2 - x1
        dy = y2 - y1

        if (dx < res * 2) or (dy < res * 2):
            raise ValueError(
                "Resolution must be smaller than half the area width and height."
            )
        return res

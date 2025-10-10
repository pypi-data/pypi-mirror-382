"""Collection of classes to stream data from different sources."""

import logging
from contextlib import contextmanager
from io import BytesIO
from typing import Any, Generator, Tuple, Union

import rasterio
import rasterio.transform
from owslib.util import ServiceException
from owslib.wcs import WebCoverageService
from owslib.wms import WebMapService
from pyproj import CRS, Transformer
from requests.exceptions import (
    ConnectionError,
    HTTPError,
    RequestException,
    Timeout,
    TooManyRedirects,
)

from soil_moisture_prediction.input_file_parser import (
    MARGIN_MULTI_RESOLUTION,
    FileValidationError,
)
from soil_moisture_prediction.pydantic_models import (
    InputParameters,
    PredictorInformationHeader,
)

# Allot of logging is done by imported packages, so we suppress them here
# For debugging purposes, you might want to remove the suppression
logging.getLogger("osgeo").setLevel(logging.ERROR)
logging.getLogger("rasterio").setLevel(logging.ERROR)
logging.getLogger("urllib3").setLevel(logging.ERROR)
logging.getLogger("requests").setLevel(logging.ERROR)
logging.getLogger("wcs201").setLevel(logging.ERROR)

DEG_PER_METER_LAT = 1 / 111320
# TODO Check Nan Values for streams


class DataRetrievalError(Exception):
    """Custom exception for data retrieval errors."""

    pass


@contextmanager
def handle_stream_errors():
    """Context manager to handle errors when streaming data from a service."""
    error_message = None
    try:
        yield
    except ConnectionError as e:
        error_message = f"Connection Error: Failed to establish a connection to the server. Please check your internet connection and the server status. Details: {str(e)}"  # noqa
    except HTTPError as e:
        error_message = f"HTTP Error: The server returned an unsuccessful status code. Please check if the service URL is correct and the server is functioning properly. Status code: {e.response.status_code}"  # noqa
    except Timeout as e:
        error_message = f"Timeout Error: The request to the server timed out. The server might be overloaded or there might be network issues. Details: {str(e)}"  # noqa
    except TooManyRedirects as e:
        error_message = f"Too Many Redirects: The request exceeded the configured number of maximum redirections. Please check the service URL and server configuration. Details: {str(e)}"  # noqa
    except RequestException as e:
        error_message = f"Request Exception: An unexpected error occurred while making the request. Details: {str(e)}"  # noqa
    except ServiceException as e:
        error_message = f"Service Exception: The server returned an error response.\n Details: {str(e)}"  # noqa

    if error_message:
        raise DataRetrievalError(error_message)


class DataStreamer:
    """Base class for all data streams."""

    maximal_bbox: Union[Tuple[float, float, float, float], None]
    name: str
    pre_transformer: Union[Transformer, None]
    post_transformer: Union[Transformer, None]
    epsg_query: str
    information: PredictorInformationHeader
    time_step: Union[str, None]
    # Type for the response can be quite complex. A deeper dive into owslib would be
    # needed
    value_response: Any
    uncertanty_response: Any
    timeout: int = 120

    def __init__(self, input_params: InputParameters) -> None:
        """Initialize the data stream."""
        if input_params.projection is None:
            raise FileValidationError("Projection is not set")

        if input_params.projection == self.epsg_query:
            self.pre_transformer = None
            self.post_transformer = None
        else:
            self.pre_transformer = Transformer.from_crs(
                input_params.projection, self.epsg_query, always_xy=True
            )
            self.post_transformer = Transformer.from_crs(
                self.epsg_query, input_params.projection, always_xy=True
            )

        if not self.input_in_boundray(input_params):
            raise FileValidationError(
                f"Input geometry is not within the bounds of the data source {self.name}"  # noqa
            )

    def __str__(self):
        """Return the name of the data source."""
        return self.name

    def input_in_boundray(
        self,
        input_params: InputParameters,
    ) -> bool:
        """Check if the bounding box is within the limits of the data source."""
        if self.maximal_bbox is None:
            return True

        xmin_input = input_params.area_x1
        xmax_input = input_params.area_x2
        ymin_input = input_params.area_y1
        ymax_input = input_params.area_y2

        xmin_data, xmax_data, ymin_data, ymax_data = self.maximal_bbox

        if self.pre_transformer is not None:
            xmin_input, ymin_input = self.pre_transformer.transform(
                xmin_input, ymin_input
            )
            xmax_input, ymax_input = self.pre_transformer.transform(
                xmax_input, ymax_input
            )

        return (
            xmin_data <= xmin_input <= xmax_data
            and ymin_data <= ymin_input <= ymax_data
            and xmin_data <= xmax_input <= xmax_data
            and ymin_data <= ymax_input <= ymax_data
        )

    def _convert_resolution(self, x, y, resolution, input_epsg, output_epsg):
        crs_input = CRS.from_epsg(input_epsg.split(":")[1])
        crs_output = CRS.from_epsg(output_epsg.split(":")[1])

        input_unit = crs_input.coordinate_system.axis_list[0].unit_name
        output_unit = crs_output.coordinate_system.axis_list[0].unit_name

        if input_unit == output_unit:
            return resolution, resolution

        transformer = Transformer.from_crs(crs_input, crs_output, always_xy=True)
        x_out, y_out = transformer.transform(x, y)

        # We use a small offset to estimate the conversion for latitude/longitude
        delta = 1e-5

        x_offset_in, y_offset_in = transformer.transform(x + delta, y)
        lon_factor = abs(x_offset_in - x_out) / delta

        x_offset_in, y_offset_in = transformer.transform(x, y + delta)
        lat_factor = abs(y_offset_in - y_out) / delta

        return resolution * lon_factor, resolution * lat_factor

    def create_size(
        self,
        input_params: InputParameters,
        margin: float = MARGIN_MULTI_RESOLUTION,
    ) -> Tuple[Tuple[float, float, float, float], int, int]:
        """Create the bounding box and size for the WMS or WCS request."""
        xmin = input_params.area_x1
        ymin = input_params.area_y1
        xmax = input_params.area_x2
        ymax = input_params.area_y2
        resolution = input_params.area_resolution
        x, y = (xmin + xmax) / 2, (ymin + ymax) / 2
        res_x, res_y = self._convert_resolution(
            x, y, resolution, input_params.projection, self.epsg_query
        )

        if self.pre_transformer is not None:
            # Find the biggest rectangle that fits in the bounding box
            xmin_1, ymin_1 = self.pre_transformer.transform(xmin, ymin)
            xmax_1, ymax_1 = self.pre_transformer.transform(xmax, ymax)
            xmin_2, ymax_2 = self.pre_transformer.transform(xmin, ymax)
            xmax_2, ymin_2 = self.pre_transformer.transform(xmax, ymin)

            xmin = min(xmin_1, xmin_2)
            ymin = min(ymin_1, ymin_2)
            xmax = max(xmax_1, xmax_2)
            ymax = max(ymax_1, ymax_2)

        xmin -= margin * res_x
        xmax += margin * res_x
        ymin -= margin * res_y
        ymax += margin * res_y

        if margin == 0:
            width = int((xmax - xmin) / res_x)
            height = int((ymax - ymin) / res_y)
        else:
            width = int((xmax - xmin) / (res_x / margin))
            height = int((ymax - ymin) / (res_y / margin))

        return xmin, ymin, xmax, ymax, width, height, res_x, res_y


class WmsDataStreamer(DataStreamer):
    """Class to stream data from a WMS service."""

    bbox: Tuple[float, float, float, float]
    size: Tuple[int, int]
    rgb_dict: dict

    def __init__(self, input_params: InputParameters) -> None:
        """Initialize the WMS data source."""
        super().__init__(input_params)

        xmin, ymin, xmax, ymax, width, height, _res_x, _res_y = self.create_size(
            input_params
        )
        self.bbox = (xmin, ymin, xmax, ymax)
        self.size = (width, height)

    def stream(
        self,
    ) -> Generator[
        Tuple[float, float, float, Union[float, None], Union[str, None]], None, None
    ]:
        """Stream the data from the source."""
        logging.debug("Reading data")
        value_dataset = rasterio.open(BytesIO(self.value_response.read()))
        red_data = value_dataset.read(1)
        green_data = value_dataset.read(2)
        blue_data = value_dataset.read(3)

        transform = value_dataset.transform

        logging.debug("After reading data")
        for row in range(value_dataset.height):
            for col in range(value_dataset.width):
                rgb = (red_data[row, col], green_data[row, col], blue_data[row, col])
                value = self.rgb_dict[rgb]

                if value is None:
                    continue

                x, y = rasterio.transform.xy(transform, row, col)
                if self.post_transformer is not None:
                    x, y = self.post_transformer.transform(x, y)

                yield x, y, value, self.uncertainty, self.time_step


class WcsDataStreamer(DataStreamer):
    """Class to stream data from a WCS service."""

    subsets: Tuple[Tuple[str, float, float], Tuple[str, float, float]]

    def __init__(self, input_params: InputParameters, no_margin=False) -> None:
        """Initialize the WCS data source."""
        super().__init__(input_params)

        if no_margin:
            xmin, ymin, xmax, ymax, _width, _height, _res_x, _res_y = self.create_size(
                input_params,
                margin=0,
            )
        else:
            xmin, ymin, xmax, ymax, _width, _height, _res_x, _res_y = self.create_size(
                input_params
            )

        self.subsets = [("X", xmin, xmax), ("Y", ymin, ymax)]

    def stream(
        self,
        conversion_factor: float = 1,
        nan_value: Union[float, None] = None,
    ) -> Generator[
        Tuple[float, float, float, Union[float, None], Union[str, None]], None, None
    ]:
        """Stream the data from the source."""
        logging.debug("Reading data")
        value_dataset = rasterio.open(BytesIO(self.value_response.read()))
        value_data = value_dataset.read(1)
        transform = value_dataset.transform

        if self.uncertainty_response is not None:
            uncertainty_dataset = rasterio.open(
                BytesIO(self.uncertainty_response.read())
            )
            uncertainty_data = uncertainty_dataset.read(1)

        logging.debug("After reading data")
        for row in range(value_dataset.height):
            for col in range(value_dataset.width):
                if value_data[row, col] == nan_value:
                    continue
                value = value_data[row, col] * conversion_factor

                x, y = rasterio.transform.xy(transform, row, col)
                if self.post_transformer is not None:
                    x, y = self.post_transformer.transform(x, y)

                if self.uncertainty_response is not None:
                    uncertainty = uncertainty_data[row, col] * conversion_factor
                else:
                    uncertainty = None

                yield x, y, value, uncertainty, self.time_step


class CorineData(WmsDataStreamer):
    """Class to stream data from the CORINE WMS service."""

    layer = "clc5"
    information = PredictorInformationHeader(
        predictor_name="CORINE",
        file_path=None,
        unit="",
        std_deviation=False,
        constant=True,
        nan_value="",
    )
    name = "CORINE"
    epsg_query = "EPSG:4326"
    maximal_bbox = (
        5.56125,
        15.57856,
        47.14122,
        55.09936,
    )
    rgb_dict = {
        (230, 0, 77): 1,
        (255, 0, 0): 2,
        (204, 77, 242): 3,
        (204, 0, 0): 4,
        (230, 204, 204): 5,
        (230, 204, 230): 6,
        (166, 0, 204): 7,
        (166, 77, 0): 8,
        (255, 77, 255): 9,
        (255, 166, 255): 10,
        (255, 230, 255): 11,
        (255, 255, 168): 12,
        (255, 255, 0): 13,
        (230, 230, 0): 14,
        (230, 128, 0): 15,
        (242, 166, 77): 16,
        (230, 166, 0): 17,
        (230, 230, 77): 18,
        (255, 230, 166): 19,
        (255, 230, 77): 20,
        (230, 204, 77): 21,
        (242, 204, 166): 22,
        (128, 255, 0): 23,
        (0, 166, 0): 24,
        (77, 255, 0): 25,
        (204, 242, 77): 26,
        (166, 255, 128): 27,
        (166, 230, 77): 28,
        (166, 242, 0): 29,
        (230, 230, 230): 30,
        (204, 204, 204): 31,
        (204, 255, 204): 32,
        (0, 0, 0): 33,
        (166, 230, 204): 34,
        (166, 166, 255): 35,
        (77, 77, 255): 36,
        (204, 204, 255): 37,
        (230, 230, 255): 38,
        (166, 166, 230): 39,
        (0, 204, 242): 40,
        (128, 242, 230): 41,
        (0, 255, 166): 42,
        (166, 255, 230): 43,
        (230, 242, 255): 44,
    }
    time_step = None
    uncertainty_response = None

    def __init__(self, _predictor_name: str, input_params: InputParameters) -> None:
        """Initialize the CORINE data source.

        Predictor name is not used, but is used as arg for compatibility with other
        data sources.
        """
        super().__init__(input_params)

        self.information = PredictorInformationHeader(
            predictor_name="corine",
            file_path=None,
            unit="",
            std_deviation=False,
            constant=True,
            nan_value="",
        )

    def stream(
        self,
    ) -> Generator[
        Tuple[float, float, float, Union[float, None], Union[str, None]], None, None
    ]:
        """
        Class method that yields (x, y, value) tuples from the CORINE WMS service.

        :param input_params: The input parameters of the model. The geometry and
        projection are used to query the WMS service.
        :return: A generator that yields tuples of (x, y, value), where x and y are the
        coordinates, and value is the raster value.
        """
        logging.debug(f"Streaming {self.name} data")

        logging.debug("Before request to WMS service")
        logging.debug(f"bbox: {self.bbox}")
        logging.debug(f"size: {self.size}")
        with handle_stream_errors():
            wms = WebMapService(
                "https://sgx.geodatenzentrum.de/wms_clc5_2018",
                version="1.3.0",
                timeout=self.timeout,
            )

            self.value_response = wms.getmap(
                layers=[self.layer],
                srs=self.epsg_query,
                bbox=self.bbox,
                size=self.size,
                format="image/tiff",
            )

        logging.debug("After request to WMS service")
        yield from super().stream()


class SoilGridsData(WcsDataStreamer):
    """Class to stream data from the SoilGrids WCS service."""

    wcs_url_template = "http://maps.isric.org/mapserv?map=/map/{}.map"
    soil_properties = {
        "bdod": {
            "Description": "Bulk density of the fine earth fraction",
            "Mapped units": "cg/cm³",
            "Conversion factor": 100,
            "Conventional units": "kg/dm³",
        },
        "cec": {
            "Description": "Cation Exchange Capacity of the soil",
            "Mapped units": "mmol(c)/kg",
            "Conversion factor": 10,
            "Conventional units": "cmol(c)/kg",
        },
        "cfvo": {
            "Description": "Volumetric fraction of coarse fragments (> 2 mm)",
            "Mapped units": "cm3/dm3 (vol‰)",
            "Conversion factor": 10,
            "Conventional units": "cm3/100cm3 (vol%)",
        },
        "clay": {
            "Description": "Proportion of clay particles (< 0.002 mm) in the fine earth fraction",  # noqa
            "Mapped units": "g/kg",
            "Conversion factor": 10,
            "Conventional units": "g/100g (%)",
        },
        "nitrogen": {
            "Description": "Total nitrogen (N)",
            "Mapped units": "cg/kg",
            "Conversion factor": 100,
            "Conventional units": "g/kg",
        },
        "phh2o": {
            "Description": "Soil pH",
            "Mapped units": "pHx10",
            "Conversion factor": 10,
            "Conventional units": "pH",
        },
        "sand": {
            "Description": "Proportion of sand particles (> 0.05/0.063 mm) in the fine earth fraction",  # noqa
            "Mapped units": "g/kg",
            "Conversion factor": 10,
            "Conventional units": "g/100g (%)",
        },
        "silt": {
            "Description": "Proportion of silt particles (≥ 0.002 mm and ≤ 0.05/0.063 mm) in the fine earth fraction",  # noqa
            "Mapped units": "g/kg",
            "Conversion factor": 10,
            "Conventional units": "g/100g (%)",
        },
        "soc": {
            "Description": "Soil organic carbon content in the fine earth fraction",
            "Mapped units": "dg/kg",
            "Conversion factor": 10,
            "Conventional units": "g/kg",
        },
        "ocd": {
            "Description": "Organic carbon density",
            "Mapped units": "hg/m³",
            "Conversion factor": 10,
            "Conventional units": "kg/m³",
        },
        "ocs": {
            "Description": "Organic carbon stocks",
            "Mapped units": "t/ha",
            "Conversion factor": 10,
            "Conventional units": "kg/m²",
        },
    }
    epsg_query = "EPSG:4326"
    name = "SoilGrids"
    maximal_bbox = None
    time_step = None

    identifier: list
    wcs: WebCoverageService
    property_id: str
    property_type: str

    def __init__(
        self, property_id: str, input_params: InputParameters, no_margin=False
    ) -> None:
        """Initialize the SoilGrids data source."""
        if property_id.split("_")[0] not in self.soil_properties:
            raise ValueError(f"Property {property_id} not in SoilGrids data")
        super().__init__(input_params, no_margin=no_margin)

        self.property_id = property_id
        self.property_type = property_id.split("_")[0]

        self.information = PredictorInformationHeader(
            predictor_name=property_id,
            file_path=None,
            unit=self.soil_properties[self.property_type]["Conventional units"],
            std_deviation=input_params.monte_carlo_predictors,
            constant=True,
            nan_value="",
        )

    def __str__(self):
        """Return the name of the data source."""
        return "SoilGrids data"

    @classmethod
    def class_info(cls, property_id):
        """Return the information of the data source."""
        property_type = property_id.split("_")[0]
        return (
            f"{cls.soil_properties[property_type]['Description']}\n"
            "Soil property data provided by SoilGrids\n"
            "The data is available for the whole world.\n"
            "The resolution of the data is 250m x 250m.\n"
            f"Measured in a depth of {property_id.split('_')[1]}\n"
        )

    def info(self):
        """Return the information of the data source."""
        return (
            f"{self.soil_properties[self.property_type]['Description']}\n"
            "Soil property data provided by SoilGrids\n"
            "The data is available for the whole world.\n"
            "The resolution of the data is 250m x 250m.\n"
            f"Measured in a depth of {self.property_id.split('_')[1]}\n"
        )

    def stream(
        self,
    ) -> Generator[
        Tuple[float, float, float, Union[float, None], Union[str, None]], None, None
    ]:
        """Stream the SoilGrids data from the WCS service."""
        conversion_factor = self.soil_properties[self.property_type][
            "Conversion factor"
        ]
        nan_value = 0

        with handle_stream_errors():
            wcs = WebCoverageService(
                self.wcs_url_template.format(self.property_type),
                version="2.0.1",
                timeout=self.timeout,
            )

            self.value_response = wcs.getCoverage(
                identifier=[f"{self.property_id}_mean"],
                crs=self.epsg_query,
                subsets=self.subsets,
                subsettingcrs=self.epsg_query,
                format="image/tiff",
            )

        if self.information.std_deviation:
            with handle_stream_errors():
                self.uncertainty_response = wcs.getCoverage(
                    identifier=[f"{self.property_id}_uncertainty"],
                    crs=self.epsg_query,
                    subsets=self.subsets,
                    subsettingcrs=self.epsg_query,
                    format="image/tiff",
                )
        else:
            self.uncertainty_response = None

        yield from super().stream(
            conversion_factor=conversion_factor, nan_value=nan_value
        )


class BkgElevationData(WcsDataStreamer):
    """Class to stream elevation data from the BKG WMS service."""

    information = PredictorInformationHeader(
        predictor_name="elevation",
        file_path=None,
        unit="m",
        std_deviation=False,
        constant=True,
        nan_value="",
    )
    name = "BKG Elevation"
    epsg_query: str = "EPSG:25832"
    maximal_bbox = (
        279300.0,
        921300.0,
        5235700.0,
        6101900.0,
    )
    uncertainty_response = None
    time_step = None

    def __init__(self, _predictor_name: str, input_params: InputParameters) -> None:
        """Initialize the Elevation data source.

        Predictor name is not used, but is used as arg for compatibility with other
        data sources
        """
        super().__init__(input_params)
        self.subsets = [
            ("E", self.subsets[0][1], self.subsets[0][2]),
            ("N", self.subsets[1][1], self.subsets[1][2]),
        ]

    def __str__(self):
        """Return the name of the data source."""
        return "BKG Elevation data"

    @classmethod
    def class_info(cls, _property_id):
        """Return the information of the data source."""
        transformer = Transformer.from_crs(cls.epsg_query, "EPSG:4326", always_xy=True)
        lon_min, lat_min = transformer.transform(
            cls.maximal_bbox[0], cls.maximal_bbox[2]
        )
        lon_max, lat_max = transformer.transform(
            cls.maximal_bbox[1], cls.maximal_bbox[3]
        )

        return (
            "Elevation data provided by the Bundes Amtes für Kartographie und Geodäsie (BKG)\n"  # noqa
            "The resolution of the data is 200m x 200m.\n"
            "The covered area is defined by the bounding box:\n"
            f"Latitude: {lat_min} to {lat_max}\n"
            f"Longitude: {lon_min} to {lon_max}\n"
        )

    def info(self):
        """Return the information of the data source."""
        transformer = Transformer.from_crs(self.epsg_query, "EPSG:4326", always_xy=True)
        lon_min, lat_min = transformer.transform(
            self.maximal_bbox[0], self.maximal_bbox[2]
        )
        lon_max, lat_max = transformer.transform(
            self.maximal_bbox[1], self.maximal_bbox[3]
        )

        return (
            "Elevation data provided by the Bundes Amtes für Kartographie und Geodäsie (BKG)\n"  # noqa
            "The resolution of the data is 200m x 200m.\n"
            "The covered area is defined by the bounding box:\n"
            f"Latitude: {lat_min} to {lat_max}\n"
            f"Longitude: {lon_min} to {lon_max}\n"
        )

    def stream(
        self,
    ) -> Generator[
        Tuple[float, float, float, Union[float, None], Union[str, None]], None, None
    ]:
        """Stream the elevation data from the WCS service."""
        with handle_stream_errors():
            wcs = WebCoverageService(
                "https://sgx.geodatenzentrum.de/wcs_dgm200_inspire", version="2.0.1"
            )

            self.value_response = wcs.getCoverage(
                identifier=["dgm200_inspire__EL.GridCoverage"],
                crs=self.epsg_query,
                subsets=self.subsets,
                subsettingcrs=self.epsg_query,
                format="image/tiff",
                timeout=self.timeout,
            )

        yield from super().stream()

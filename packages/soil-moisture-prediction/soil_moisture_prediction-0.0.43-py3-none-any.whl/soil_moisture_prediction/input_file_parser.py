"""This module provides classes for parsing input files."""

import csv
import json
import logging
import math
import re
from typing import Set, Union

from pydantic import ValidationError

from soil_moisture_prediction.area_geometry import RectGeom
from soil_moisture_prediction.pydantic_models import (
    PredictorInformationHeader,
    pprint_pydantic_validation_error,
)

# A margin of 5 times the resolution is used to check if a point is inside the area.
MARGIN_MULTI_RESOLUTION = 4
# The character used to indicate a comment line in the input file.
COMMENT_CHAR = "#"


class FileValidationError(Exception):
    """Exception raised when a file validation fails."""

    pass


class InputFileParser:
    """This abstract base class defines the common methods for parsing an input file."""

    def __init__(self, geom_area):
        """Set parse_geom_area so that every point added expands area."""
        self.input_geom_area = geom_area
        self.parse_geom_area = RectGeom(
            float("inf"), -float("inf"), float("inf"), -float("inf"), 0, False
        )

    def _check_time_step(self, cell, row, row_index):
        return cell

    def _check_first_line(self):
        raise NotImplementedError("This method should be implemented in child class.")

    def _check_row(self):
        raise NotImplementedError("This method should be implemented in child class.")

    def get_file_information(self):
        """Return the information about the file."""
        raise NotImplementedError("This method should be implemented in child class.")

    def _check_validty_area(self):
        raise NotImplementedError("This method should be implemented in child class.")

    def _check_coordinate(self, cell, row, row_index):
        try:
            coor = float(cell)
        except ValueError:
            raise FileValidationError(
                f"Cell ''{cell}'' is not a decimal number."
                f"Row number {row_index} '{','.join(row)}'."
            )
        return coor

    def parse(self, in_file_stream):
        """Parse, validate and yield rows of the input file.

        Rows are yielded if they contained in the RectGeom.
        Raises FileValidationError if the file is not valid.
        """
        in_file_stream.seek(0)
        # Guess the delimiter
        sniffer = csv.Sniffer()

        # Get first line with no comment char
        line = ""
        while line == "":
            try:
                line = in_file_stream.readline()
            except UnicodeDecodeError:
                raise FileValidationError("File is not a UTF-8 file.")

            if line[0] == COMMENT_CHAR:
                line = ""

        try:
            dialect = sniffer.sniff(line)
        except csv.Error as e:
            if str(e) == "Could not determine delimiter":
                raise FileValidationError(str(e))
        in_file_stream.seek(0)

        csv_reader = csv.reader(in_file_stream, dialect=dialect)

        first_line = next(csv_reader)

        row = self._check_first_line(first_line, dialect.delimiter)
        if row:
            yield row

        for row_index, row in enumerate(csv_reader, start=2):
            row = self._check_row(row, row_index)
            if row:
                yield row

        self._check_validty_area()


class PredictorParser(InputFileParser):
    """
    Parses an input file containing predictor data.

    This class extends InputFileParser and provides specific functionality for
    validation of predictor data. At the end, a global check is performed so
    that the predictor file must cover the input GeomArea completely, including
    a margin.

    Methods:
        parse(file_path, out_file_path):
            Parses the input file and writes valid predictor data to
            the output file.

    Attributes:
        file_information (dict):
            Information about the file contents (type, unit, std_deviation).
    """

    information: Union[None, PredictorInformationHeader]
    percentage: float

    def __init__(
        self,
        geom_area: RectGeom,
        information: Union[None, PredictorInformationHeader] = None,
    ):
        """Set uncertainty flag."""
        super().__init__(geom_area)
        self.information = information
        if self.information is not None:
            self.information.file_path = None

    def _check_first_line(self, comments, delimiter):
        comment_line = delimiter.join(comments)
        if not comments[0][0] == "#":
            if self.information is None:
                raise FileValidationError(
                    f"First line '{comment_line}' is not a comment line."
                )
            row = self._check_row(comments, 1)
        else:
            json_regex = r"(\{.*\})"
            match = re.search(json_regex, comment_line)
            if match is None:
                raise FileValidationError(
                    f"Comment line '{comment_line}' is not a valid JSON string."
                )
            json_string = match.group(1)
            try:
                information_from_header = PredictorInformationHeader(
                    **json.loads(json_string)
                )
            except json.JSONDecodeError:
                raise FileValidationError(
                    f"Comment line '{comment_line}' is not a valid JSON string."
                )
            except ValidationError as validation_error:
                validation_message = pprint_pydantic_validation_error(validation_error)
                raise FileValidationError(
                    f"Predictor information in comment line doesn`t match the schema.\n"
                    f"{validation_message}"
                )

            if self.information:
                if information_from_header != self.information:
                    raise FileValidationError(
                        f"Information from comment line '{information_from_header}' "
                        f"does not match the expected information '{self.information}'."
                    )
            else:
                self.information = information_from_header

            row = comment_line

        return row

    def _check_row_length(self, row, row_index):
        row_length = 3
        if self.information.std_deviation:
            row_length += 1
        if not self.information.constant:
            row_length += 1

        if len(row) != row_length:
            raise FileValidationError(
                f"Row number {row_index} '{','.join(row)}' has not correct number "
                f"of columns {row_length}."
            )

    def _check_predictor(self, cell, row, row_index):
        try:
            if cell == self.information.nan_value:
                predictor = None
            else:
                predictor = float(cell)
                if math.isnan(predictor):
                    raise ValueError
        except ValueError:
            raise FileValidationError(
                f"Cell '{cell}' is not a decimal number. "
                f"Row number {row_index} '{','.join(row)}'."
            )

        return predictor

    def _check_row(self, row, row_index):
        self._check_row_length(row, row_index)
        x = self._check_coordinate(row[0], row, row_index)
        y = self._check_coordinate(row[1], row, row_index)
        value = self._check_predictor(row[2], row, row_index)
        if self.information.std_deviation:
            std_deviation = self._check_predictor(row[3], row, row_index)
        else:
            std_deviation = None

        if self.information.constant:
            time_step = None
        else:
            column_index = 4 if self.information.std_deviation else 3
            time_step = self._check_time_step(row[column_index], row, row_index)

        if value is not None and (
            self.input_geom_area.contain(
                x, y, margin_multi_resolution=MARGIN_MULTI_RESOLUTION
            )
        ):
            self.parse_geom_area.expand(x, y)
            return x, y, value, std_deviation, time_step

    def get_file_information(self):
        """Return the information about the predictor file."""
        file_information = self.information.model_dump()
        file_information["coverage"] = self.percentage
        return file_information

    def _check_validty_area(self):
        area_input = self.input_geom_area.get_area()
        area_file = self.parse_geom_area.get_area()
        self.percentage = (area_file / area_input) * 100
        if self.percentage < 50:
            logging.warning(
                f"Predictor file covers only {self.percentage:.2f}% of the input area."
            )
        else:
            logging.info(
                f"Predictor file covers {self.percentage:.2f}% of the input area."
            )


class SoilMoistureParser(InputFileParser):
    """Parser for soil moisture data."""

    time_steps: Set
    data_points: int
    row_length: Union[None, int]

    def __init__(self, geom_area: RectGeom):
        """Set uncertainty flag."""
        super().__init__(geom_area)
        self.time_steps = set()
        self.data_points = 0
        self.row_length = None

    def _check_first_line(self, headers, delimiter):
        del delimiter
        if len(headers) not in [4, 6]:
            raise FileValidationError(
                f"Row number {1} '{','.join(headers)}' has not correct number "
                f"of columns 4 or 6."
            )
        self.row_length = len(headers)

        try:
            return self._check_row(headers, 1)
        except FileValidationError:
            return None

    def _check_row_length(self, row, row_index):
        if len(row) != self.row_length:
            raise FileValidationError(
                f"Row number {row_index} '{','.join(row)}' has not correct number "
                f"of columns {self.row_length}."
            )

    def _check_soil_moisture(self, cell, row, row_index, negativ):
        min_soil_moisture = 0
        max_soil_moisture = 1

        try:
            if negativ:
                soil_moisture = abs(float(cell))
            else:
                soil_moisture = float(cell)
        except ValueError:
            raise FileValidationError(
                f"Cell '{cell}' is not a decimal number. "
                f"Row number {row_index} '{','.join(row)}'."
            )
        if soil_moisture < min_soil_moisture or soil_moisture >= max_soil_moisture:
            raise FileValidationError(
                f"Cell '{cell}' needs to be between {min_soil_moisture} and "
                f"{max_soil_moisture}. "
                f"Row number {row_index} '{','.join(row)}'."
            )

        return soil_moisture

    def _check_row(self, row, row_index):
        self._check_row_length(row, row_index)
        x = self._check_coordinate(row[0], row, row_index)
        y = self._check_coordinate(row[1], row, row_index)
        time_step = self._check_time_step(row[2], row, row_index)

        if self.row_length == 6:
            soil_moisture = self._check_soil_moisture(row[3], row, row_index, False)
            err_low = self._check_soil_moisture(row[4], row, row_index, True)
            err_high = self._check_soil_moisture(row[5], row, row_index, False)
        else:
            soil_moisture = self._check_soil_moisture(row[3], row, row_index, True)
            err_low = None
            err_high = None

        if self.input_geom_area.contain(x, y):
            self.parse_geom_area.expand(x, y)
            self.time_steps.add(time_step)
            self.data_points += 1
            return x, y, time_step, soil_moisture, err_low, err_high

    def get_file_information(self):
        """Return the time steps in the soil moisture file."""
        file_information = {
            "time_steps": list(self.time_steps),
            "num_data_points": self.data_points,
        }
        return file_information

    def _check_validty_area(self):
        if self.data_points == 0:
            raise FileValidationError(
                "No CRN measurments are in the user defined area!"
            )

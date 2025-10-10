"""Command line module for soil moisture prediction."""

import argparse
import json
import logging
import os
import sys
import time
import traceback
from json.decoder import JSONDecodeError

from pydantic import ValidationError

from soil_moisture_prediction.__version__ import __version__
from soil_moisture_prediction.input_file_parser import FileValidationError
from soil_moisture_prediction.pydantic_models import (
    InputParameters,
    pprint_pydantic_validation_error,
)
from soil_moisture_prediction.random_forest_model import RFoModel
from soil_moisture_prediction.streams import DataRetrievalError

parser = argparse.ArgumentParser()
parser.add_argument(
    "-w", "--work_dir", type=str, required=True, help="Working directory"
)
parser.add_argument("--use_dump", action="store_true", help="Use dump files")
parser.add_argument(
    "-v",
    "--verbosity",
    choices=["quiet", "verbose", "debug"],
    default="verbose",
    help="Verbosity level (quiet, verbose [default], debug)",
)
parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")


def main(verbosity=None, work_dir=None, use_dump=False):
    """Run the soil moisture prediction module."""
    if verbosity is None or work_dir is None:
        args = parser.parse_args()
        verbosity = args.verbosity
        work_dir = args.work_dir
        use_dump = args.use_dump

    # Convert string choice to corresponding numeric level
    verbosity_levels = {"quiet": 30, "verbose": 20, "debug": 10}
    selected_verbosity = verbosity_levels[verbosity]

    logging.basicConfig(format="%(asctime)s - %(message)s", level=selected_verbosity)

    # Suppress matplotlib logging
    matplotlib_logger = logging.getLogger("matplotlib")
    matplotlib_logger.setLevel(logging.CRITICAL)

    logging.info(f"Running soil moisture prediction version {__version__}")

    if not os.path.isfile(os.path.join(work_dir, "parameters.json")):
        logging.error("Abborting! Input parameters file does not exist:")
        logging.error(os.path.join(work_dir, "parameters.json"))
        return None

    try:
        with open(os.path.join(work_dir, "parameters.json"), "r") as f_handle:
            file_content = f_handle.read()
            input_parameters = InputParameters(**json.loads(file_content))

        logging.debug("Input parameters:")
        logging.debug(json.dumps(input_parameters.model_dump(), indent=4))

        start_time = time.time()
        rfo_model = RFoModel(input_parameters=input_parameters, work_dir=work_dir)
        rfo_model.load_input_data(load_from_dump=use_dump)
        rfo_model.complete_prediction()
    except ValidationError as validation_error:
        validation_message = pprint_pydantic_validation_error(validation_error)
        logging.error(f"Abborting: Invalid input parameters\n{validation_message}")
        return None
    except JSONDecodeError:
        logging.error("Abborting! Input parameters file is not a valid JSON file")
        return None
    except FileValidationError as file_validation_error:
        logging.error("Abborting due to file validation error")
        logging.error(file_validation_error)
        return None
    except DataRetrievalError as data_retrieval_error:
        logging.error("Abborting! Could not retrieve data")
        logging.error(data_retrieval_error)
        return None

    end_time = time.time()
    execution_time = end_time - start_time
    logging.info("Execution time: %.2f seconds", execution_time)

    with open(os.path.join(work_dir, "smp_version.txt"), "w") as version_file:
        version_file.write(__version__)

    return rfo_model


def cli():
    """Run the soil moisture prediction module."""
    try:
        return_value = main()
    except KeyboardInterrupt:
        logging.error("Aborted by user")
        sys.exit(1)
    except Exception:  # noqa
        logging.error("An error occurred")
        logging.error(traceback.format_exc())
        sys.exit(1)

    if return_value is None:
        sys.exit(1)

    sys.exit(0)


if __name__ == "__main__":
    cli()

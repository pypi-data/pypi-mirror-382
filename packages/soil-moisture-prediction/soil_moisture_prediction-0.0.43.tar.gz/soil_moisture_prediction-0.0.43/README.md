# SOIL MOISTURE PREDICTION

## Description
This script performs soil moisture prediction using a Random Forest model based on soil properties. Additionally, it allows for incorporating soil moisture uncertainty in the input file and performs a probabilistic prediction using a Monte Carlo approach.

## Usage

The package provides a command line interface `smp_cli` to run the prediction. 

The cli-tool takes the path to a directory containing a JSON file with input parameters. The input files can be put in the same directory as the parameters file or must be given as an absolute path.

## Directory structure
This is an example of this directory structure:

```
soil_moisture_prediction/test_data/
├── crn_soil-moisture.csv
├── parameters.json
├── predictor_1.csv
├── predictor_2.csv
├── predictor_3.csv
└── predictor_4.csv
```

## Input parameters
The parameters.json file in this example directory contains the following content:

```
$ cat soil_moisture_prediction/test_data/parameters.json
{
  "geometry": [
    632612,
    634112,
    5739607,
    5741107,
    250
  ],
  "projection": "EPSG:25832",
  "predictors": {
    "elevation": {
      "file_path": "predictor_1.csv",
      "unit": "m",
      "std_deviation": true,
      "constant": true,
      "nan_value": ""
    },
    "variable predictor": {
      "file_path": "predictor_2.csv",
      "unit": "u",
      "std_deviation": true,
      "constant": false,
      "nan_value": "0.0"
    },
    "pred_3": {
      "file_path": "predictor_3.csv",
      "unit": "u",
      "std_deviation": true,
      "constant": true,
      "nan_value": ""
    },
    "pred_4": {
      "file_path": "predictor_4.csv",
      "unit": "u",
      "std_deviation": true,
      "constant": true,
      "nan_value": "NaN"
    }
  },
  "soil_moisture_data": "crn_soil-moisture.csv",
  "monte_carlo_soil_moisture": true,
  "monte_carlo_predictors": true,
  "monte_carlo_iterations": 10,
  "predictor_qmc_sampling": false,
  "compute_slope": true,
  "compute_aspect": true,
  "past_prediction_as_feature": true,
  "reset_when_rain_occured": false,
  "allow_nan_in_training": false,
  "what_to_plot": {
    "predictors": true,
    "prediction_distance": true,
    "pred_correlation": true,
    "day_measurements": true,
    "day_predictor_importance": true,
    "day_prediction_map": true,
    "alldays_predictor_importance": true,
    "geotiff_export": true
  },
  "save_results": false,
  "save_input_data": false
}
```

## Input data
There are two ways to provide predictor data. Either by providing a file path or by providing a specific key for one of the following predictor sources. If a key is used, the information in the parameters.json file must be 'null'. For each predictor key an external source is used to retrieve the data for the selected geometry.

If for ["predictors"][pred_key]["file_path"] and ["soil_moisture_data"] a file path is given, the file is assumed to be in the same directory as the parameters.json file.

The predictor keys are:

 * elevation_bkg: Elevation data provided by the Bundes Amtes für Kartographie und Geodäsie (BKG)
   The resolution of the data is 200m x 200m.
   The covered area is defined by the bounding box:
   Latitude: 47.23766056897108 to 54.88593008642519
   Longitude: 6.083977454450403 to 15.57232578151963
   
 * bdod_x-ycm: Bulk density of the fine earth fraction
   Soil property data provided by SoilGrids
   The data is available for the whole world.
   The resolution of the data is 250m x 250m.
   Measured in a depth of x-ycm
   
 * cec_x-ycm: Cation Exchange Capacity of the soil
   Soil property data provided by SoilGrids
   The data is available for the whole world.
   The resolution of the data is 250m x 250m.
   Measured in a depth of x-ycm
   
 * cfvo_x-ycm: Volumetric fraction of coarse fragments (> 2 mm)
   Soil property data provided by SoilGrids
   The data is available for the whole world.
   The resolution of the data is 250m x 250m.
   Measured in a depth of x-ycm
   
 * clay_x-ycm: Proportion of clay particles (< 0.002 mm) in the fine earth fraction
   Soil property data provided by SoilGrids
   The data is available for the whole world.
   The resolution of the data is 250m x 250m.
   Measured in a depth of x-ycm
   
 * nitrogen_x-ycm: Total nitrogen (N)
   Soil property data provided by SoilGrids
   The data is available for the whole world.
   The resolution of the data is 250m x 250m.
   Measured in a depth of x-ycm
   
 * phh2o_x-ycm: Soil pH
   Soil property data provided by SoilGrids
   The data is available for the whole world.
   The resolution of the data is 250m x 250m.
   Measured in a depth of x-ycm
   
 * sand_x-ycm: Proportion of sand particles (> 0.05/0.063 mm) in the fine earth fraction
   Soil property data provided by SoilGrids
   The data is available for the whole world.
   The resolution of the data is 250m x 250m.
   Measured in a depth of x-ycm
   
 * silt_x-ycm: Proportion of silt particles (≥ 0.002 mm and ≤ 0.05/0.063 mm) in the fine earth fraction
   Soil property data provided by SoilGrids
   The data is available for the whole world.
   The resolution of the data is 250m x 250m.
   Measured in a depth of x-ycm
   
 * soc_x-ycm: Soil organic carbon content in the fine earth fraction
   Soil property data provided by SoilGrids
   The data is available for the whole world.
   The resolution of the data is 250m x 250m.
   Measured in a depth of x-ycm
   
 * ocd_x-ycm: Organic carbon density
   Soil property data provided by SoilGrids
   The data is available for the whole world.
   The resolution of the data is 250m x 250m.
   Measured in a depth of x-ycm
   
 * ocs_x-ycm: Organic carbon stocks
   Soil property data provided by SoilGrids
   The data is available for the whole world.
   The resolution of the data is 250m x 250m.
   Measured in a depth of x-ycm
   
 * Available depth levels for SoilGrids data: 0-5cm, 5-15cm, 15-30cm, 30-60cm, 60-100cm, 100-200cm


So these are three possbile ways to provide the predictor data:

```
"predictors": {
  "elevation": {
    "file_path": "predictor_1.csv",
    "unit": "m",
    "std_deviation": true,
    "constant": true,
    "nan_value": ""
  },
  ...
}
```

```
"predictors": {
  "elevation": {
    "file_path": [
      "/abs/path/to/predictor_1.csv"
    ],
    "unit": "m",
    "std_deviation": true,
    "constant": true,
    "nan_value": ""
  },
  ...
}
```

```
"predictors": {
  "elevation_bkg": null,
  ...
}
```

The predictor file looks like this:
```
$ head -n 5 soil_moisture_prediction/test_data/predictor_data.csv
# { "predictor_name": "elevation", "unit": "m", "std_deviation": true, "constant": true, "nan_value": "", "file_path": null  }
632200.0,5741600.0,251.3,5.026
632400.0,5741600.0,241.85,4.837
632600.0,5741600.0,235.02,4.7004
632800.0,5741600.0,229.0,4.58
```

The predictor can have a head starting with a #. After the #, a json must be given with the same information as the parameters.json file. This is a redundant way of giving the parameters and is used for programmatic reading with out a parameters.json file.

The soil moisture data looks like this:
```
$ head -n 5 soil_moisture_prediction/test_data/soil_moisture_data.csv
EPSG_UTM_x,EPSG_UTM_y,Day,soil_moisture,err_low,err_high
633742.2079,5741065.818,20220327,0.26870625,-0.0264875,0.0298375
633694.9659,5741026.54,20220327,0.27261,-0.02075,0.022775
633652.0085,5740981.625,20220327,0.27655625,-0.0171125,0.018425
633613.7622,5740928.489,20220327,0.280341071,-0.01545,0.0165375
```

The soil moisture data can have a header with the column names.

## Pydantic model
This is a description of the input parameters model:
area_x1:
  Defining the left boundrie of the area.

area_x2:
  Defining the right boundrie of the area.

area_y1:
  Defining the lower boundrie of the area.

area_y2:
  Defining the higher boundrie of the area.

area_resolution:
  Defining the resolution of the area.

projection:
  The projection of the bounding box e.g. EPSG:25832

soil_moisture_data:
  The path to the soil moisture data.

predictors:
  A dictionary of predictors. Either provide one of the predefined predictors (e.g. 'corine') with None or provide a predictor information model.

monte_carlo_soil_moisture:
  Whether to use a Monte Carlo Simulation to predict uncertainty for soil moisture.

monte_carlo_predictors:
  Whether to use a Monte Carlo Simulation to predict uncertainty for the predictors.

monte_carlo_iterations:
  Number of iterations for the Monte Carlo Simulation.

allow_nan_in_training:
  Whether to allow NaN values in the training data.

predictor_qmc_sampling:
  Whether to use Quasi-Monte Carlo sampling for the predictors.

compute_slope:
  Whether to compute the slope from elevation and use as predictor.

compute_aspect:
  Whether to compute the aspect from elevation and use as predictor.

past_prediction_as_feature:
  Whether to use the past prediction as a feature.

what_to_plot:
  List of which plotting functions should be used.

save_results:
  Dump random forest model. Reload it and use it for predictions.

save_input_data:
  Dump input data. Quicker to reload the data.

## Algorithm
The algorithm trains a random forest regressor (RandomForestRegressor from scikit-learn) with the soil moisture data and the predictor values at the measurements locations.
The trained model is then applied on the whole densely gridded area. 
The output is the a numpy array with the soil moisture values at each grid node. 

## Visualization
In addition to the resulting array(s) (prediction only or prediction and coefficient of dispersion),
the programm offers to plot some results.  
*predictors*: plot all the predictors as color maps after re-gridding them to the project grid.  
*pred\_correlation*: compute and plot the correlation between each predictors and display them as a heatmap. The color intensity indicates the strength and direction of correlation,
ranging from -1 (strong negative correlation) to 1 (strong positive correlation). It can help to remove redundant predictors highly correlated between them.  
*day\_measurements*: plot soil moisture measurements as a scatter plot on an x-y mapfor each day. The measurements are colored according to their corresponding soil moisture values.
If Monte Carlo simulations are enabled, error bands representing the standard deviations are overlaid on the scatter plot.  
*day\_predictor\_importance*: plot histogram of the normalized predictor importances from the random forest model for each day.  
If Monte Carlo simulations are enabled, the plot shows the 5th, 50th (median), and 95th quantiles of the importance values.
*day\_prediction\_map*: plot the map of the densely modelled soil moisture on the project area. If uncertainty are provided
the coefficient of dispersion map is also provided.  
*alldays\_predictor\_importance*: if several days are provided, the predictor importance is computed for each day 
and a curve of the predictor importance along days is plotted for each predictor. The x-axis represents the days, and the y-axis represents the importance values.

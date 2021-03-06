# Generating fake data

## Overview and Purpose
This directory contains a file called `generate_fake_data.py`. The purpose of `generate_fake_data.py` is to create a `.csv` file with fake data with the following intended applications:
- As an example of how data needs to be formatted to be passed into the model.
- To ensure the files are being generated correctly to test GUI setup.
- To test the setup and running of the repo.

The following should be noted with regards to artefacts produced by using fake data:
- *DO NOT* use the fake data generated to inform any insights to be applied to a real world setting.
- *DO NOT* use the fake data to test the performance of the model.

The data is generated completely randomly, with each field having random values generated independently of other fields. This generator was created having never been exposed to the real data.

The categories for the fields in the fake data can be found in [fake_data_categories.json](../config/fake_data_categories.json). The categories specified in this file are randomly chosen to fill the corresponding fields in the fake data. This is done in `generate_fake_data.py`.

Note a number of the fields will show only test categories and may not be reflective of the types of categories or number of categories types in each field. However the formatting of the fields is reflective as an example of what is required to run the model.

Data fields that do not have their categories specified in [fake_data_categories.json](../config/fake_data_categories.json) or are not categorical variables have the fake data required generated in `generate_fake_data.py` line by line to show how the data is being generated for each field. In `generate_fake_data.py` the fields are split into the field data type (e.g. str, int) required for the models to train.


## How to run
Before running ensure your environment is set up as described in: [Getting Started](../README.md) 

Please note all bash commands listed below assume the working directory is `fake_data_generation` (this directory).

There are a number of parameters to run the `generate_fake_data.py`, available using the `--help` flag:

```
$ python3  generate_fake_data.py --help
usage: generate_fake_data.py [-h] [--filename FILENAME] [--number_of_students NUMBER_OF_STUDENTS] [--number_of_wards NUMBER_OF_WARDS] [--seed SEED]

The purpose of `generate_fake_data.py` is to create a `.csv` file with fake data with the following intended applications: An example of how data needs to be formatted to be passed into the model and to test the setup and running of the repo.

optional arguments:
  -h, --help            show this help message and exit
  --number_of_students NUMBER_OF_STUDENTS, -ns NUMBER_OF_STUDENTS
                        [int] Number of students records to generate. Default is 20.
  --number_of_wards NUMBER_OF_WARDS, -nw NUMBER_OF_WARDS
                        [int] Number of students records to generate. Default is 5.
  --filename FILENAME, -fn FILENAME
                        [str] The name of the csv file saved at the end (do not add.csv). The default name is set to "fake_data". This will generate a file called "fake_data.csv" .
  --seed SEED, -s SEED  [int] If specified will ensure result is reproducible. Default is set to None so will generate a different result each time.
  ```

  To test the setup and the running of the repo it is recommended to run `generate_fake_data` with the following arguments:
  ```bash
$ python3 generate_fake_data.py --number_of_students 25 --number_of_wards 4 -fn "fake_data"
```
or depending on your machine setup:

  ```bash
$ python generate_fake_data.py --number_of_students 25 --number_of_wards 4 -fn "fake_data"
```

## Generating fake data to test repo
For a step by step guide on how to generate the fake data and then train the models to test the repo setup, please see the [main README](../README.md) 
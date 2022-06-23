"""
This file generates fake data randomly.
The purpose of this data is to test the running of the models and setup of the repo.
Field values are generated randomly independently of each other.
Instructions on how to run this file can be found in the README.md in this directory.
"""

import argparse
import json
import numpy as np
import pandas as pd
import random

# Get arguments from command line
# (If args are not specified default values will be used.)
parser = argparse.ArgumentParser(
    description="""The purpose of `generate_fake_data.py` is to create a `.csv` file with fake data with the following intended applications: 
    An example of how data needs to be formatted to be passed into the model and to test the setup and running of the repo."""
)

# Args to generate
parser.add_argument(
    "--number_of_students",
    "-ns",
    type=int,
    default=20,
    help="[int] Number of students records to generate. Default is 20.",
)

parser.add_argument(
    "--number_of_wards",
    "-nw",
    type=int,
    default=5,
    help="[int] Number of wards to generate. Default is 5.",
)

parser.add_argument(
    "--filename",
    "-fn",
    type=str,
    default="fake_data",
    help="""[str] The name of the xlsx file saved at the end (do not add.csv).
    The default name is set to "fake_data". This will generate a file called "fake_data.xlsx" . """,
)

parser.add_argument(
    "--seed",
    "-s",
    default=None,
    type=int,
    help="[int] If specified will ensure result is reproducible. Default is set to None so will generate a different result each time.",
)

# Read arguments from the command line
args = parser.parse_args()

import os

cwd = os.getcwd()
print(cwd)


# Set seed if specified:
if args.seed is not None:
    np.random.seed(seed=args.seed)

# Load fake_data_description.json to get columns required for training data
with open("config/fake_data_description.json", "r") as file:
    data_columns = json.load(file)

# Create dataframe with original data fields
student_columns = [x for x in data_columns["student_data_fields"]]
student_df = pd.DataFrame(columns=student_columns)

ward_columns = [x for x in data_columns["ward_data_fields"]]
ward_df = pd.DataFrame(columns=ward_columns)

placement_columns = [x for x in data_columns["placement_data_fields"]]
placement_df = pd.DataFrame(columns=placement_columns)

# Load data_categories.json to get the data categories required for each field in the fake data
with open("config/fake_data_categories.json", "r") as file:
    data_cat = json.load(file)

# Assign data categories to fields in dataframe
for column in student_columns:
    if column in data_cat["student_data_fields"].keys():
        student_df[column] = np.random.choice(
            data_cat["student_data_fields"][column], size=args.number_of_students
        )

for column in ward_columns:
    if column in data_cat["ward_data_fields"].keys():
        ward_df[column] = np.random.choice(
            data_cat["ward_data_fields"][column], size=args.number_of_wards
        )

for column in placement_columns:
    if column in data_cat["placement_data_fields"].keys():
        placement_df[column] = np.random.choice(
            data_cat["placement_data_fields"][column], size=args.number_of_students * 3
        )

# Remaining fields to fill in so they are not null
# fields requiring int:
student_df["student_id"] = ["Student" + str(i) for i in range(args.number_of_students)]

ward_df["ward_name"] = ["Ward" + str(i) for i in range(args.number_of_wards)]
ward_df["capacity_num"] = ward_df["p1_cap"] = ward_df["p2_cap"] = ward_df[
    "p3_cap"
] = np.random.randint(2, 30, size=(args.number_of_wards))

placement_df["placement_len_weeks"] = np.random.randint(
    1, 5, size=(args.number_of_students * 3)
)

student_df["prev_placements"] = [[] for i in range(args.number_of_students)]

# Write dataframe to excel
with pd.ExcelWriter(f"data/{args.filename}.xlsx") as writer:
    student_df.to_excel(writer, sheet_name="students", index=False)
    ward_df.to_excel(writer, sheet_name="wards", index=False)
    placement_df.to_excel(writer, sheet_name="placements", index=False)
    writer.save()

# Message to show script has run
print(
    f"Fake Data Generated! File saved: {args.filename}.xlsx with {args.number_of_students} students, {args.number_of_wards} wards and {args.number_of_students*3} placements created. Seed was set to {args.seed}."
)

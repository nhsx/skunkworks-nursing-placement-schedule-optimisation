from src import data_load
import pandas as pd
import pytest

def test_readData():
    dataload = data_load.DataLoader()
    dataload.readData("tests/test_data.xlsx")
    assert len(dataload.students) == 20
    assert len(dataload.ward_data) == 5
    assert len(dataload.uni_placements) == 60


def test_cohort_generation():
    dataload = data_load.DataLoader()
    cohort_df = pd.DataFrame([['uni','qual','start']],columns = ['uni_col','qual_col','start_col'])
    cohort_df = dataload.createCohort(cohort_df,'student_cohort','uni_col','qual_col','start_col')
    assert cohort_df['student_cohort'][0] == 'uni_qual start'

def test_relative_date_calc():
    dataload = data_load.DataLoader()
    date_df = pd.DataFrame([['01/01/2020','15/01/2020']],columns = ['start_date','end_date'])
    date_df = dataload.calcRelDateWeeks(date_df,date_df,'weeks_diff','end_date','start_date')
    assert date_df['weeks_diff'][0] == 2

    date_df = pd.DataFrame([['01/01/2020','15/01/2020']],columns = ['start_date','end_date'])
    date_df = dataload.calcRelDateWeeks(date_df,date_df,'weeks_diff','start_date','end_date')
    assert date_df['weeks_diff'][0] == -22
from src import data_load
import pandas as pd
import numpy as np

def test_readData():
    dataload = data_load.DataLoader()
    dataload.readData("tests/test_data.xlsx")
    assert len(dataload.students) == 20
    assert len(dataload.ward_data) == 5
    assert len(dataload.uni_placements) == 60

def test_cohort_generation():
    dataload = data_load.DataLoader()
    cohort_df = pd.DataFrame(
        {
            'uni_col':['uni'],
            'qual_col':['qual'],
            'start_col':['start']
        })
    cohort_df = dataload.createCohort(cohort_df,'student_cohort','uni_col','qual_col','start_col')
    assert cohort_df['student_cohort'][0] == 'uni_qual start'

def test_relative_date_calc():
    dataload = data_load.DataLoader()
    date_df = pd.DataFrame(
        {
            'start_date':['01/01/2020'],
            'end_date':['15/01/2020']
        })
    date_df = dataload.calcRelDateWeeks(date_df,date_df,'weeks_diff','end_date','start_date')
    assert date_df['weeks_diff'][0] == 2

def test_relative_date_calc_negative_diff():
    dataload = data_load.DataLoader()
    date_df = pd.DataFrame(
        {
            'start_date':['15/01/2020'],
            'end_date':['01/01/2020']
        })
    date_df = dataload.calcRelDateWeeks(date_df,date_df,'weeks_diff','end_date','start_date')
    assert date_df['weeks_diff'][0] == -2


def test_placement_cleaning():
    dataload = data_load.DataLoader()
    dataload.students = pd.DataFrame({
        'prev_placements':["ward1,ward2,'ward3',ward4"],
        'allprevwards':['']
    })
    dataload.cleanPrevPlacements()
    print(dataload.students["allprevwards"])
    assert len(dataload.students["allprevwards"][0]) == len(['ward1','ward2','ward3','ward4'])
    assert all([a == b for a, b in zip(dataload.students["allprevwards"][0], ['ward1','ward2','ward3','ward4'])])

def test_cleanStudentPlacementCohorts():
    dataload = data_load.DataLoader()
    cohort_df = pd.DataFrame(
        {
            'university':['uni'],
            'qualification':['qual'],
            'course_start':['start']
        })
    dataload.students = cohort_df
    dataload.uni_placements = cohort_df
    dataload.cleanStudentPlacementCohorts()

    assert dataload.students['student_cohort'][0] == 'uni_qual start'
    assert dataload.uni_placements['student_cohort'][0] == 'uni_qual start'

def test_cleanWardAuditExp():
    dataload = data_load.DataLoader()
    dataload.ward_data = pd.DataFrame(
        {
            'education_audit_exp':['2020/01/15']
        })
    dataload.uni_placements = pd.DataFrame(
        {
            'placement_start_date':['2020/01/01','2020/02/30','2019/09/15'],
        })
    dataload.calcWardAuditExp()
    assert dataload.ward_data['education_audit_exp_week'][0] == 17

def test_cleanWardCapacity():
    dataload = data_load.DataLoader()
    dataload.ward_data = pd.DataFrame({
        'p1_cap':[5],
        'p2_cap':[2],
        'p3_cap':[3],
        'capacity':['']
    })
    dataload.cleanWardCapacity()
    assert dataload.ward_data['capacity'][0]==5

def test_cleanSelectWardColumnNames():
    dataload = data_load.DataLoader()
    dataload.ward_data = pd.DataFrame(None, columns = ["ward_name",
                "ward_speciality",
                "education_audit_exp",
                "education_audit_exp_week",
                "covid_status",
                "capacity",
                "p1_cap",
                "p2_cap",
                "p3_cap",])
    dataload.cleanSelectWardColumnNames()
    intended_col_names = [
            "Ward",
            "Department",
            "education_audit_exp",
            "education_audit_exp_week",
            "covid_status",
            "capacity",
            "P1_CAP",
            "P2_CAP",
            "P3_CAP",
        ]
    assert all([a == b for a, b in zip(dataload.ward_data.columns, intended_col_names)])

def test_cleanStudentsPreviousDepartments():
    dataload = data_load.DataLoader()
    dataload.ward_data = pd.DataFrame({
        'Ward':['WardA','WardB','WardC'],
        'Department':['DepartmentD','DepartmentB','DepartmentC']
    })
    dataload.students = pd.DataFrame({
        'allprevwards':[['WardA','WardB']],
        'prevdeps':[''],
        'allprevdeps':['']
    })
    dataload.cleanStudentsPreviousDepartments()
    assert dataload.students["allprevdeps"][0] == 'DepartmentD, DepartmentB'

def test_cleanStudentPreviousWards():
    dataload = data_load.DataLoader()
    dataload.students = pd.DataFrame({
        'allprevwards':[['WardA','WardC','WardD']]
    })
    dataload.cleanStudentPreviousWards()
    assert dataload.students['allprevwards'][0] == 'WardA, WardC, WardD'

def test_mergeStudentsWithPlacements():
    dataload = data_load.DataLoader()
    dataload.students = pd.DataFrame({
        'student_cohort':['CohortA','CohortB','CohortC']
    })

    dataload.uni_placements = pd.DataFrame({
        'student_cohort':['CohortA','CohortB','CohortC'],
        'placement_details':['Placement1','Placement2','Placement3']
    })

    dataload.mergeStudentsWithPlacements()
    print(dataload.student_placements['placement_details'].values)
    assert all([a == b for a, b in zip(dataload.student_placements['placement_details'].values, ['Placement1','Placement2','Placement3'])])


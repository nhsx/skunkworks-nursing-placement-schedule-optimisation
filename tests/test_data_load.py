from src import data_load
import pandas as pd
import numpy as np
import pytest

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

def test_datePreparation():
    dataload = data_load.DataLoader()
    dataload.student_placements = pd.DataFrame({
        'placement_start_date': ['2020/01/01','2020/01/22'],
        'placement_len_weeks':[2,1]
    })
    dataload.uni_placements = pd.DataFrame({
        'placement_start_date': ['2019/01/01','2019/01/22']
    })

    dataload.datePreparation()

    assert all([a == b for a, b in zip(dataload.student_placements['placement_end_date'].values, [53,55])])

def test_restructureData():
    dataload = data_load.DataLoader()
    num_weeks = 5

    dataload.ward_data = pd.DataFrame({
        'Ward':['WardA','WardB','WardC'],
        'Department':['DepartmentD','DepartmentB','DepartmentC'],
        'education_audit_exp_week':[5,6,7],
        'covid_status':['Low/Medium','Medium/High','Low/Medium'],
        'capacity':[2,2,2],
        'P1_CAP':[2,1,2],
        'P2_CAP':[1,2,2],
        'P3_CAP':[2,2,1]
    })

    dataload.student_placements = pd.DataFrame({
        'student_id':[0,1],
        'placement_name':['PlacementA','PlacementB'],
        'student_cohort':['CohortA','CohortB'],
        'placement_len_weeks':[2,1],
        'placement_start_date': [5,8],
        'placement_start_date_raw': ['2020/01/01','2020/01/22'],
        'year_num':[1,1],
        'allprevwards': ['WardA, WardB','WardC, WardD'],
        'allprevdeps': ['DepA, DepB','DepC'],
        'allowable_covid_status': ['Medium/High','Medium/High']
        })
    dataload.restructureData(num_weeks)

    assert len(dataload.slots) == 5
    assert dataload.slots[3].id == 3    

    assert len(dataload.ward_data) == 3
    assert dataload.wards[1].covid_status == 'Medium/High'

    assert len(dataload.placements) == 2
    assert dataload.placements[1].start_date == '2020/01/22'

def test_val_date_datatype():
    dataload = data_load.DataLoader()
    col_dict = {"Placements": ["placement_start_date"]}
    dataload.placements = pd.DataFrame({
        'placement_start_date':['20th January 2019']
    })
    with pytest.raises(TypeError):
        dataload.val_date_datatype(col_dict)
        
def test_val_other_datatype():
    dataload = data_load.DataLoader()
    col_dict = {"Students": ["year"]}
    dataload.placements = pd.DataFrame({
        'year':['2']
    })
    with pytest.raises(TypeError):
        dataload.val_other_datatype(col_dict, 'int')

def test_input_quality_checks_int_check():
    dataload = data_load.DataLoader()
    dataload.students = pd.DataFrame({
        'prev_placements': ['[Placement1, Placement2, Placement3]'],
        'year':[3]
    })
    dataload.wards = pd.DataFrame({
        'capacity_num': [3],
        'p1_cap': [2], 
        'p2_cap': ['2'], 
        'p3_cap': [3],
        'education_audit_exp': ['2020/05/01']
    })
    dataload.uni_placements = pd.DataFrame({
        'placement_len_weeks': [5],
        'placement_start_date': ['2020/01/01']
    })

    with pytest.raises(TypeError):
        dataload.input_quality_checks()


def test_input_quality_checks_date_check():
    dataload = data_load.DataLoader()
    dataload.students = pd.DataFrame({
        'prev_placements': ['[Placement1, Placement2, Placement3]'],
        'year':[3]
    })
    dataload.wards = pd.DataFrame({
        'capacity_num': [3],
        'p1_cap': [2], 
        'p2_cap': [2], 
        'p3_cap': [3],
        'education_audit_exp': ['20th January 2019']
    })
    dataload.uni_placements = pd.DataFrame({
        'placement_len_weeks': [5],
        'placement_start_date': ['2020/01/01']
    })

    with pytest.raises(TypeError):
        dataload.input_quality_checks()
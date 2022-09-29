from tkinter import Place
from src import Schedule
from src.Ward import Ward
from src.Placement import Placement
from src.Slot import Slot
import pandas as pd
import numpy as np
import pytest

def test_init():
    sch = Schedule.Schedule(slots = [1,2,3], wards = [1,2,3], placements = [1,2,3], num_weeks = 5)
    assert sch.num_weeks == 5
    assert sch.slots == [[],[],[],[],[],[],[],[],[]]
    assert sch.critical_care_placement_check == False

def test_calc_slot_index():
    sch = Schedule.Schedule(slots = [1,2,3], wards = [1,2,3], placements = [1,2,3], num_weeks = 5)
    slot_index = sch.calc_slot_index(ward_id = 5, num_weeks = 3, start_week = 2)
    assert slot_index == 18

test_diff_years = [{'placement': Placement([0, 'A_P1,E1', 'CohortA', 2, 1, '2020/01/01', 'P1', ['list'], ['list'], 'Medium/High']), 'year_cap': 2},
                {'placement': Placement([0, 'A_P1,E1', 'CohortA', 2, 1, '2020/01/01', 'P2', ['list'], ['list'], 'Medium/High']), 'year_cap': 3},
                {'placement': Placement([0, 'A_P1,E1', 'CohortA', 2, 1, '2020/01/01', 'P3', ['list'], ['list'], 'Medium/High']), 'year_cap': 1},
                {'placement': Placement([0, 'A_P1,E1', 'CohortA', 2, 1, '2020/01/01', 'P8', ['list'], ['list'], 'Medium/High']), 'year_cap': 3},
        ]

@pytest.mark.parametrize('param_input', test_diff_years)
def test_id_year_capacity(param_input):
    wards = [Ward([0, 'WardA', 'DepartmentB', 4, 'Low/Medium', 3, 2, 3, 1])]
    sch = Schedule.Schedule(slots = [1,2,3], wards = wards, placements = [1,2,3], num_weeks = 5)
    pl = param_input['placement']
    yc = sch.id_year_capacity(pl, 0)
    assert yc == param_input['year_cap']

def test_normal_schedule_generation():
    wards = [Ward([0, 'WardA', 'DepartmentB', 4, 'Low/Medium', 3, 2, 3, 2]),Ward([1, 'WardB', 'DepartmentA', 1, 'Low/Medium', 2, 2, 0, 1])]
    placements = [Placement([0, 'A_P1,E1', 'CohortA', 2, 1, '2020/01/01', 'P2', ['list'], ['list'], 'Medium/High'])]
    slots = [Slot([0,'1']),Slot([1,'2']),Slot([2,'3']),Slot([3,'4'])]
    sch = Schedule.Schedule(slots = slots, wards = wards, placements = placements, num_weeks = 4)
    sch.slots[2].append(placements[0])
    sch.slots[2].append(placements[0])
    sch.schedule_generation()
    assert sch.conf_placements[0]['placement'] == placements[0]
    assert sch.conf_placements[0]['startweek'] == 1
    assert sch.conf_placements[0]['slotIndex'] == 2

def test_no_wards_covid_schedule_generation():
    wards = [Ward([0, 'WardA', 'DepartmentB', 4, 'Medium/High', 3, 2, 3, 2]),Ward([1, 'WardB', 'DepartmentA', 1, 'Medium/High', 2, 2, 0, 1])]
    placements = [Placement([0, 'A_P1,E1', 'CohortA', 2, 1, '2020/01/01', 'P2', ['list'], ['list'], 'Low/Medium'])]
    slots = [Slot([0,'1']),Slot([1,'2']),Slot([2,'3']),Slot([3,'4'])]
    sch = Schedule.Schedule(slots = slots, wards = wards, placements = placements, num_weeks = 4)
    with pytest.warns(UserWarning):
        sch.schedule_generation()

def test_no_cap_schedule_generation():
    wards = [Ward([0, 'WardA', 'DepartmentB', 4, 'Low/Medium', 2, 0, 1, 0]),Ward([1, 'WardB', 'DepartmentA', 1, 'Low/Medium', 2, 0, 1, 0])]
    placements = [Placement([0, 'A_P1,E1', 'CohortA', 2, 1, '2020/01/01', 'P2', ['list'], ['list'], 'Medium/High'])]
    slots = [Slot([0,'1']),Slot([1,'2']),Slot([2,'3']),Slot([3,'4'])]
    sch = Schedule.Schedule(slots = slots, wards = wards, placements = placements, num_weeks = 4)
    print(sch.slots)
    print(len(sch.slots))
    sch.slots[2].append(placements[0])
    sch.slots[6].append(placements[0])
    print(sch.slots)
    with pytest.warns(UserWarning):
        sch.schedule_generation()

def test_clean_departments():
    sch = Schedule.Schedule(slots = [1,2,3], wards = [1,2,3], placements = [1,2,3], num_weeks = 5)
    cleaned_deps = sch.clean_departments('eneral Department, DepartmentC, DepartmentA, Depart\xa0mentE, None')
    print(cleaned_deps)
    assert all([a == b for a, b in zip(cleaned_deps, ['general','department','departmentc','departmenta','departmente'])])

def test_get_fitness():
    wards = [Ward([0, 'WardA', 'DepartmentB', 4, 'Low/Medium', 3, 2, 3, 2]),Ward([1, 'WardB', 'DepartmentA', 1, 'Low/Medium', 2, 2, 0, 1])]
    placements = [Placement([0, 'A_P1,E1', 'CohortA', 2, 1, '2020/01/01', 'P2', "['WardA','WardB']", "['DepA','DepB']", 'Low/Medium'])]
    slots = [Slot([0,'1']),Slot([1,'2']),Slot([2,'3']),Slot([3,'4'])]
    sch = Schedule.Schedule(slots = slots, wards = wards, placements = placements, num_weeks = 4)
    sch.schedule_generation()
    sch.get_fitness()
    assert sch.fitness > 0

def test_capacity_exc_get_fitness():
    wards = [Ward([0, 'WardA', 'DepartmentB', 4, 'Low/Medium', 0, 0, 0, 0]),Ward([1, 'WardB', 'DepartmentA', 1, 'Low/Medium', 0, 0, 0, 0])]
    placements = [Placement([0, 'A_P1,E1', 'CohortA', 2, 1, '2020/01/01', 'P2', "['WardA','WardB']", "['DepA','DepB']", 'Low/Medium'])]
    slots = [Slot([0,'1']),Slot([1,'2']),Slot([2,'3']),Slot([3,'4'])]
    sch = Schedule.Schedule(slots = slots, wards = wards, placements = placements, num_weeks = 4)
    sch.schedule_generation()
    sch.get_fitness()
    assert sch.viable == False
    assert sch.non_viable_reason == 'Cap Exceeded'

def test_covid_status_get_fitness():
    wards = [Ward([0, 'WardA', 'DepartmentB', 4, 'Medium/High', 3, 2, 3, 2]),Ward([1, 'WardB', 'DepartmentA', 1, 'Medium/High', 2, 2, 0, 1])]
    placements = [Placement([0, 'A_P1,E1', 'CohortA', 2, 1, '2020/01/01', 'P2', "['WardA','WardB']", "['DepA','DepB']", 'Low/Medium'])]
    slots = [Slot([0,'1']),Slot([1,'2']),Slot([2,'3']),Slot([3,'4'])]
    sch = Schedule.Schedule(slots = slots, wards = wards, placements = placements, num_weeks = 4)
    sch.schedule_generation()
    sch.get_fitness()
    assert sch.viable == False
    assert sch.non_viable_reason == 'Covid status not compatible'

def test_double_booked_get_fitness():
    wards = [Ward([0, 'WardA', 'DepartmentB', 4, 'Low/Medium', 1, 1, 1, 1]),Ward([1, 'WardB', 'DepartmentA', 1, 'Low/Medium', 1, 1, 1, 1])]
    placements = [Placement([0, 'A_P1,E1', 'CohortA', 2, 1, '2020/01/01', 'P2', "['WardA','WardB']", "['DepA','DepB']", 'Low/Medium']),Placement([0, 'A_P1,E1', 'CohortA', 2, 1, '2020/01/01', 'P2', "['WardA','WardB']", "['DepA','DepB']", 'Low/Medium'])]
    slots = [Slot([0,'1']),Slot([1,'2']),Slot([2,'3']),Slot([3,'4'])]
    sch = Schedule.Schedule(slots = slots, wards = wards, placements = placements, num_weeks = 4)
    sch.schedule_generation()
    sch.get_fitness()
    assert sch.viable == False
    assert sch.non_viable_reason == 'Double booked'

def test_check_specific_speciality():
    wards = [Ward([0, 'WardA', 'DepartmentB', 4, 'Low/Medium', 3, 2, 3, 2]),Ward([1, 'WardB', 'DepartmentA', 1, 'Low/Medium', 2, 2, 0, 1])]
    placements = [Placement([0, 'A_P1,E1', 'CohortA', 2, 1, '2020/01/01', 'P2', "WardA,WardB", "DepA, DepB", 'Low/Medium'])]
    slots = [Slot([0,'1']),Slot([1,'2']),Slot([2,'3']),Slot([3,'4'])]
    sch = Schedule.Schedule(slots = slots, wards = wards, placements = placements, num_weeks = 4)
    sch.schedule_generation()
    sch.get_fitness()
    sch.schedule_scores = 0
    sch.check_specific_speciality(True, ['depb'],10)
    assert sch.schedule_scores == 10

def test_populate_schedule():
    wards = [Ward([0, 'WardA', 'DepartmentB', 4, 'Low/Medium', 3, 2, 3, 2]),Ward([1, 'WardB', 'DepartmentA', 1, 'Low/Medium', 2, 2, 0, 1])]
    placements = [Placement([0, 'A_P1,E1', 'CohortA', 2, 1, '2020/01/01', 'P2', "['WardA','WardB']", "['DepA','DepB']", 'Low/Medium'])]
    slots = [Slot([0,'1']),Slot([1,'2']),Slot([2,'3']),Slot([3,'4'])]
    sch = Schedule.Schedule(slots = slots, wards = wards, placements = placements, num_weeks = 4)
    sch.schedule_generation()
    sch.populate_schedule()
    assert sch.viable == True
    assert sch.fitness > 0

def test_recombination():
    wards = [Ward([0, 'WardA', 'DepartmentB', 4, 'Low/Medium', 3, 2, 3, 2]),Ward([1, 'WardB', 'DepartmentA', 1, 'Low/Medium', 2, 2, 0, 1])]
    placements1 = [Placement([0, 'A_P1,E1', 'CohortA', 2, 1, '2020/01/01', 'P2', "['WardA','WardB']", "['DepA','DepB']", 'Low/Medium'])]
    placements1.append(placements1[0])
    slots = [Slot([0,'1']),Slot([1,'2']),Slot([2,'3']),Slot([3,'4'])]
    sch1 = Schedule.Schedule(slots = slots, wards = wards, placements = placements1, num_weeks = 4)

    wards = [Ward([0, 'WardA', 'DepartmentB', 4, 'Low/Medium', 3, 2, 3, 2]),Ward([1, 'WardB', 'DepartmentA', 1, 'Low/Medium', 2, 2, 0, 1])]
    placements2 = [Placement([0, 'A_P1,E1', 'CohortA', 3, 1, '2020/01/01', 'P2', "['WardA','WardB']", "['DepA','DepB']", 'Low/Medium'])]
    placements2.append(placements2[0])
    slots = [Slot([0,'1']),Slot([1,'2']),Slot([2,'3']),Slot([3,'4'])]
    sch2 = Schedule.Schedule(slots = slots, wards = wards, placements = placements2, num_weeks = 4)

    sch1.schedule_generation()
    sch1.populate_schedule()
    sch2.schedule_generation()
    sch2.populate_schedule()

    new_schs = sch1.recombination(sch2, 2, 3)
    assert len(new_schs) == 3

def test_mutation():
    wards = [Ward([0, 'WardA', 'DepartmentB', 4, 'Low/Medium', 3, 2, 3, 2]),Ward([1, 'WardB', 'DepartmentA', 1, 'Low/Medium', 2, 2, 0, 1])]
    placements = [Placement([0, 'A_P1,E1', 'CohortA', 2, 1, '2020/01/01', 'P2', "['WardA','WardB']", "['DepA','DepB']", 'Low/Medium'])]
    slots = [Slot([0,'1']),Slot([1,'2']),Slot([2,'3']),Slot([3,'4']),Slot([4,'5']),Slot([5,'6']),Slot([6,'7']),Slot([7,'8']),Slot([8,'9']),Slot([9,'10'])]
    sch = Schedule.Schedule(slots = slots, wards = wards, placements = placements, num_weeks = 10)

    sch.schedule_generation()
    prev_slot_index = sch.conf_placements[0]['slotIndex']
    all_mut_schs = []
    for entry in range(0,10):
        all_mut_schs.append(sch.mutation(1))

    total_changed = 0
    for mut_sch in all_mut_schs:
        if mut_sch.conf_placements[0]['slotIndex'] != prev_slot_index:
            total_changed += 1
    assert total_changed > 0

def test_produce_dataframe():
    wards = [Ward([0, 'WardA', 'DepartmentB', 4, 'Low/Medium', 3, 2, 3, 2]),Ward([1, 'WardB', 'DepartmentA', 1, 'Low/Medium', 2, 2, 0, 1])]
    placements = [Placement([0, 'A_P1,E1', 'CohortA', 2, 1, '2020/01/01', 'P2', "['WardA','WardB']", "['DepA','DepB']", 'Low/Medium'])]
    slots = [Slot([0,'1']),Slot([1,'2']),Slot([2,'3']),Slot([3,'4'])]
    sch = Schedule.Schedule(slots = slots, wards = wards, placements = placements, num_weeks = 4)

    sch.schedule_generation()
    sch_df = sch.produce_dataframe()
    assert sch_df.placement_duration[0] == 2
    assert sch_df.placement_start_date[0] == '2020/01/01'
    assert sch_df.p3_ward_capacity[0] == 2

def test_schedule_quality_check():
    wards = [Ward([0, 'WardA', 'DepartmentB', 4, 'Low/Medium', 3, 2, 3, 2]),Ward([1, 'WardB', 'DepartmentA', 1, 'Low/Medium', 2, 2, 0, 1])]
    placements = [Placement([0, 'A_P1,E1', 'CohortA', 2, 1, '2020/01/01', 'P2', "['WardA','WardB']", "['DepA','DepB']", 'Low/Medium'])]
    slots = [Slot([0,'1']),Slot([1,'2']),Slot([2,'3']),Slot([3,'4'])]
    sch = Schedule.Schedule(slots = slots, wards = wards, placements = placements, num_weeks = 4)

    sch.schedule_generation()
    (incorrect_num_plac_rows, incorrect_len_rows, cap_exceeded_rows, double_booked_rows) = sch.schedule_quality_check()
    assert incorrect_num_plac_rows == None
    assert incorrect_len_rows == None
    assert cap_exceeded_rows == None
    assert double_booked_rows == None
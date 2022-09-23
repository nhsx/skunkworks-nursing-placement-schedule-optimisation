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
    with pytest.raises(RuntimeError):
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
    with pytest.raises(RuntimeError):
        sch.schedule_generation()

    
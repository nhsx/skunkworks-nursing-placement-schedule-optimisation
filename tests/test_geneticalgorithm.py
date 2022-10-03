from src import Schedule
from src.GeneticAlgorithm import GeneticAlgorithm
from src.Ward import Ward
from src.Placement import Placement
from src.Slot import Slot
import pytest
import os


def test_generate_new_schedule():
    wards = [Ward([0, 'WardA', 'DepartmentB', 4, 'Low/Medium', 3, 2, 3, 2]),Ward([1, 'WardB', 'DepartmentA', 1, 'Low/Medium', 2, 2, 0, 1])]
    placements = [Placement([0, 'A_P1,E1', 'CohortA', 2, 1, '2020/01/01', 'P2', "['WardA','WardB']", "['DepA','DepB']", 'Low/Medium'])]
    slots = [Slot([0,'1']),Slot([1,'2']),Slot([2,'3']),Slot([3,'4'])]
    ga = GeneticAlgorithm(slots, wards, placements, 10, 4)

    sch = ga.generate_new_schedule()

    assert sch.fitness > 0
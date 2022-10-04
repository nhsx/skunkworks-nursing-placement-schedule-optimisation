from src.Schedule import Schedule
from src.GeneticAlgorithm import GeneticAlgorithm
from src.Ward import Ward
from src.Placement import Placement
from src.Slot import Slot
import inspect
import pytest
import os


def test_generate_new_schedule():
    wards = [Ward([0, 'WardA', 'DepartmentB', 4, 'Low/Medium', 3, 2, 3, 2]),Ward([1, 'WardB', 'DepartmentA', 1, 'Low/Medium', 2, 2, 0, 1])]
    placements = [Placement([0, 'A_P1,E1', 'CohortA', 2, 1, '2020/01/01', 'P2', "['WardA','WardB']", "['DepA','DepB']", 'Low/Medium'])]
    slots = [Slot([0,'1']),Slot([1,'2']),Slot([2,'3']),Slot([3,'4'])]
    ga = GeneticAlgorithm(slots, wards, placements, 10, 4)
    sch = ga.generate_new_schedule()
    assert sch.fitness > 0

def test_seed_schedules():
    wards = [Ward([0, 'WardA', 'DepartmentB', 4, 'Low/Medium', 3, 2, 3, 2]),Ward([1, 'WardB', 'DepartmentA', 1, 'Low/Medium', 2, 2, 0, 1])]
    placements = [Placement([0, 'A_P1,E1', 'CohortA', 2, 1, '2020/01/01', 'P2', "['WardA','WardB']", "['DepA','DepB']", 'Low/Medium'])]
    slots = [Slot([0,'1']),Slot([1,'2']),Slot([2,'3']),Slot([3,'4'])]
    ga = GeneticAlgorithm(slots, wards, placements, 10, 4)
    ga.seed_schedules()
    assert len(ga.schedules) == 10
    for i in range(0,9):
        assert ga.schedules[i]['fitness'] > 0
        assert isinstance(ga.schedules[i]['schedule'], Schedule) == True
        assert ga.schedules[i]['sched_id'] >= 0
        assert ga.schedules[i]['sched_id'] <= 9999

def test_non_viable_viable_schedule_check():
    wards = [Ward([0, 'WardA', 'DepartmentB', 4, 'Low/Medium', 3, 2, 3, 2]),Ward([1, 'WardB', 'DepartmentA', 1, 'Low/Medium', 2, 2, 0, 1])]
    placements = [Placement([0, 'A_P1,E1', 'CohortA', 2, 1, '2020/01/01', 'P2', "['WardA','WardB']", "['DepA','DepB']", 'Low/Medium'])]
    slots = [Slot([0,'1']),Slot([1,'2']),Slot([2,'3']),Slot([3,'4'])]
    ga = GeneticAlgorithm(slots, wards, placements, 1, 4)
    ga.seed_schedules()
    continue_eval, sch, sch_fit_list = ga.viable_schedule_check()
    assert continue_eval == True
    assert sch == None
    assert sch_fit_list[0] > 0

def test_viable_viable_schedule_check():
    wards = [Ward([0, 'WardA', 'DepartmentB', 4, 'Low/Medium', 3, 2, 3, 2]),Ward([1, 'WardB', 'DepartmentA', 1, 'Low/Medium', 2, 2, 0, 1])]
    placements = [Placement([0, 'A_P1,E1', 'CohortA', 2, 1, '2020/01/01', 'P2', "['WardA','WardB']", "['DepA','DepB']", 'Low/Medium'])]
    slots = [Slot([0,'1']),Slot([1,'2']),Slot([2,'3']),Slot([3,'4'])]
    ga = GeneticAlgorithm(slots, wards, placements, 1, 4)
    ga.fitness_threshold = 0.2
    ga.seed_schedules()
    continue_eval, sch, sch_fit_list = ga.viable_schedule_check()
    assert continue_eval == False
    assert sch == ga.schedules[0]['schedule']
    assert sch_fit_list[0] > 0

def test_status_update():
    wards = [Ward([0, 'WardA', 'DepartmentB', 4, 'Low/Medium', 3, 2, 3, 2]),Ward([1, 'WardB', 'DepartmentA', 1, 'Low/Medium', 2, 2, 0, 1])]
    placements = [Placement([0, 'A_P1,E1', 'CohortA', 2, 1, '2020/01/01', 'P2', "['WardA','WardB']", "['DepA','DepB']", 'Low/Medium'])]
    slots = [Slot([0,'1']),Slot([1,'2']),Slot([2,'3']),Slot([3,'4'])]
    ga = GeneticAlgorithm(slots, wards, placements, 1, 4)
    ga.seed_schedules()
    count = ga.status_update()
    assert count == 1
    assert ga.last_fitness == ga.schedules[0]['fitness']

def test_change_detected_no_change_check():
    wards = [Ward([0, 'WardA', 'DepartmentB', 4, 'Low/Medium', 3, 2, 3, 2]),Ward([1, 'WardB', 'DepartmentA', 1, 'Low/Medium', 2, 2, 0, 1])]
    placements = [Placement([0, 'A_P1,E1', 'CohortA', 2, 1, '2020/01/01', 'P2', "['WardA','WardB']", "['DepA','DepB']", 'Low/Medium'])]
    slots = [Slot([0,'1']),Slot([1,'2']),Slot([2,'3']),Slot([3,'4'])]
    ga = GeneticAlgorithm(slots, wards, placements, 1, 4)
    ga.seed_schedules()

    ga.last_fitness = ga.schedules[0]['fitness']
    ga.max_no_change_iterations = 1

    continue_eval, sch = ga.no_change_check()

    assert continue_eval == False
    assert sch == ga.schedules[0]['schedule']

def test_no_change_detected_no_change_check():
    wards = [Ward([0, 'WardA', 'DepartmentB', 4, 'Low/Medium', 3, 2, 3, 2]),Ward([1, 'WardB', 'DepartmentA', 1, 'Low/Medium', 2, 2, 0, 1])]
    placements = [Placement([0, 'A_P1,E1', 'CohortA', 2, 1, '2020/01/01', 'P2', "['WardA','WardB']", "['DepA','DepB']", 'Low/Medium'])]
    slots = [Slot([0,'1']),Slot([1,'2']),Slot([2,'3']),Slot([3,'4'])]
    ga = GeneticAlgorithm(slots, wards, placements, 1, 4)
    ga.seed_schedules()

    continue_eval, sch = ga.no_change_check()

    assert continue_eval == True
    assert sch == None

def test_evaluate():
    wards = [Ward([0, 'WardA', 'DepartmentB', 4, 'Low/Medium', 3, 2, 3, 2]),Ward([1, 'WardB', 'DepartmentA', 1, 'Low/Medium', 2, 2, 0, 1])]
    placements = [Placement([0, 'A_P1,E1', 'CohortA', 2, 1, '2020/01/01', 'P2', "['WardA','WardB']", "['DepA','DepB']", 'Low/Medium'])]
    slots = [Slot([0,'1']),Slot([1,'2']),Slot([2,'3']),Slot([3,'4'])]
    ga = GeneticAlgorithm(slots, wards, placements, 1, 4)
    ga.seed_schedules()

    continue_eval, chosen_schedule, fitness, iter_count, schedule_fitnesses = ga.evaluate()

    assert continue_eval == True
    assert chosen_schedule == None
    assert fitness == ga.schedules[0]['fitness']
    assert iter_count == 1
    assert schedule_fitnesses[0] == ga.schedules[0]['fitness']

def test_change_detected_evaluate():
    wards = [Ward([0, 'WardA', 'DepartmentB', 4, 'Low/Medium', 3, 2, 3, 2]),Ward([1, 'WardB', 'DepartmentA', 1, 'Low/Medium', 2, 2, 0, 1])]
    placements = [Placement([0, 'A_P1,E1', 'CohortA', 2, 1, '2020/01/01', 'P2', "['WardA','WardB']", "['DepA','DepB']", 'Low/Medium'])]
    slots = [Slot([0,'1']),Slot([1,'2']),Slot([2,'3']),Slot([3,'4'])]
    ga = GeneticAlgorithm(slots, wards, placements, 1, 4)
    ga.seed_schedules()

    ga.fitness_threshold = 0.2
    ga.last_fitness = ga.schedules[0]['fitness']
    ga.max_no_change_iterations = 1

    continue_eval, chosen_schedule, fitness, iter_count, schedule_fitnesses = ga.evaluate()

    assert continue_eval == False
    assert chosen_schedule == ga.schedules[0]['schedule']
    assert fitness == ga.schedules[0]['fitness']
    assert iter_count == 1
    assert schedule_fitnesses[0] == ga.schedules[0]['fitness']


def test_execute_mutation():
    wards = [Ward([0, 'WardA', 'DepartmentB', 4, 'Low/Medium', 3, 2, 3, 2]),Ward([1, 'WardB', 'DepartmentA', 1, 'Low/Medium', 2, 2, 0, 1])]
    placements = [Placement([0, 'A_P1,E1', 'CohortA', 2, 1, '2020/01/01', 'P2', "['WardA','WardB']", "['DepA','DepB']", 'Low/Medium'])]
    slots = [Slot([0,'1']),Slot([1,'2']),Slot([2,'3']),Slot([3,'4'])]
    ga = GeneticAlgorithm(slots, wards, placements, 100, 4)
    ga.seed_schedules()

    ga.execute_mutation()
    assert len(ga.new_schedules) > 1

    for i in range(0,len(ga.new_schedules)):
        assert ga.new_schedules[i]['fitness'] > 0
        assert isinstance(ga.new_schedules[i]['schedule'], Schedule) == True
        assert ga.new_schedules[i]['sched_id'] >= 0
        assert ga.new_schedules[i]['sched_id'] <= 9999

def test_select_parents():
    wards = [Ward([0, 'WardA', 'DepartmentB', 4, 'Low/Medium', 3, 2, 3, 2]),Ward([1, 'WardB', 'DepartmentA', 1, 'Low/Medium', 2, 2, 0, 1])]
    placements = [Placement([0, 'A_P1,E1', 'CohortA', 2, 1, '2020/01/01', 'P2', "['WardA','WardB']", "['DepA','DepB']", 'Low/Medium'])]
    slots = [Slot([0,'1']),Slot([1,'2']),Slot([2,'3']),Slot([3,'4'])]
    ga = GeneticAlgorithm(slots, wards, placements, 100, 4)
    ga.seed_schedules()

    parents_list = ga.select_parents()

    assert len(parents_list) > 0
    for i in range(0,len(parents_list)):
        print(parents_list[i])
        assert isinstance(parents_list[i][0], int) == True
        assert isinstance(parents_list[i][1], int) == True

def test_generate_offspring():
    wards = [Ward([0, 'WardA', 'DepartmentB', 4, 'Low/Medium', 3, 2, 3, 2]),Ward([1, 'WardB', 'DepartmentA', 4, 'Low/Medium', 2, 2, 2, 1])]
    placements = [Placement([0, 'A_P1,E1', 'CohortA', 2, 1, '2020/01/01', 'P2', "['WardA','WardB']", "['DepA','DepB']", 'Low/Medium'])]
    slots = [Slot([0,'1']),Slot([1,'2']),Slot([2,'3']),Slot([3,'4'])]
    ga = GeneticAlgorithm(slots, wards, placements, 10, 4)
    ga.seed_schedules()

    ga.generate_offspring(ga.select_parents())

    assert len(ga.new_schedules) > 1
    for i in range(0,len(ga.new_schedules)):
        assert ga.new_schedules[i]['fitness'] > 0
        assert isinstance(ga.new_schedules[i]['schedule'], Schedule) == True
        assert ga.new_schedules[i]['sched_id'] >= 0
        assert ga.new_schedules[i]['sched_id'] <= 9999


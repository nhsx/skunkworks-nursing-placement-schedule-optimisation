from xmlrpc.client import Boolean
from src.Schedule import Schedule
from utils.utils import get_time_now
from operator import itemgetter
from datetime import datetime
import numpy as np
import random
import streamlit as st
import yaml
from random import randrange
from typing import Tuple
import logging


class GeneticAlgorithm:
    """
    The Genetic Algorithm object is what drives the process behind the tool, orchestrating the generation, evolution and 
    evaluation of the schedules to determine the option that best matches the criteria. It contains functionality to generate schedules, evolve them and evaluate when
    the best option has been identified.

    For more detail see documentation at docs/ga.md
    
    :param slots: A list of all potential placement week positions
    :param wards: A list of all potential wards that placements can be taken on
    :param placements: A list of all placements to be allocated
    :param number_of_schedules: Integer number of schedules to be produced (dictates the population size)
    :param num_weeks: Integer number of weeks that placements will take place over
    """

    def __init__(
        self,
        slots: list,
        wards: list,
        placements: list,
        number_of_schedules: int,
        num_weeks: int,
    ):
        self.slots = slots
        self.wards = wards
        self.placements = placements
        self.number_of_schedules = number_of_schedules
        self.num_weeks = num_weeks

        self.schedules = []
        self.new_schedules = []

        self.iteration_count = 0

        with open("config/params.yml") as f:
            params = yaml.load(f, Loader=yaml.FullLoader)

        ga_params = params["genetic_algorithm_params"]
        self.new_schedule_count = int(
            self.number_of_schedules
            * ga_params["new_schedule_prop"]
        )

        self.mutation_probability = ga_params["mutationProbability"]
        self.recombination_probability = ga_params["recombinationProbability"]
        self.num_mutations = ga_params["num_mutations"]  # Note that this is number of mutations per schedule
        self.recomb_points = ga_params["recomb_points"]
        self.max_no_change_iterations = ga_params["max_no_change_iterations"]
        self.fitness_threshold = ga_params["fitness_threshold"]
        self.changed_protected_proportion = ga_params["changed_protected_proportion"]

        self.last_fitness = 0
        self.no_change_count = 0

    def generate_new_schedule(self):
        """
        Function to generate new schedule and calculate fitness score

        :returns: a populated Schedule object 
        """
        schedule_obj = Schedule(
                self.slots, self.wards, self.placements, self.num_weeks
            )
        schedule_obj.schedule_generation()
        schedule_obj.get_fitness()
        return schedule_obj

    def seed_schedules(self):
        """
        Function to initialise the first generation of schedules
        """
        for i in range(0, self.number_of_schedules):
            schedule_obj = self.generate_new_schedule()
            self.schedules.append(
                {
                    "schedule": schedule_obj,
                    "fitness": schedule_obj.fitness,
                    "sched_id": randrange(9999),
                }
            )



    def viable_schedule_check(self) -> Tuple[bool, object, list]:
        """
        Function to check whether a viable schedule exists with the prequisite level of fitness

        :returns: bool to determine whether evaluation should continue, a schedule and a list of schedule fitnesses
        """
        continue_eval = True
        schedule_fitnesses = []
        for schedule in self.schedules:
            schedule["schedule"].populate_schedule()
            schedule_fitnesses.append(schedule["schedule"].fitness)
            if (schedule["schedule"].fitness > self.fitness_threshold) and (
                schedule["schedule"].viable
            ):
                schedule["schedule"].save_report()
                logging.info(
                    f'Viable schedule identified with fitness of {schedule["schedule"].fitness}, saving'
                )
                continue_eval = False
                return continue_eval, schedule["schedule"], schedule_fitnesses
        if continue_eval:
            return continue_eval, None, schedule_fitnesses

    def status_update(self):
        """
        Function to output status update to demonstrate progress in evolving schedules

        :returns: current count of iterations
        """
        total_schedules = len(self.schedules)
        if self.last_fitness < self.schedules[total_schedules - 1]["fitness"]:
            now = get_time_now()
            self.last_fitness = self.schedules[total_schedules - 1]["fitness"]
            logging.info(
                f'At {now} the best fitness in generation is schedule {self.schedules[total_schedules - 1]["sched_id"]} with: {self.last_fitness}'
            )
            self.no_change_count = 0
        self.iteration_count += 1
        return self.iteration_count

    def no_change_check(self) -> Tuple[bool, object]:
        """
        Function to check whether there is a new fittest schedule after another round of evolution

        :returns: bool to determine whether evaluation should continue and a schedule
        """
        total_schedules = len(self.schedules)
        continue_eval = True
        logging.info(
            f'No change detected: {self.last_fitness == self.schedules[total_schedules - 1]["fitness"]}, no change number {self.no_change_count}'
        )
        if self.last_fitness == self.schedules[total_schedules - 1]["fitness"]:
            self.no_change_count += 1
            if self.no_change_count >= self.max_no_change_iterations:
                self.schedules[total_schedules - 1]["schedule"].populate_schedule()
                self.schedules[total_schedules - 1]["schedule"].save_report()
                self.schedules[total_schedules - 1]["schedule"].get_fitness()
                logging.info(
                    f"The algorithm has passed more then {self.max_no_change_iterations} without an improvement in fitness, program terminating"
                )
                continue_eval = False
                return continue_eval, self.schedules[total_schedules - 1]["schedule"]

        if continue_eval:
            self.last_fitness = self.schedules[total_schedules - 1]["fitness"]
            return continue_eval, None

    def evaluate(self) -> Tuple[bool, object, float, int, list]:
        """
        Function to evaluate the fitness of the existing cohort of schedules

        :returns: bool to determine if evaluation should continue and then details on current best schedule
        """
        (
            continue_eval,
            chosen_schedule,
            schedule_fitnesses,
        ) = self.viable_schedule_check()
        iter_count = self.status_update()
        if continue_eval:
            continue_eval, chosen_schedule = self.no_change_check()
        if chosen_schedule is None:
            fitness = self.last_fitness
        else:
            fitness = chosen_schedule.fitness
        return continue_eval, chosen_schedule, fitness, iter_count, schedule_fitnesses

    def execute_mutation(self):
        """
        Function to randomly determine which schedules should be mutated

        :returns: no explicit return but populates new_schedules class object
        """
        self.new_schedules = []
        # Mutate a proportion of the schedules
        for mutation_index in range(0, len(self.schedules) - 1):
            if random.uniform(0, 1) <= self.mutation_probability:
                mutuated_schedule = self.schedules[mutation_index]["schedule"].mutation(
                    self.num_mutations
                )
                self.new_schedules.append(
                    {
                        "schedule": mutuated_schedule,
                        "fitness": mutuated_schedule.fitness,
                        "sched_id": randrange(9999),
                    }
                )

    def select_parents(self) -> int:
        """
        Function to use a roulette wheel approach (i.e. probability of selection is
        proportional to fitness of schedule) to select parents for recombination

        :returns: a list of schedules to be used as parents for recombination
        """
        total_fitness = 0
        population_size = len(self.schedules)
        for schedule in self.schedules:
            total_fitness += schedule["fitness"]

        prob_selection = [i / total_fitness for i in range(population_size)]
        cum_prob = np.cumsum(prob_selection)
        select_indices = [random.random() for i in range(population_size)]
        selected_parents = []

        for parent_one_index in range(population_size):
            for parent_two_index in range(population_size):
                if (
                    cum_prob[parent_two_index] < (select_indices[parent_one_index])
                    and cum_prob[parent_two_index + 1]
                    >= select_indices[parent_one_index]
                ):
                    pair = (parent_one_index, parent_two_index)
                    if parent_one_index != parent_two_index:
                        selected_parents.append(pair)

        return selected_parents

    def generate_offspring(self, selected_parents: list):
        """
        Function to produce offspring through recombination using a selected set of parents

        :param selected_parents: a list of schedules to be used as parents for recombination
        :returns: no explicit return but populates new_schedules class object with recombined schedules
        """
        for pair in selected_parents:
            if random.uniform(0, 1) <= self.recombination_probability:
                offspring_schedules = self.schedules[pair[0]]["schedule"].recombination(
                    self.schedules[pair[1]]["schedule"],
                    int(np.round(self.num_weeks / self.recomb_points, 0)),
                    1,
                )
                for schedule in offspring_schedules:
                    schedule.get_fitness()
                    self.new_schedules.append(
                        {
                            "schedule": schedule,
                            "fitness": schedule.fitness,
                            "sched_id": randrange(9999),
                        }
                    )

    def culling(self, num_new_schedules: int):
        """
        Function to prevent population stagnating, introduce proportion of newly generated schedules each round

        :param num_new_schedules: the integer number of new schedules to be generated/to be replaced in existing population
        :returns: no explicit return but populates new_schedules class object with newly generated schedules
        """
        for i in range(0, num_new_schedules):
            schedule_obj = self.generate_new_schedule()
            self.new_schedules.append(
                {
                    "schedule": schedule_obj,
                    "fitness": schedule_obj.fitness,
                    "sched_id": randrange(9999),
                }
            )

    def update_population(self):
        """
        Function to using mutated schedules and offspring, replace the least fit schedules

        :returns: no explicit return but replaces lowest scoring schedules in schedules class object with newly generated ones
        """
        self.schedules = sorted(self.schedules, key=itemgetter("fitness"))
        # Update schedules of all but the top X %
        for i in range(
            0,
            min(
                len(self.new_schedules),
                int(len(self.schedules) * (1 - self.changed_protected_proportion)),
            ),
        ):
            self.schedules[i] = self.new_schedules[i]

    def evolve(self) -> Tuple[bool, object, float, int, list]:
        """
        Function to execute the genetic algorithm until convergence or no change found

        :returns: bool to determine if evaluation should continue as well as details on best performing schedule
        """
        self.new_schedules = []
        self.culling(self.new_schedule_count)
        self.execute_mutation()
        self.generate_offspring(self.select_parents())
        self.update_population()
        (
            continue_eval,
            chosen_schedule,
            fitness,
            iteration,
            schedule_fitnesses,
        ) = self.evaluate()
        return continue_eval, chosen_schedule, fitness, iteration, schedule_fitnesses

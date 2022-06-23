from src.Schedule import Schedule
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
    
    param: slots: A list of all potential placement week positions
    param: wards: A list of all potential wards that placements can be taken on
    param: placements: A list of all placements to be allocated
    param: number_of_schedules: Integer number of schedules to be produced (dictates the population size)
    param: num_weeks: Integer number of weeks that placements will take place over
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

        self.new_schedule_count = int(
            self.number_of_schedules
            * params["genetic_algorithm_params"]["new_schedule_prop"]
        )

        self.mutation_probability = params["genetic_algorithm_params"][
            "mutationProbability"
        ]
        self.recombination_probability = params["genetic_algorithm_params"][
            "recombinationProbability"
        ]
        self.num_mutations = params["genetic_algorithm_params"][
            "num_mutations"
        ]  # Note that this is number of mutations per schedule
        self.recomb_points = params["genetic_algorithm_params"]["recomb_points"]
        self.max_no_change_iterations = params["genetic_algorithm_params"][
            "max_no_change_iterations"
        ]
        self.fitness_threshold = params["genetic_algorithm_params"]["fitness_threshold"]
        self.changed_protected_proportion = params["genetic_algorithm_params"][
            "changed_protected_proportion"
        ]

        self.last_fitness = 0
        self.no_change_count = 0

    def seed_schedules(self):
        """
        Initiase the first generation of schedules
        """
        for i in range(0, self.number_of_schedules):
            schedule_obj = Schedule(
                self.slots, self.wards, self.placements, self.num_weeks
            )
            schedule_obj.schedule_generation()
            schedule_obj.get_fitness()
            self.schedules.append(
                {
                    "schedule": schedule_obj,
                    "fitness": schedule_obj.fitness,
                    "sched_id": randrange(9999),
                }
            )

    def viable_schedule_check(self) -> Tuple[bool, list, str, float]:
        """
        Check whether a viable schedule exists with the prequisite level of fitness
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
        Output status update to demonstrate progress in evolving schedules
        """
        total_schedules = len(self.schedules)
        if self.last_fitness < self.schedules[total_schedules - 1]["fitness"]:
            now = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            self.last_fitness = self.schedules[total_schedules - 1]["fitness"]
            logging.info(
                f'At {now} the best fitness in generation is schedule {self.schedules[total_schedules - 1]["sched_id"]} with: {self.last_fitness}'
            )
            self.no_change_count = 0
        self.iteration_count += 1
        return self.iteration_count

    def no_change_check(self):
        """
        Check whether there is a new fittest schedule after another round of evolution
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

    def evaluate(self):
        """
        Evaluate the fitness of the existing cohort of schedules
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
        Randomly determines which schedules should be mutated
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

    def select_parents(self):
        """
        Using a roulette wheel approach (i.e. probability of selection is
        proportional to fitness of schedule), parents for recombination
        are selected
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

    def generate_offspring(self, selected_parents):
        """
        Using a selected set of parents, produce offspring through
        recombination
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

    def culling(self, num_new_schedules):
        """
        To prevent population stagnating, introduce proportion of newly generated schedules each round
        """
        for i in range(0, num_new_schedules):
            schedule_obj = Schedule(
                self.slots, self.wards, self.placements, self.num_weeks
            )
            schedule_obj.schedule_generation()
            schedule_obj.get_fitness()
            self.new_schedules.append(
                {
                    "schedule": schedule_obj,
                    "fitness": schedule_obj.fitness,
                    "sched_id": randrange(9999),
                }
            )

    def update_population(self):
        """
        Using mutated schedules and offspring, replace the least fit schedules
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

    def evolve(self):
        """
        Execute the genetic algorithm until convergence or no change found
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

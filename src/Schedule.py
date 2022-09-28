from random import randint, shuffle, randrange
import copy
import math
import collections
from xmlrpc.client import Boolean
import pandas as pd
import numpy as np
from datetime import datetime
import re
from typing import Tuple
import yaml
import os
import logging
import warnings
from utils.utils import get_time_now


class Schedule:
    """
    A Schedule object contains a complete set of student placements across all wards. When the genetic algorithm is run there are many 
    Schedule objects which are manipulated and scored to try and reach the best possible solution.

    param: conf_placements: An empty list for confirmed placements to be stored in
    param total_slots: An integer number of empty lists to be inserted into slots
    param: slots: An empty list of lists for slots to be created in
    param: wards: A list of Ward objects where placements can take place
    param: placements: A list of Placement objects to be assigned
    param: placement_slots: A list of Slot objects for placements on wards to be assigned into
    param: num_weeks: An integer number of the length of time that placements need to be allocated for
    param: generation: An integer initialising the generation of this schedule
    param: fitness: A float initialising the fitness score for this schedule
    param: viable: A Boolean initialising the viability of this schedule
    param: non_viable_reason: A None string initialising the explanation for why the schedule is not viable
    """

    def __init__(self, slots: list, wards: list, placements: list, num_weeks: int):
        self.conf_placements = []
        self.slots = []
        total_slots = len(slots) * len(wards)
        self.slots = [[] for _ in range(0, total_slots)]

        self.wards = wards
        self.placements = placements
        self.placement_slots = slots

        self.num_weeks = num_weeks
        self.generation = 1
        self.fitness = 0.0
        self.viable = False
        self.non_viable_reason = None

        with open("config/params.yml") as f:
            params = yaml.load(f, Loader=yaml.FullLoader)

        self.medical_placement_check = params["schedule_params"][
            "medical_placement_check"
        ]
        self.surgical_placement_check = params["schedule_params"][
            "surgical_placement_check"
        ]
        self.community_placement_check = params["schedule_params"][
            "community_placement_check"
        ]
        self.critical_care_placement_check = params["schedule_params"][
            "critical_care_placement_check"
        ]

        self.within_capacity_scoring_factor = params["schedule_params"][
            "within_capacity_scoring_factor"
        ]
        self.double_booked_scoring_factor = params["schedule_params"][
            "double_booked_scoring_factor"
        ]
        self.correct_num_wards_scoring_factor = params["schedule_params"][
            "correct_num_wards_scoring_factor"
        ]
        self.uniq_departments_scoring_factor = params["schedule_params"][
            "uniq_departments_scoring_factor"
        ]
        self.uniq_wards_scoring_factor = params["schedule_params"][
            "uniq_wards_scoring_factor"
        ]
        self.all_placements_assigned_scoring_factor = params["schedule_params"][
            "all_placements_assigned_scoring_factor"
        ]
        self.capacity_utilisation_scoring_factor = params["schedule_params"][
            "capacity_utilisation_scoring_factor"
        ]

        self.medical_placement_scoring_factor = params["schedule_params"][
            "medical_placement_scoring_factor"
        ]
        self.surgical_placement_scoring_factor = params["schedule_params"][
            "surgical_placement_scoring_factor"
        ]
        self.community_placement_scoring_factor = params["schedule_params"][
            "community_placement_scoring_factor"
        ]
        self.critical_care_placement_scoring_factor = params["schedule_params"][
            "critical_care_placement_scoring_factor"
        ]

    def id_year_capacity(self, placement: "placement", ward_id: int) -> int:
        """
        Function to identify the year-specific capacity relevant for a given placement

        :param placement: the placement object
        :param ward_id: id of the ward as per original data
        :returns: capacity for the specific type of placement and ward
        """

        if placement.part == "P1":
            year_cap = self.wards[ward_id].p1_capacity
        elif placement.part == "P2":
            year_cap = self.wards[ward_id].p2_capacity
        elif placement.part == "P3":
            year_cap = self.wards[ward_id].p3_capacity
        else:
            year_cap = self.wards[ward_id].capacity

        return year_cap

    def calc_slot_index(self, ward_id: int, num_weeks: int, start_week: int) -> int:
        """
        Function to calculate the index for the slot based on the id of the ward,
        the total number of weeks the schedule is produced over and
        the start week of the placement

        :param ward_id: id of the ward as per original data
        :param num_weeks: total integer number of weeks the entire schedule covers
        :param start_week: week number that the placement starts in
        :returns: the id within the slots class object that the placement starts on
        """

        return int((ward_id * num_weeks) + start_week + 1)

    def schedule_generation(self):
        """
        Function to initialise a schedule which is generated by randomly choosing a
        ward for the placement to occur on

        :returns: no explicit return but populates conf_placements class object
        """

        for p in self.placements:
            placement_duration = int(p.duration)
            invalid_ward = True

            # Find a ward which valid based on capacity and education audit
            ward_ids = set()
            while invalid_ward:
                invalid_ward = False
                if len(ward_ids) == len(self.wards):
                    warnings.warn('No valid ward is available for placement to be allocated to, random ward assigned')
                    ward_id = randint(0, len(self.wards) - 1)
                    break
                ward_id = randint(0, len(self.wards) - 1)
                ward_ids.add(ward_id)
                slot_index_increment = self.calc_slot_index(
                    ward_id, self.num_weeks, p.start
                )

                year_cap = self.id_year_capacity(p, ward_id)
                if year_cap == 0:
                    invalid_ward = True
                else:
                    for i in range(0, placement_duration):
                        # Check if overall capacity breached or ward has expired education audit
                        if (
                            len(self.slots[slot_index_increment])
                            >= self.wards[ward_id].capacity
                        ) or (
                            (p.covid_status == "Low/Medium")
                            and (self.wards[ward_id].covid_status == "Medium/High")
                        ):
                            invalid_ward = True
                            break
                        else:
                            # If overall cap and education audit are fine, check whether year-specific capacity satisfied
                            same_year_count = 0
                            for plac in self.slots[slot_index_increment]:
                                if plac.part == p.part:
                                    same_year_count += 1
                            if same_year_count >= year_cap:
                                invalid_ward = True
                            if invalid_ward:
                                break
                        slot_index_increment += 1

            # Now that ward has been identified, populate schedule
            overall_slot_index = self.calc_slot_index(ward_id, self.num_weeks, p.start)
            slot_index_increment = overall_slot_index
            for i in range(0, placement_duration):
                self.slots[slot_index_increment].append(p)
                slot_index_increment += 1

            self.conf_placements.append(
                {
                    "placement": p,
                    "slotIndex": overall_slot_index,
                    "startweek": p.start,
                    "length": placement_duration,
                }
            )

    def clean_departments(self, output_string: str) -> list:
        """
        Function to clean up a list of department names for analysis. Removes some non-required words.

        :params output_string: the string to be cleaned, containing multiple department names
        :returns: a clean list of individual words seen in original string
        """
        replace_dict = {
            ",": "",
            "and": "",
            "the": "",
            "of": "",
            "eneral": "general",
            "None": "",
            "-": "",
            "\xa0": "",
            "  ": " ",
        }
        for word, replacement in replace_dict.items():
            output_string = output_string.replace(word, replacement)
        output_string = output_string.lower()
        output_list = output_string.split(" ")
        output_list = list(filter(None, output_list))
        return output_list

    def get_fitness(self):
        """
        Function to assess the fitness of each schedule according to a range of metrics

        :returns: no explicit return but updates various class object parameters
        """
        self.schedule_scores = 0
        self.placement_wards = collections.defaultdict(list)
        self.placement_deps = collections.defaultdict(list)
        self.viable = None  # Viable variable indicates whether a schedule
        # could be used i.e. no hard constraints
        # are breached

        self.schedule_eval_scores = {}
        self.schedule_eval_scores["cap_exceeded_score"] = 0
        self.schedule_eval_scores["double_booked_score"] = 0
        ward_utilisation = []

        # Create a list of placements to be allocated, so we can check
        # later whether all placements allocated in a schedule
        placementsToAllocate = [p.id for p in self.placements]
        for confirmed_placement in self.conf_placements:
            schedule_score_component = 0

            if confirmed_placement["placement"].id in placementsToAllocate:
                placementsToAllocate.remove(confirmed_placement["placement"].id)

            placement_index = int(confirmed_placement["slotIndex"])
            ward_index = int(math.floor(placement_index / len(self.placement_slots)))

            ward = self.wards[ward_index]

            # Add Ward and Speciality to each nurse's individual list
            nurse_name = confirmed_placement["placement"].name.split("_", maxsplit=1)[0]

            # Maximise variety of wards
            if not self.placement_wards[nurse_name]:
                previous_wards = confirmed_placement["placement"].wardhistory.split(
                    ", "
                )
                for old_ward in previous_wards:
                    self.placement_wards[nurse_name].append(old_ward)

            self.placement_wards[nurse_name].append(ward.ward)
            # Maximise variety of specialities
            if not self.placement_deps[nurse_name]:
                previous_departments = self.clean_departments(
                    confirmed_placement["placement"].dephistory
                )
                self.placement_deps[nurse_name] = previous_departments

            dep_clean = self.clean_departments(ward.department)
            for dep_word in dep_clean:
                self.placement_deps[nurse_name].append(dep_word)

            # Check if wards have exceeded capacity of assigned placements #
            year_cap = self.id_year_capacity(
                confirmed_placement["placement"], ward_index
            )

            year_count = 0
            for oth_placement in self.slots[placement_index]:
                if oth_placement.part == confirmed_placement["placement"].part:
                    year_count += 1

            if (
                len(self.slots[placement_index]) <= self.wards[ward_index].capacity
            ) and (year_count <= year_cap):
                schedule_score_component += self.within_capacity_scoring_factor
                self.schedule_eval_scores[
                    "cap_exceeded_score"
                ] += self.within_capacity_scoring_factor
            else:
                schedule_score_component = 0
                self.schedule_eval_scores["cap_exceeded_score"] = 0
                self.viable = False
                self.non_viable_reason = "Cap Exceeded"

            if self.wards[ward_index].capacity != 0:
                ward_utilisation.append(
                    len(self.slots[placement_index]) / self.wards[ward_index].capacity
                )
            else:
                ward_utilisation.append(0)

            # Check if student's covid status can accommodate selected ward
            if (confirmed_placement["placement"].covid_status == "Low/Medium") and (
                self.wards[ward_index].covid_status == "Medium/High"
            ):
                schedule_score_component = 0
                self.viable = False
                self.non_viable_reason = "Covid status not compatible"

            # Check if student has another placement arranged for a different
            # ward at the same time ##
            double_booked = False
            for id in range(1, len(self.wards)):
                if id != ward_index:
                    indexForChecking = self.calc_slot_index(
                        id, len(self.placement_slots), confirmed_placement["startweek"]
                    )
                    if indexForChecking == placement_index:
                        continue

                    if len(self.slots[indexForChecking]):
                        for potential_match in self.slots[indexForChecking]:
                            if (
                                potential_match.name
                                == confirmed_placement["placement"].name
                            ):
                                double_booked = True
                                break
                    else:
                        continue
            if not double_booked:
                schedule_score_component += self.double_booked_scoring_factor
                self.schedule_eval_scores[
                    "double_booked_score"
                ] += self.double_booked_scoring_factor
            else:
                self.viable = False
                self.non_viable_reason = "Double booked"
                schedule_score_component = 0
                self.schedule_eval_scores["double_booked_score"] = 0
            self.schedule_scores += schedule_score_component

        self.schedule_eval_scores["mean_ward_util"] = sum(ward_utilisation) / len(
            ward_utilisation
        )

        mean_uniq_wards_list = []
        for assigned_wards in self.placement_wards.values():
            mean_uniq_wards_list.append(len(set(assigned_wards)) / len(assigned_wards))
        prop_uniq_wards = sum(mean_uniq_wards_list) / len(mean_uniq_wards_list)
        self.add_score(self.uniq_wards_scoring_factor * prop_uniq_wards)
        self.schedule_eval_scores["mean_uniq_wards"] = prop_uniq_wards

        ## Reward schedules which have a unique set of departments ##
        mean_uniq_deps_list = []
        for assigned_departments in self.placement_deps.values():
            mean_uniq_deps_list.append(
                len(set(assigned_departments)) / len(assigned_departments)
            )

        mean_uniq_deps = sum(mean_uniq_deps_list) / len(mean_uniq_deps_list)
        self.add_score(self.uniq_departments_scoring_factor * mean_uniq_deps)

        self.schedule_eval_scores["mean_uniq_deps"] = mean_uniq_deps

        ####################################################################################
        ## NOTE THAT THE BELOW IS CURRENT TURNED OFF USING BOOLEANS SET AT START OF CLASS ##
        ####################################################################################

        ## Enforce at least one Medical placement
        ## Increase score if assigned to a Medical ward ##
        self.check_specific_speciality(
            self.medical_placement_check,
            ["Medical", "Medicine"],
            self.medical_placement_scoring_factor,
        )

        ## Increase score if assigned to a Surgical ward ##
        self.check_specific_speciality(
            self.surgical_placement_check,
            ["Surgical", "Surgery"],
            self.surgical_placement_scoring_factor,
        )

        ## Increase score if assigned to a Community ward ##
        self.check_specific_speciality(
            self.community_placement_check,
            ["Community"],
            self.community_placement_scoring_factor,
        )

        ## Increase score if assigned to a Critical Care ward ##
        self.check_specific_speciality(
            self.critical_care_placement_check,
            ["Critical", "Emergency"],
            self.critical_care_placement_scoring_factor,
        )

        ## Increase fitness if all placements assigned ##
        if len(placementsToAllocate) == 0:
            self.add_score(self.all_placements_assigned_scoring_factor)
        else:
            self.viable = False
            self.non_viable_reason = "Placement not allocated"

        ## Increase fitness based on placement capacity utilisation #
        avg_utilisation = sum(ward_utilisation) / len(ward_utilisation)
        self.add_score(avg_utilisation * self.capacity_utilisation_scoring_factor)

        # Calculate maximum score
        max_score = (  # Must have scoring components
            (len(self.conf_placements) * self.within_capacity_scoring_factor)
            + (  # Exceeded capacity component
                len(self.conf_placements) * self.double_booked_scoring_factor
            )
            + (  # Double booked component
                len(self.conf_placements) * self.all_placements_assigned_scoring_factor
            )
            +  # All placements allocated component
            # Nice to have scoring components
            (self.uniq_departments_scoring_factor)
            + (self.uniq_wards_scoring_factor)  # Unique departments component
            + (self.capacity_utilisation_scoring_factor)  # Unique wards component
            +  # Average utilisation component
            # Speciality specific scoring components
            (
                self.medical_placement_check
                * len(self.placement_wards.values())
                * self.medical_placement_scoring_factor
            )
            + (  # Medical ward component
                self.surgical_placement_check
                * len(self.placement_wards.values())
                * self.surgical_placement_scoring_factor
            )
            + (  # Surgical ward component
                self.community_placement_check
                * len(self.placement_wards.values())
                * self.community_placement_scoring_factor
            )
            + (  # Community ward component
                self.critical_care_placement_check
                * len(self.placement_wards.values())
                * self.critical_care_placement_scoring_factor
            )  # High Dependency ward component
        )
        self.fitness = float(self.schedule_scores) / max_score


        if self.viable is None:
            self.viable = True

    def check_specific_speciality(
        self, check_boolean: Boolean, check_words: list, check_score: int
    ):
        """
        Function to check presence of specific words in specialities list for a student
        """
        if check_boolean:
            check_words_regex = re.compile("|".join(check_words))
            for assigned_departments in self.placement_deps.values():
                print(assigned_departments)
                for dep in assigned_departments:
                    if check_words_regex.search(dep):
                        self.add_score(check_score)

    def add_score(self, score: float):
        """
        Function to add score value to all schedule entries

        :param score: score to be added to overall total
        :returns: no explicit return but updates schedule_scores object
        """
        self.schedule_scores += score

    def populate_schedule(self):
        """
        Function to reconstruct schedules after mutations and recombination to make sure
        that placements are still structured correctly (prevents
        mutation/recombination from putting lots of incorrectly located
        placements in the schedule)

        :returns: no explicit return but updates slots class object
        """
        self.slots = [[] for _ in range(len(self.slots))]
        for confirmed_placement in self.conf_placements:
            slotIndex = int(confirmed_placement["slotIndex"])
            for i in range(0, confirmed_placement["length"]):
                self.slots[slotIndex].append(confirmed_placement["placement"])
                slotIndex += 1
        self.get_fitness()

    def recombination(
        self, otherparent: object, num_recomb_points: int, num_offspring: int
    ) -> list:
        """
        Function to produce offspring by combining two parent schedules,
        with 2 crossing points. This will yield:
        p1 = [0 0 0 1 1 0 0 1 0 1]
        p2 = [1 0 1 0 0 0 1 0 0 0]
        p1 [combined with] p2 = [0 0|1 0 0 0 1|1 0 1]
        which corresponds to [p1 | p2 | p1] being combined after
        the 3rd and 7th indices

        :param otherparent: other schedule for recombination to be carried out with
        :param num_recomb_points: integer number of crossing over points to be used
        :param num_offspring: integer number of offspring to produce
        :returns: list of recombined schedule objects
        """
        pop_size = len(self.conf_placements)
        rcp = []
        for i in range(num_recomb_points, 0, -1):
            check_point = False
            while not check_point:
                p = randrange(pop_size)
                if p not in rcp:
                    rcp.append(p)
                    check_point = True
        rcp = sorted(rcp)

        offspring_list = []
        prev_index = 0

        shuffle(self.conf_placements)
        shuffle(otherparent.conf_placements)

        parents = [self.conf_placements, otherparent.conf_placements]
        first_parent = True
        for i in range(num_offspring):
            offspring = Schedule(
                self.placement_slots, self.wards, self.placements, self.num_weeks
            )
            for index in rcp:
                list_index = rcp.index(index)
                if first_parent:
                    parent_index = 0
                    other_index = 1
                else:
                    parent_index = 1
                    other_index = 0
                if list_index == 0:
                    offspring.conf_placements += parents[parent_index][0:index]
                elif index == rcp[-1]:
                    prev_index = rcp[list_index - 1]
                    offspring.conf_placements += parents[other_index][prev_index:index]
                    offspring.conf_placements += parents[parent_index][index:]
                else:
                    prev_index = rcp[list_index - 1]
                    offspring.conf_placements += parents[parent_index][prev_index:index]
                first_parent = not first_parent
            offspring.generation = max(self.generation, otherparent.generation) + 1
            offspring.populate_schedule()
            offspring_list.append(offspring)

        return offspring_list

    def mutation(self, num_mutations: int) -> object:
        """
        Function to mutate the location of one of the placements within a schedule

        :param num_mutations: integer number of mutations to introduce to mutated schedule
        :returns: mutated schedule object
        """
        mutation_schedule = copy.copy(self)

        for i in range(0, num_mutations):
            placement_index = randint(0, len(mutation_schedule.conf_placements) - 1)
            ward_index = randint(0, len(self.wards) - 1)
            mutation_schedule.conf_placements[placement_index][
                "slotIndex"
            ] = self.calc_slot_index(
                ward_index,
                self.num_weeks,
                mutation_schedule.conf_placements[placement_index]["startweek"],
            )

        mutation_schedule.generation = self.generation + 1
        mutation_schedule.populate_schedule()
        return mutation_schedule

    def produce_dataframe(self) -> pd.DataFrame:
        """
        Function to save results out to a CSV

        :returns: a pandas dataframe summarising the schedule generated
        """
        ward_names = []
        ward_deps = []
        ward_caps = []
        ward_p1_caps = []
        ward_p2_caps = []
        ward_p3_caps = []
        ward_ed_audits = []
        placement_names = []
        placement_cohorts = []
        placement_parts = []
        placement_start = []
        placement_start_dates = []
        placement_durations = []
        placement_week = []
        for i in range(0, len(self.slots)):
            ward_index = int(math.floor(i / len(self.placement_slots)))
            week_index = i - (ward_index * self.num_weeks)
            if i % len(self.placement_slots) == 0:
                ward_name = self.wards[ward_index].ward
                ward_dep = self.wards[ward_index].department
                ward_cap = self.wards[ward_index].capacity
                p1_ward_cap = self.wards[ward_index].p1_capacity
                p2_ward_cap = self.wards[ward_index].p2_capacity
                p3_ward_cap = self.wards[ward_index].p3_capacity
                ward_ed_audit = self.wards[ward_index].ed_audit_expiry_week

            scheduled_placements = self.slots[i]

            for schedule_placement in scheduled_placements:
                if schedule_placement is not None:
                    ward_names.append(ward_name)
                    ward_deps.append(ward_dep)
                    ward_caps.append(ward_cap)
                    ward_p1_caps.append(p1_ward_cap)
                    ward_p2_caps.append(p2_ward_cap)
                    ward_p3_caps.append(p3_ward_cap)
                    ward_ed_audits.append(ward_ed_audit)
                    placement_names.append(schedule_placement.name)
                    placement_cohorts.append(schedule_placement.cohort)
                    placement_parts.append(schedule_placement.part)
                    placement_start.append(schedule_placement.start)
                    placement_start_dates.append(schedule_placement.start_date)
                    placement_week.append(week_index)
                    placement_durations.append(schedule_placement.duration)

        schedule_df = pd.DataFrame(
            {
                "nurse_name": placement_names,
                "nurse_uni_cohort": placement_cohorts,
                "placement_part": placement_parts,
                "placement_start": placement_start,
                "placement_start_date": placement_start_dates,
                "placement_week": placement_week,
                "placement_duration": placement_durations,
                "ward_name": ward_names,
                "department": ward_deps,
                "ward_capacity": ward_caps,
                "p1_ward_capacity": ward_p1_caps,
                "p2_ward_capacity": ward_p2_caps,
                "p3_ward_capacity": ward_p3_caps,
                "ed_audit_exp_week": ward_ed_audits,
            }
        )

        schedule_df.sort_values(
            by=["nurse_name", "placement_start", "placement_week"], inplace=True
        )

        script_directory = os.path.dirname(os.path.abspath(__file__))
        save_directory = os.path.join(script_directory, "..", "results")

        try:
            os.makedirs(save_directory)
        except OSError:
            pass  # already exists

        now = get_time_now()
        full_save_path = os.path.join(save_directory, f"sched_output_{now}.csv")
        schedule_df.to_csv(full_save_path)
        return schedule_df

    def schedule_quality_check(self) -> Tuple[int, int, int, int]:
        """
        Function to do some basic checks to make sure all rules have worked as desired

        :returns: counts of the number of schedules affected by poor quality
        """
        # Check that everyone has all placements assigned
        self.quality_metrics = {}

        schedule = self.produce_dataframe()

        schedule["placement_start_week"] = schedule["placement_week"]
        schedule["nurse_id"] = None
        schedule["block"] = None
        schedule[["nurse_id", "block"]] = schedule["nurse_name"].str.split(
            "_", expand=True, n=1
        )

        schedule["ward_name"] = schedule["ward_name"].fillna("None")
        schedule["placement_week_date"] = pd.to_datetime(
            schedule.placement_start_date.min()
        )
        schedule["placement_offset"] = (schedule["placement_week"] - 1) * 7
        schedule["placement_week_date"] = schedule[
            "placement_week_date"
        ] + pd.to_timedelta(schedule["placement_offset"], unit="d")
        schedule = schedule.drop("placement_offset", axis=1)

        all_assigned_check = schedule[["nurse_name", "block"]]
        all_assigned_check = all_assigned_check.drop_duplicates()
        all_assigned_check_df = pd.DataFrame(
            all_assigned_check.groupby("nurse_name")["block"].count()
        )

        placement_list = [p.name for p in self.placements]
        total_placements_df = pd.DataFrame(placement_list, columns=["placement"])
        total_placements_df[["nurse_name", "placement_title"]] = total_placements_df[
            "placement"
        ].str.split("_", expand=True, n=1)
        student_plac_count = pd.DataFrame(
            total_placements_df.groupby("nurse_name")["placement_title"].count()
        ).reset_index()
        plac_count_compare = all_assigned_check_df.merge(
            student_plac_count, on="nurse_name"
        )
        plac_count_compare.columns = [
            "nurse_id",
            "assigned_count",
            "placement_to_be_assigned",
        ]
        num_incorr_num_plac = plac_count_compare[
            plac_count_compare.assigned_count
            != plac_count_compare.placement_to_be_assigned
        ].shape[0]

        if num_incorr_num_plac > 0:
            incorrect_num_plac_rows = plac_count_compare[
                plac_count_compare.assigned_count
                != plac_count_compare.placement_to_be_assigned
            ]
        else:
            incorrect_num_plac_rows = None
        logging.info(
            f"{num_incorr_num_plac} students have the incorrect number of placements"
        )

        ## Check that all placements are correct length
        placement_length_check = schedule[
            ["nurse_name", "block", "placement_week", "placement_duration"]
        ]
        placement_length_check = placement_length_check.drop_duplicates()
        placement_length_check_df = pd.DataFrame(
            placement_length_check.groupby(["nurse_name", "block"]).agg(
                {"placement_week": "count", "placement_duration": "max"}
            )
        )
        num_incorrect_length = placement_length_check_df[
            placement_length_check_df["placement_week"]
            != placement_length_check_df["placement_duration"]
        ].shape[0]
        if num_incorrect_length > 0:
            incorrect_len_rows = placement_length_check_df[
                placement_length_check_df["placement_week"]
                != placement_length_check_df["placement_duration"]
            ]
        else:
            incorrect_len_rows = None
        logging.info(f"{num_incorrect_length} placements are the incorrect length")

        ## Check whether year-specificcapacity of any of the wards is exceeded
        year_specific_ward_cap = pd.DataFrame(
            schedule.groupby(["ward_name", "placement_part", "placement_week"])[
                "nurse_name"
            ].count()
        )
        year_specific_ward_cap.reset_index(inplace=True)
        year_specific_ward_cap.columns = [
            "ward_name",
            "placement_part",
            "placement_week",
            "assigned_students",
        ]

        capacities = schedule[
            [
                "ward_name",
                "ward_capacity",
                "p1_ward_capacity",
                "p2_ward_capacity",
                "p3_ward_capacity",
            ]
        ].drop_duplicates()

        overall_ward_cap = pd.DataFrame(
            schedule.groupby(["ward_name", "placement_week"])["nurse_name"].count()
        )
        overall_ward_cap.reset_index(inplace=True)
        overall_ward_cap.columns = ["ward_name", "placement_week", "assigned_students"]
        overall_ward_cap["placement_part"] = "All"

        ward_cap = pd.concat([year_specific_ward_cap, overall_ward_cap])
        ward_cap = ward_cap.merge(capacities, on="ward_name")
        ward_cap["cap_exceeded"] = np.where(
            (
                (ward_cap["placement_part"] == "P1")
                & (ward_cap["assigned_students"] > ward_cap["p1_ward_capacity"])
            )
            | (
                (ward_cap["placement_part"] == "P2")
                & (ward_cap["assigned_students"] > ward_cap["p2_ward_capacity"])
            )
            | (
                (ward_cap["placement_part"] == "P3")
                & (ward_cap["assigned_students"] > ward_cap["p3_ward_capacity"])
            )
            | (
                (ward_cap["placement_part"] == "All")
                & (ward_cap["assigned_students"] > ward_cap["ward_capacity"])
            ),
            True,
            False,
        )
        ward_cap.sort_values(by=["ward_name", "placement_week"], axis=0, inplace=True)

        num_capacity_exceeded = ward_cap[(ward_cap.cap_exceeded)].shape[0]
        if num_capacity_exceeded > 0:
            logging.info(
                f"Total ward-weeks where capacity exceeded: {num_capacity_exceeded}"
            )
            cap_exceeded_rows = ward_cap[(ward_cap.cap_exceeded)]
        else:
            cap_exceeded_rows = None
            logging.info(
                f"{num_capacity_exceeded} wards have their placement capacity exceeded"
            )

        # Check whether any of the nurses have duplicate assignments
        ward_assignment = pd.DataFrame(
            schedule.groupby(["nurse_name", "block"])["ward_name"].nunique()
        )
        ward_assignment.reset_index(inplace=True)
        num_double_booked = ward_assignment[ward_assignment.ward_name > 1].shape[0]
        if num_double_booked > 0:
            logging.info(
                f"Total blocks where multiple placements assigned: {num_double_booked}"
            )
            double_booked_rows = ward_assignment[ward_assignment.ward_name > 1]
        else:
            double_booked_rows = None
            logging.info(
                f"{num_double_booked} nurses have more than one placement assigned in a certain week"
            )

        self.quality_metrics["num_incorr_num_plac"] = num_incorr_num_plac
        self.quality_metrics["num_incorrect_length"] = num_incorrect_length
        self.quality_metrics["num_capacity_exceeded"] = num_capacity_exceeded
        self.quality_metrics["num_double_booked"] = num_double_booked

        return (
            incorrect_num_plac_rows,
            incorrect_len_rows,
            cap_exceeded_rows,
            double_booked_rows,
        )

    def save_report(self) -> str:
        """
        Function to save down the formatted versions of the schedules including
        a number of views

        :returns: the file name of the saved down report
        """
        schedule = self.produce_dataframe()
        logging.info(f"Generation: {str(self.generation)}")
        logging.info(f"Schedule Viable?: {self.viable}")
        if not self.viable:
            logging.info(f"Non-viable reason: {self.non_viable_reason}")

        schedule["placement_start_week"] = schedule["placement_week"]
        schedule["nurse_id"] = None
        schedule["block"] = None
        schedule[["nurse_id", "block"]] = schedule["nurse_name"].str.split(
            "_", expand=True, n=1
        )

        schedule["ward_name"] = schedule["ward_name"].fillna("None")
        schedule["placement_week_date"] = pd.to_datetime(
            schedule.placement_start_date.min()
        )
        schedule["placement_offset"] = (schedule["placement_week"] - 1) * 7
        schedule["placement_week_date"] = schedule[
            "placement_week_date"
        ] + pd.to_timedelta(schedule["placement_offset"], unit="d")
        schedule = schedule.drop("placement_offset", axis=1)

        (
            incorrect_num_plac_rows,
            incorrect_len_rows,
            cap_exceeded_rows,
            double_booked_rows,
        ) = self.schedule_quality_check()

        # Student-level ward allocation
        nurse_sch = schedule[["nurse_id", "placement_week_date", "ward_name"]]
        nurse_sch_formatted = (
            nurse_sch.groupby(["nurse_id", "placement_week_date"])
            .ward_name.first()
            .unstack()
        )

        # Ward-level student allocation
        ward_sch = schedule[["nurse_id", "placement_week_date", "ward_name"]]
        ward_sch_formatted = (
            ward_sch.groupby(["ward_name", "placement_week_date"])
            .agg({"nurse_id": ", ".join})
            .unstack()
        )

        # Ward hours bases on 37.5 hour weeks
        ward_hours_sch = schedule[["nurse_id", "placement_week_date", "ward_name"]]
        ward_hours_sch_formatted = (
            ward_hours_sch.groupby(["ward_name", "placement_week_date"])
            .nurse_id.count()
            .unstack()
        )
        ward_hours_sch_formatted.fillna(0.0, inplace=True)
        ward_hours_sch_formatted = ward_hours_sch_formatted * 37.5

        # Ward hours bases on 37.5 hour weeks
        cohort_hours_sch = schedule[
            ["nurse_id", "placement_week_date", "nurse_uni_cohort"]
        ]
        cohort_hours_sch_formatted = (
            cohort_hours_sch.groupby(["nurse_uni_cohort", "placement_week_date"])
            .nurse_id.count()
            .unstack()
        )
        cohort_hours_sch_formatted.fillna(0.0, inplace=True)
        cohort_hours_sch_formatted = cohort_hours_sch_formatted * 37.5

        # Ward Utilisation
        ward_util_sch = schedule[["nurse_id", "placement_week_date", "ward_name"]]
        ward_util_sch_caps = schedule[["ward_name", "ward_capacity"]]
        ward_util_sch_caps = ward_util_sch_caps.drop_duplicates()
        ward_util_sch_caps.set_index("ward_name", inplace=True)
        ward_util_sch_formatted = (
            ward_util_sch.groupby(["ward_name", "placement_week_date"])
            .nurse_id.count()
            .unstack()
        )
        ward_util_sch_formatted.fillna(0.0, inplace=True)
        ward_util_sch_formatted = ward_util_sch_formatted.merge(
            ward_util_sch_caps, left_index=True, right_index=True
        )
        ward_util_sch_formatted = ward_util_sch_formatted.astype(float)
        df_cols = list(ward_util_sch_formatted.columns)
        df_cols.remove("ward_capacity")
        ward_util_sch_formatted[df_cols] = (
            ward_util_sch_formatted[df_cols].div(
                ward_util_sch_formatted["ward_capacity"], axis=0
            )
            * 100
        )
        ward_util_sch_formatted = ward_util_sch_formatted.round(2)

        # Quarterly utilisation
        ward_q_util_sch = schedule[["nurse_id", "placement_week_date", "ward_name"]]
        ward_q_util_sch_caps = schedule[["ward_name", "ward_capacity"]]
        ward_q_util_sch_caps = ward_q_util_sch_caps.drop_duplicates()
        ward_q_util_sch_caps.set_index("ward_name", inplace=True)
        ward_q_util_sch.set_index("ward_name", inplace=True)
        ward_q_util_sch_capacities = ward_q_util_sch.merge(
            ward_q_util_sch_caps, left_index=True, right_index=True
        )
        ward_q_util = pd.DataFrame(
            ward_q_util_sch_capacities.groupby(
                ["ward_name", "placement_week_date", "ward_capacity"]
            )["nurse_id"].count()
        )
        ward_q_util.reset_index(inplace=True)
        ward_q_util.columns = [
            "ward_name",
            "placement_week_date",
            "ward_capacity",
            "student_count",
        ]
        ward_q_util["util"] = (
            ward_q_util["student_count"] / ward_q_util["ward_capacity"]
        )
        ward_q_util["placement_q"] = ward_q_util["placement_week_date"].dt.to_period(
            "Q"
        )
        ward_q_util_formatted = (
            ward_q_util.groupby(["ward_name", "placement_q"]).util.mean().unstack()
        )
        ward_q_util_formatted = ward_q_util_formatted.fillna(0.0)
        ward_q_util_formatted = ward_q_util_formatted.round(2)

        # Placements on wards with expired education audits
        ed_aud_exp = schedule[
            [
                "nurse_name",
                "ward_name",
                "placement_start",
                "placement_duration",
                "ed_audit_exp_week",
            ]
        ]
        ed_aud_exp_fail = ed_aud_exp[
            ed_aud_exp.ed_audit_exp_week
            < (ed_aud_exp.placement_start + ed_aud_exp.placement_duration + 1)
        ]
        ed_aud_exp_fail = ed_aud_exp_fail.drop(
            ["placement_start", "placement_duration", "ed_audit_exp_week"], axis=1
        )
        ed_aud_exp_fail = ed_aud_exp_fail.drop_duplicates()
        ed_aud_exp_fail = ed_aud_exp_fail.sort_values(by="ward_name")

        script_directory = os.path.dirname(os.path.abspath(__file__))
        save_directory = os.path.join(script_directory, "..", "results")
        try:
            os.makedirs(save_directory)
        except OSError:
            pass  # already exists

        now = get_time_now()
        file_name = f"schedule_output_{now}_{self.generation}_{self.viable}.xlsx"
        self.file_name = file_name

        full_save_path = os.path.join(save_directory, file_name)

        with pd.ExcelWriter(full_save_path) as writer:
            ed_aud_exp_fail.to_excel(
                writer, sheet_name="wards_expired_audits", index=False
            )
            if incorrect_num_plac_rows is not None:
                incorrect_num_plac_rows.to_excel(
                    writer, sheet_name="incorrect_num_placements", index=False
                )
            if incorrect_len_rows is not None:
                incorrect_len_rows.to_excel(
                    writer, sheet_name="incorrect_len_placements", index=False
                )
            if cap_exceeded_rows is not None:
                cap_exceeded_rows.to_excel(
                    writer, sheet_name="capacity_exceeded", index=False
                )
            if double_booked_rows is not None:
                double_booked_rows.to_excel(
                    writer, sheet_name="double_booked_students", index=False
                )
            nurse_sch_formatted.to_excel(writer, sheet_name="nurse_schedule")
            ward_sch_formatted.to_excel(writer, sheet_name="ward_schedule")
            ward_hours_sch_formatted.to_excel(writer, sheet_name="ward_hours_schedule")
            cohort_hours_sch_formatted.to_excel(
                writer, sheet_name="cohort_hours_schedule"
            )
            ward_util_sch_formatted.to_excel(
                writer, sheet_name="ward_weekly_util_schedule"
            )
            ward_q_util_formatted.to_excel(
                writer, sheet_name="ward_quarterly_util_schedule"
            )

        return file_name

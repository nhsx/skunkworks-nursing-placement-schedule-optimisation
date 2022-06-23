## Schedule
This document provides an overview of the Schedule class 

### Schedule Object
Each Schedule object contains a complete set of student placements across all wards. When the algorithm is run there are many Schedule objects which are manipulated and scored to try and reach the best possible solution.

### Key Functions
#### schedule_generation
This is a an important function as it is the way that each schedule is initialised. This is done on a random basis as long as the following are adhered to:
- The ward chosen has capacity to accommodate the student (both in total and for students of their year group)
- The ward chosen has a valid education audit in place
- The ward has a covid risk status that the student is able to work with

The function will randomly select wards until it finds one where these criteria are met. If one is not found in suitable time, the application will stop entirely as a valid solution is not possible.

#### get_fitness
This is a substantial function which scores each schedule so that the population can ranked in terms of how well criteria are met. It has a number of steps:
- For each placement that has been allocated:
    - For each nurse who has a placement, make a list of wards and specialities they have been on placement at before, as well as for the current placement
    - Check whether the placement is at a ward which has capacity to take the student (both overall and for students of their year group)
    - Check that the ward and student are compatible in terms of their covid risk statuses
    - Check that the student does not have a placement allocated on another ward at the same time
- Assign a score based on the average uniqueness of wards that students have been placed at
- Assign a score based on the average uniqueness of specialities that students have been placed at
- Assign scores based on a number of specialities that students may need to visit during their entire course of placements (this is scored by looking at all words to describe specialities that a student has been placed within. From this set of the words, the % of words that are unique is calculated, and this is used as the scoring multiplier.)
- Assign a score based on whether any placements are unallocated
- Assign a score based on the average utilisation of placement capacity for each ward
- Finally calculate the overall score compared to the maximum score that can be awarded

#### populate_schedule
This is a useful function which is used to ensure that the mutation and recombination processes that Schedule objects have done to them does not result in incomplete student placements. This can occur as recombination can split a placement in two, meaning half of a placement is included in the final version. To alleviate this, after mutations and recombinations are completed, the function cycles through each placement and reconstructs it within the chromosome structure. It does this by looking at the location that the placement is assigned to and the week that the placement starts, before repopulating the Slots object correctly.

#### recombination
Recombination is a vital process in a genetic algorithm. It works by combining two schedules with crossing points. The example from the function provides a useful demonstration:
It produces offspring by combining two parent schedules, with 2 crossing points. This will yield:
p1 = [0 0 0 1 1 0 0 1 0 1]
p2 = [1 0 1 0 0 0 1 0 0 0]
p1 [combined with] p2 = [0 0|1 0 0 0 1|1 0 1]
which corresponds to [p1 | p2 | p1] being combined after the 3rd and 7th indices

#### mutation
This function is another vital process for a genetic algorithm. The mutation randomly changes the location of a placement, ignoring any of the constraints. It is a way of randomly exploring the problem space to find better problem solutions. Ignoring constraints ensures that the problem space is explored as fully as possible, and also speeds up processing by not needing to check a variety of constraints before moving the placement to a new location.

#### produce_dataframe
This function simply converts the chromosome structure of the schedule into a much more easily readable Pandas Dataframe format.

#### schedule_quality_check
This function does some basic checks to make sure that the constraints applied have not been breached. It contributes to some of the metrics displayed on the UI

#### save_report
This function takes the Pandas DataFrame produced by `produce_dataframe` and converts it into a range of formatted reports which help the stakeholders with mandatory reporting as well as generally being more useful and readable depending on the circumstance.
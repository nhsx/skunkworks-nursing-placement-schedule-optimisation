## Background
Placement capacity is a major constraint in building out a hospital's workforce pipeline. The [Royal College of Nursing says](https://www.ed.ac.uk/files/imports/fileManager/RCNHelpingStudentsgettheBestfromtheirPracticePlacements.pdf) that "Learning in the contextual setting of clinical practice enables you to confront many of the challenges and issues related to caring. Practice is where lifelong learning is promoted and enhanced." and gives some benefits of undertaking placements as "continue to develop your competence in both interpersonal and practical skills" and "work within a wide range of rapidly changing health and social services that recognise the continuing nature of care" to give just two examples.

Placement teams in each Trust/organisation create individualised schedules for every learner that enters the Trust on placement. For larger Trusts, this means creating up to 450 schedules that meet the regulatory standards, curriculum requirements and placement capacity.
Typically, Trusts creates their schedules manually in spreadsheets. This is problematic for several reasons:
- Non-standardised spreadsheets preclude efficient use of system-wide placement capacity

- Information for mandatory reports must be manually copied from large spreadsheets

By combining the experience and knowledge of coordinators with the Nursing Placement Optimisation tool means we can ensure we are getting the best schedules for students in the following ways:
- Student placement schedules are optimised against the numerous required criteria

- Placement capacity is used in an optimal manner

- Opportunities for students to experience a range of placement settings are maximised

- Time is saved by placement coordinators, enabling them to focus on other tasks

Special thanks to Imperial College Healthcare NHS Trust who were pivotal in providing expertise and guidance in order for this tool to be developed.

## Placement Optimisation tool

The tool is presented as a web-based app, running in your web browser. The tool requires data to be in a specific format (see [Data Dictionary](config/input_data_dictionary.json)). When run, the tool ingests the data saved in the 'data' folder and converts it to the required format. With the data prepared, the tool runs the genetic algorithm which is implemented within it, and returns a number of schedules pre-specified by the user. The schedules are accompanied by a scoring document which score various aspects of each schedule for comparison against one another (for additional details, see the [UI documentation](docs/UI.md)). 

The schedules themselves consist of a number of tabs which enable views from the perspective of both the student and the ward, as well as reporting-based schedules which show hours and utilisation rate for each working week that the schedule covers. The schedules that are produced are different solutions or options to the same problem for the same set of students. In other words, they are different versions of the same schedule.

By producing a variety of schedules which are each strong in slightly different areas, the tool provides placement coordinators with a strong baseline on which the coordinator can impart their knowledge to get the best learning outcomes for the students, and the best allocation of students for the trust.

(For a diagram of how the algorithm works, please see `nursing_opt_tool_overview.png` in the `docs` folder)

Within the src code files (`src/`), the classes and functions have been given docstrings to provide more specific information around what each piece of functionality does. Please see there for additional information on how the algorithm works.

The tool has demonstrated a robust capability to produce varied sets of placements which meet student needs and allow placement coordinators to have a range of options available on demand. The various reporting views also enable placement coordinators to facilitate changes or updates as required. One example might be that if a student needs a different placement to the one selected by the tool, the ward-centric utilisation tracker allows the placement coordinator to have a single view of each ward's capability to support another placement student.

## Genetic Algorithm
This document provides an overview of how the Genetic Algorithm in this tool works, to provide an accesible point of reference when reviewing the code.

For more detail, please see GeneticAlgorithm documentation (Found in docs/ga.md)

The basic process for the algorithm is as follows:

1. Randomly generate N schedules, utilising the required start dates for 
   each placement.

2. From the population of schedules, randomly choose some schedules to have 
   P mutations performed on them. In this context, a mutation is randomly 
   moving a placement from one ward to another.

3. Additionally from the population of schedules, choose Q parents to be used
   to generate 'offspring'. Parents are selected using a ranked roulette wheel
   where the probability of being chosen is proportional to the fitness of the
   schedule. Offspring are produced by using recombination (sometimes also 
   referred to as crossover) to combine two schedules using a pre-defined
   number of crossover points.

4. The mutated schedules and the offspring are then used to replace the least
   fit schedules in the population, improving the overall fitness of the 
   population.

5. Steps 2-4 are then iterated until either:
    1. A schedule which reaches a minimum level of fitness is identified 
    AND the schedule is viable. In this case, the schedule which meets these 
    requirements is saved down.

    2. There has been no change in the highest ranking schedule's fitness score
    for a pre-defined number of iterations. In this case, the best scoring
    schedule is saved down, regardless of whether the schedule is viable, this
    is to prevent the algorithm from running for too long.

6. The algorithm (steps 1-5) is run X times (defined by the user) to produce 
   X schedules for the placement coordinator to consider the benefits of 
   each option.


## Constraints
The rules implemented in the tool are can be found in the Constraints documentation (Found in docs/constraints.md)

## NHS AI Lab Skunkworks
The project is carried out by the NHS AI Lab Skunkworks, which exists within the NHS AI Lab to support the health and care community to rapidly progress ideas from the conceptual stage to a proof of concept.

Find out more about the [NHS AI Lab Skunkworks](https://www.nhsx.nhs.uk/ai-lab/ai-lab-programmes/skunkworks/).
Join our [Virtual Hub](https://future.nhs.uk/connect.ti/system/text/register) to hear more about future problem-sourcing event opportunities.
Get in touch with the Skunkworks team at [aiskunkworks@nhsx.nhs.uk](aiskunkworks@nhsx.nhs.uk).

## Acknowledgements
This tool is developed, in part, based on [GASchedule.py](https://github.com/mcychan/GASchedule.py) which was used as a starting point for this project


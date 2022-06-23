## User Interface
This document provides an overview of the User Interface (UI) and the meaning of various components

![UIOverview](ui_overview.png)
### Running the algorithm
When the UI first loads, several components will be visible initially:
| Component | Purpose |
| --------- | ------- |
| "Choose your page" dropdown | this dropdown menu allows the user to switch between "Run algorithm" and "Documentation". This allows the user to view basic documentation within the browser, helping them to get started |
| "Start date" date selector | this allows the user to choose the earliest date for which placements should be allocated |
| "End date" date selector | this allows the user to choose the latest date for which placements should be allocated |
| "Choose number of schedules to generate" slider | this allows the user to choose the number of times that the algorithm will run, and subsequently how many options will be offered to them at the end |

Below these components may be:
- A red error box containing the following text "Be aware that the following wards have Education Audits which expire on or before the start date of your schedules:" followed by a list of wards. This comprises a list of wards where the Education Audit expiry date is on or before the Start Date selected with the End Date date selector.
- An amber box containing the following text "Additionally, be aware that the following wards have Education Audits which expire on or before the end date of your schedules:" followed by a list of wards. This comprises a list of wards where the Education Audit expiry date is after the Start Date but on or before the End Date selected with the End Date date selector.

Whether or not these boxes appear will depend on the Education Audit Status of your wards. Note that the Education Audit Expiry date warnings **DO NOT** prevent students from going on placement at that ward. When each final schedule is produced, a list of wards with expired Education Audits will be generated as part of the schedule, to demonstrate the wards which must have an Education Audit completed before placements can be accepted.

Finally, below this will be the "Click here to start running" button. When pressed, this will begin running the algorithm with the settings configured using the components above.

### While the algorithm runs
While the tool is running, some live information will be displayed to help you keep track of the progress. Information will be displayed for each schedule being produced including the following:
| Field | Explanation |
| ----- | ----------- |
| Schedule # being generated | this is simply to help keep count of how many schedules have been generated so far out of the number requested |
| Current schedule version being generated | this shows the progress of the algorithm and will count up as it tries to produce the best possible schedule |
| Highest schedule fitness score | this is the current highest score of the schedules which have been generated. This score should increase while the tool runs, but may reach a point where it can no longer improve the best schedule. |

With each schedule that is finished, a table will be displayed summarising some key information about each schedule. This information includes:
| Field | Explanation |
| ----- | ----------- |
| Schedule file name | This is the name of the schedule as saved in the `results` folder |
| Viable schedule? | This immediately tells you whether or not the schedule satisfies all of the [constraints](docs/constraints.md) specified |
| Number of iterations to generate | This tells you how many cycles of the algorithm it took to produce the final schedule |
| Schedule Fitness Score | This is the fitness score of each schedule produced. These scores are mostly useful to compare schedules to each other |
| Placement Utilisation Score | This is the average % utilisation of placement capacity on each ward |
| Unique Specialities Score | This is the average % of terms which are unique in the list of all specialities that a student has been on placement at |
| Unique Wards Score | This is the average % of wards which are unique where a student has been on placement |
| No. students with incorrect no. of placements | This is the number of students who have too many or too few placements (in most cases this will be 0) |
| No. of placements with the incorrect length  | This is the number of placements which are longer or shorter than they need to be (in most cases this will be 0) |
| No. of ward-weeks where capacity is exceeded | This is the number of ward-weeks where too many students (either overall or of a specific year) are allocated to a ward |
| No. of placements where student is double-booked | This is the number of placements where a student is assigned to more than 1 ward at a time |

#### Example calculation of Unique Specialities and Unique Wards Scores
The Unique Specialities and Unique Wards Scores are important drivers in encourgaing the algorithm to allocate a selection of placements to students which help them to experience a diverse range of skills. In addition, these scoring metrics can help placement coordinators to compare schedules and see the pros and cons of each of the options.
To illustrate how these scores would be calculated, here is a simple example

##### Unique Specialities Score
If Student A goes on placements at wards or teams specialising in (these specialities are for demonstration purposes only) 'Critical and Emergency Care', 'Abdominal Surgery', 'Cardiac Surgery', 'District Nursing' and 'Elderly Rehabilitiation Care', they will have 13 words which describe the specialities they have had placements in. Of those 13 words, 11 are unique, so the Unique Specialities Score for this student would be 11/13 = 0.846. This calculation is carried out for each student, and the score displayed on the UI is the average of all scores.

##### Unique Wards Score
If Student B goes on placements at the following wards: 'Ward A', 'Ward G', 'Ward C', 'Ward M', 'Ward A', 'Ward P', the student will have completed 6 placements in total. However they will have only experienced 5 unique wards, so their Unique Wards Score would be 0.833. This calculation is carried out for each student, and the score displayed on the UI is the average of all scores.

### After the algorithm has run
Once the algorithm has finished running, some balloons will appear, as well as a green box stating 'Schedule production complete!'. This indicates that all of the requested schedules have been produced and are ready for human review.

Each schedule will be saved down to the `results` folder, as well as a copy of the table displayed on the UI, so that comparisons can be done after the tool is closed.
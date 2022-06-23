## Constraints
This document contains a list of all the goals implemented in the genetic algorithm. These are what the tool try to maximise for.

| Goal | Explanation |
| ---- | ----------- |
| Maximising the unique number of wards that a student visits | This encourages the tool to try and ensure that a student doesn't go to the same ward more than once |
| Maximising the unique number of specialities that a student experiences | This encourages placement diversity beyond wards alone. This is achieved by maximising the unique number of words that describe a speciality |
| [OPTIONAL] Encouraging placements to be assigned to pre-defined | Some universities or Trusts require students to have at least one placement in specific settings. There are 4 pre-implemented versions of this enabling maximisation of Medical, Surgical, Community and Critical Care/Emergency placements. This goal can be turned on and off as required.|


### Configuring the speciality goals
Within the `params.yml` file (found [here](../config/params.yml)), there are four speciality options that can be turned on and off:
- The variables that determine if one of the goals are turned on or off are named `medical_placement_check`, `surgical_placement_check`, `community_placement_check`, `critical_care_placement_check`.
- Each of these checks looks for keywords to determine if a speciality has been visited:
    - A placement that is a Medical speciality is defined as having 'medical' or 'medicine' in the speciality description
    - A placement that is a Surgical speciality is defined as having 'surgical' or 'surgery' in the speciality description
    - A placement that is a Community speciality is defined as having 'community' in the speciality description
    - A placement that is a Critical Care speciality is defined as having 'emergency' or 'critical' in the speciality description
- By default, these have 'False' next to them, meaning that the goal is not enabled and the tool will not try and ensure that type of placement is included.
- To enable them, replace 'False' with 'True' (note the exact capitalisation). This will activate that speciality goal only.
- Note that if a student has historically been on a placement to a speciality, and that check is enabled, the tool will not necessarily include another placement of that speciality. Historic placements are included as part of assessing if a student has been visited the desired specialities.
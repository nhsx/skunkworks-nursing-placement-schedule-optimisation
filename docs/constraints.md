## Constraints
This document contains a list of all the constraints implemented on the genetic algorithm

| Constraint | Purpose |
| ---------- | ------- |
| One placement per student per block | Ensures that students do not have multiple placements allocated for a single block |
| Ward capacity cannot be exceeded | Ensures that wards are not allocated more placements than they can support (both overall and from a year-specific capacity) |
| Ward covid risk must match student covid risk | Ensure no students who are at-risk of Covid go on placement to a high risk ward |
| All placements must be allocated to a ward | Ensures that all placements are assigned to a ward (important if mutation/recombination leaves a placement unassigned) |
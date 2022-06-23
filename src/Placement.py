class Placement:
    """ Placement class represents the list of student placements to be assigned """

    def __init__(self, listOfInputs):
        (
            self.id,
            self.name,
            self.cohort,
            self.duration,
            self.start,
            self.start_date,
            self.part,
            self.wardhistory,
            self.dephistory,
            self.covid_status,
        ) = listOfInputs

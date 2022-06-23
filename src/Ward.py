class Ward:
    """ Ward class represents wards where placements can take place """

    def __init__(self, listOfInputs):
        (
            self.id,
            self.ward,
            self.department,
            self.ed_audit_expiry_week,
            self.covid_status,
            self.capacity,
            self.p1_capacity,
            self.p2_capacity,
            self.p3_capacity,
        ) = listOfInputs

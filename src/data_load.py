import pandas as pd
import numpy as np
from src.Slot import Slot
from src.Ward import Ward
from src.Placement import Placement
import warnings


class DataLoader:

    def readData(self, filename):
        """
        Load data from files and do basic preprocessing and prep
        """

        # Load relevant files
        self.students = pd.read_excel(
            filename, sheet_name="students", engine="openpyxl"
        )
        self.ward_data = pd.read_excel(filename, sheet_name="wards", engine="openpyxl")

        self.uni_placements = pd.read_excel(
            filename, sheet_name="placements", engine="openpyxl"
        )

    def createCohort(self,df,cohort_col_name,uni_col_name,qual_col_name,start_col_name):
        df[cohort_col_name] = (
            df[uni_col_name].astype(str)
            + "_"
            + df[qual_col_name].astype(str)
            + " "
            + df[start_col_name].astype(str)
        )
        return df

    def calcRelDateWeeks(self, df, ref_df, output_col_name, calc_date_col, ref_data_col):
        """"
        Calculate a date in weeks relative to another date
        """

        df[output_col_name] = np.round(
            (
                pd.to_datetime(df[calc_date_col], yearfirst=True)
                - pd.to_datetime(
                    ref_df[ref_data_col].min(), yearfirst=True
                )
            )
            / np.timedelta64(1, "W"),
            0,
        )
        return df

    def cleanPrevPlacements(self):
        # Process student info
        self.students["prev_placements"] = (
            self.students["prev_placements"].str.strip().str.replace("'", "")
        )
        self.students["allprevwards"] = self.students.prev_placements.apply(
            lambda x: x[1:-1].split(",")
        )

    def cleanStudentPlacementCohorts(self):
        self.students = self.createCohort(self.students,"student_cohort","university","qualification","course_start")
        self.uni_placements = self.createCohort(self.uni_placements,"student_cohort","university","qualification","course_start")

    def cleanWardAuditExpCapacity(self):
        self.ward_data = self.calcRelDateWeeks(self.ward_data,self.uni_placements,"education_audit_exp_week", "education_audit_exp", "placement_start_date")

        self.ward_data["capacity"] = self.ward_data[["p1_cap", "p2_cap", "p3_cap"]].max(
            axis=1
        )

    def cleanSelectWardColumnNames(self):
        self.ward_data = self.ward_data[
            [
                "ward_name",
                "ward_speciality",
                "education_audit_exp",
                "education_audit_exp_week",
                "covid_status",
                "capacity",
                "p1_cap",
                "p2_cap",
                "p3_cap",
            ]
        ]
        self.ward_data.columns = [
            "Ward",
            "Department",
            "education_audit_exp",
            "education_audit_exp_week",
            "covid_status",
            "capacity",
            "P1_CAP",
            "P2_CAP",
            "P3_CAP",
        ]

    def cleanStudentsPreviousDepartments(self):
        self.ward_dep_match = pd.Series(
            self.ward_data.Department.values, index=self.ward_data.Ward
        ).to_dict()
        self.ward_dep_match[""] = "None"
        self.students["prev_deps"] = [
            [self.ward_dep_match[value.rstrip().lstrip()] for value in x]
            for x in self.students["allprevwards"]
        ]
        self.students["allprevdeps"] = [
            ", ".join(dep_list) for dep_list in self.students["prev_deps"]
        ]

    def cleanStudentPreviousWards(self):
        self.students["allprevwards"] = [
            ", ".join(prev_plac) for prev_plac in self.students["allprevwards"]
        ]
    
    def mergeStudentsWithPlacements(self):
        self.student_placements = self.students.merge(
            self.uni_placements, how="left", on="student_cohort"
        )

    def datePreparation(self):
        """
        Preprocess date fields in student_placements df
        """

        # Process placement student_placements
        self.student_placements["placement_start_date"] = pd.to_datetime(
            self.student_placements["placement_start_date"], yearfirst=True
        )
        self.student_placements["placement_start_date_raw"] = self.student_placements[
            "placement_start_date"
        ].copy()

        self.student_placements = self.calcRelDateWeeks(self.student_placements,self.uni_placements,"placement_start_date", "placement_start_date", "placement_start_date")

        self.student_placements["placement_end_date"] = (
            self.student_placements["placement_start_date"]
            + self.student_placements["placement_len_weeks"]
            - 1
        )

    def restructureData(self, num_weeks):
        """
        Convert dataframes into lists of Class objects for Genetic Algorithm
        """

        num_slots = list(range(1, num_weeks + 1))
        self.slots = []
        pos = 0
        for item in num_slots:
            row_contents = []
            row_contents.extend([pos, str(item)])
            pos += 1
            slot_item = Slot(row_contents)
            self.slots.append(slot_item)

        self.wards = []
        for index, row in self.ward_data.iterrows():
            row_contents = []
            row_contents.extend(
                [
                    index,
                    row.Ward,
                    row.Department,
                    row.education_audit_exp_week,
                    row.covid_status,
                    row.capacity,
                    row.P1_CAP,
                    row.P2_CAP,
                    row.P3_CAP,
                ]
            )
            ward_item = Ward(row_contents)
            self.wards.append(ward_item)

        self.placements = []
        for index, row in self.student_placements.iterrows():
            row_contents = []
            year_num = row.placement_name.split(",", maxsplit=1)[0]
            row_contents.extend(
                [
                    index,
                    str(row.student_id) + "_" + str(row.placement_name),
                    row.student_cohort,
                    row.placement_len_weeks,
                    row.placement_start_date,
                    row.placement_start_date_raw,
                    year_num,
                    row.allprevwards,
                    row.allprevdeps,
                    row.allowable_covid_status,
                ]
            )
            placement_item = Placement(row_contents)
            self.placements.append(placement_item)



def input_quality_checks(self):
    try:
        self.students["prev_placements"] = self.students["prev_placements"].astype(list)
    except:
        raise TypeError(
            "Previous placements contains entries which are not in a list format e.g. ['ward1','ward2','ward3']"
        )

    int_dict = {
        "Students": ["year"],
        "Wards": ["capacity_num", "p1_cap", "p2_cap", "p3_cap"],
        "Placements": ["placement_len_weeks"],
    }
    for tab, list in int_dict.values():
        for col in list:
            try:
                if tab == "Students":
                    self.students[col] = self.students[col].astype(int)
                elif tab == "Wards":
                    self.wards[col] = self.wards[col].astype(int)
                elif tab == "Placements":
                    self.uni_placements[col] = self.uni_placements[col].astype(int)
            except:
                raise TypeError(
                    f"{col} column in {tab} tab contains entries which are not integers (e.g. whole numbers)"
                )

    date_dict = {
        "Wards": ["education_audit_exp"],
        "Placements": ["placement_start_date"],
    }
    for tab, list in date_dict.values():
        for col in list:
            try:
                if tab == "Students":
                    self.students[col] = self.students[col].astype(int)
                elif tab == "Wards":
                    self.wards[col] = self.wards[col].astype(int)
                elif tab == "Placements":
                    self.uni_placements[col] = self.uni_placements[col].astype(int)
            except:
                raise TypeError(
                    f"{col} column in {tab} tab contains entries which are not datetime and/or in the correct format of YYYY-MM-DD"
                )

import logging

for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)
logging.basicConfig(
    filename="log/nurse_opt_logging.log", filemode="w", level=logging.INFO
)

import streamlit as st
import pandas as pd
import numpy as np
from src.data_load import DataLoader
from src.GeneticAlgorithm import GeneticAlgorithm
import yaml
from datetime import datetime
import os
import matplotlib.pyplot as plt


def main(num_schedules: int, pop_size: int):
    """
    Function to run Nursing Placement Optimisation tool end-to-end
    :param num_schedules: the overall integer number of schedules to output from the tool. Can be otherwise thought of as number of times the tool is run
    :param pop_size: the size of the population to be used for each run. This is the integer number of schedules randomly produced for each run of the tool, which are used as the base to find the best performing schedule from
    
    :returns: A series of .xlsx files, stored in results/ which contain the schedules, as well as a comparison file which shows the scores of each schedule beside each other
    """

    st.info(
        "Some useful information which may be of interest will be printed in the Command Line terminal and stored in log/nurse_opt_logging.log"
    )
    st.subheader("Cycle information")
    st.subheader("Last saved schedule details")
    ui_schedule_results = st.empty()

    num_weeks = int(
        np.round(
            (
                pd.to_datetime(
                    dataload.student_placements["placement_start_date_raw"].max()
                )
                - pd.to_datetime(
                    dataload.student_placements["placement_start_date_raw"].min()
                )
            )
            / np.timedelta64(1, "W"),
            0,
        )
    )

    #  Add maximum placement length so that schedule is large enough to accommodate even the longest placement
    num_weeks = (
        num_weeks + int(dataload.student_placements["placement_len_weeks"].max()) + 1
    )

    logging.info(f"Total weeks covered: {num_weeks}")
    slots, wards, placements = dataload.preprocData(num_weeks)

    num_iter = num_schedules
    scheduleCompare = []
    placeholder = st.empty()
    graph_placeholder = st.empty()
    for i in range(num_iter):
        GA = GeneticAlgorithm(slots, wards, placements, pop_size, num_weeks)
        GA.seed_schedules()
        (
            continue_eval,
            chosen_schedule,
            fitness,
            iteration,
            schedule_fitnesses,
        ) = GA.evaluate()
        # prev_fitness = 0
        while continue_eval:
            with placeholder.container():
                metric1, metric2, metric3 = st.columns(3)
                metric1.metric("Schedule # being generated", i + 1)
                metric2.metric("Current schedule version generating", iteration)
                metric3.metric("Highest schedule fitness score", np.round(fitness, 4))
                with graph_placeholder.container():
                    fig, ax = plt.subplots(figsize=(20, 5))
                    ax.hist(
                        schedule_fitnesses,
                        bins=100,
                        color="#005EB8",
                        edgecolor="#003087",
                    )
                    ax.set_title("Distribution of Fitness Scores")
                    ax.set_ylabel("Count of Schedules")
                    ax.set_xlabel("Fitness Score")
                    ax.set_ylim([0, 35])
                    ax.set_xlim([0.3, 1])
                    fig.set_facecolor("#ececec")
                    ax.set_facecolor("#ececec")
                    st.pyplot(fig, clear_figure=True)
                    st.info(
                        "The above plot shows a histogram of fitness scores for schedules created by the algorithm. A score of 1 is the best possible score, while a score of 0 is the worst possible"
                    )
                (
                    continue_eval,
                    chosen_schedule,
                    fitness,
                    iteration,
                    schedule_fitnesses,
                ) = GA.evolve()
        viable = chosen_schedule.file_name.split("_", maxsplit=10)[9].replace(
            ".xlsx", ""
        )
        schedule_scores = chosen_schedule.schedule_eval_scores
        quality_scores = chosen_schedule.quality_metrics
        scheduleCompare.append(
            [
                chosen_schedule.file_name,
                viable,
                chosen_schedule.non_viable_reason,
                iteration,
                np.round(chosen_schedule.fitness, 4),
                np.round(schedule_scores["mean_ward_util"], 2),
                np.round(schedule_scores["mean_uniq_deps"], 2),
                np.round(schedule_scores["mean_uniq_wards"], 2),
                np.round(quality_scores["num_incorr_num_plac"], 2),
                np.round(quality_scores["num_incorrect_length"], 2),
                np.round(quality_scores["num_capacity_exceeded"], 2),
                np.round(quality_scores["num_double_booked"], 2),
            ]
        )

        scheduleCompareDF = pd.DataFrame(
            scheduleCompare,
            columns=[
                "Schedule file name",
                "Viable schedule?",
                "Non-viable reason",
                "Number of iterations to generate",
                "Schedule Fitness Score",
                "Placement Utilisation score ",
                "Unique Specialities Score",
                "Unique Wards Score",
                "No. students with incorrect no. of placements",
                "No. of placements with the incorrect length",
                "No. of ward-weeks where capacity is exceeded",
                "No. of placements where student is double-booked",
            ],
        )

        ui_schedule_results.dataframe(
            scheduleCompareDF.style.highlight_max(axis=0, color="lightgreen")
        )
        logging.info(f"{chosen_schedule.file_name} generated")

    script_directory = os.path.dirname(os.path.abspath(__file__))
    save_directory = os.path.join(script_directory, "results")
    try:
        os.makedirs(save_directory)
    except OSError:
        pass  # already exists

    now = datetime.now().strftime("%d_%m_%Y_%H_%M_%S")
    file_name = f"schedule_comparison_{now}.csv"
    full_save_path = os.path.join(save_directory, file_name)
    now = datetime.now().strftime("%d_%m_%Y_%H_%M_%S")
    scheduleCompareDF.to_csv(full_save_path)
    logging.info("Comparison file saved")
    viableBool = False
    if len(scheduleCompareDF[scheduleCompareDF["Viable schedule?"] == True]) > 0:
        viableBool = True
    return viableBool


st.set_page_config(
    page_title="Placement Optimisation",
    page_icon="nhs_logo.png",
    layout="wide",
    initial_sidebar_state="auto",
)
st.image("docs/banner.png")
st.title("Nursing Placement Optimisation")


page = st.selectbox("Choose your page", ["Run algorithm", "Documentation"])

if page == "Run algorithm":

    dataload = DataLoader()

    # Open the config params file to get some key arguments
    with open("config/params.yml") as f:
        params = yaml.load(f, Loader=yaml.FullLoader)

    # From the config file, read in the number of chromosomes (this is genetic algorithm terminology for the size of the population, or in this case the number of schedules being created to use to find the best solution)
    numberOfChromosomes = params["ui_params"]["numberOfChromosomes"]

    file_source = st.selectbox(
        "Select your data source", ["Fake data", "Your own data"]
    )

    if file_source == "Fake data":
        try:
            dataload.readData("data/fake_data.xlsx")
        except FileNotFoundError:
            logging.exception(f"No fake_data.xlsx file found in the data directory")
    elif file_source == "Your own data":
        # From the config file, get the name of the file containing the input data
        input_file_name = params["ui_params"]["input_file_name"]
        if input_file_name == "file_name_here" or input_file_name == "":
            st.error(
                f"No input file name has been configured, please update config/params.yml. Other errors may appear below this as a result."
            )
        else:
            try:
                dataload.readData(f"data/{input_file_name}")
            except FileNotFoundError:
                logging.exception(
                    f"No file found by the name {input_file_name} in the data directory"
                )

    student_placement_starts = dataload.student_placements["placement_start_date_raw"]

    start_date = st.date_input(
        "Start Date",
        value=pd.to_datetime(min(student_placement_starts), format="%Y-%m-%d"),
    )
    end_date = st.date_input(
        "End Date",
        value=pd.to_datetime(max(student_placement_starts), format="%Y-%m-%d"),
    )

    if start_date >= end_date:
        st.error(
            f"Start date comes after or on the same day as the end date, please correct before proceeding"
        )
        logging.exception(
            "Start date comes after or on the same day as the end date, please correct before proceeding"
        )
    else:
        dataload.student_placements = dataload.student_placements[
            (
                pd.to_datetime(
                    dataload.student_placements.placement_start_date_raw
                ).dt.date
                >= start_date
            )
            & (
                pd.to_datetime(
                    dataload.student_placements.placement_start_date_raw
                ).dt.date
                < end_date
            )
        ]

        schedule_num = st.empty()
        num_schedules = st.slider(
            "Choose number of schedules to generate",
            min_value=1,
            max_value=10,
            value=2,
            step=1,
            help="Note that once you click the Run button below, moving this slider again with cancel the program",
        )

        expire_wards_string = ""
        for item in list(
            dataload.ward_data[
                pd.to_datetime(dataload.ward_data.education_audit_exp).dt.date
                <= start_date
            ]["Ward"]
        ):
            expire_wards_string = expire_wards_string + item + ", "

        going_to_expire_wards_string = ""
        for item in list(
            dataload.ward_data[
                (
                    pd.to_datetime(dataload.ward_data.education_audit_exp).dt.date
                    <= end_date
                )
                & (
                    pd.to_datetime(dataload.ward_data.education_audit_exp).dt.date
                    > start_date
                )
            ]["Ward"]
        ):
            going_to_expire_wards_string = going_to_expire_wards_string + item + ", "

        if len(expire_wards_string) > 0:
            st.error(
                f"Be aware that the following wards have Education Audits which expire on or before the start date of your schedules:\n {expire_wards_string}"
            )
            logging.warning(
                f"Be aware that the following wards have Education Audits which expire on or before the start date of your schedules: {expire_wards_string}"
            )
        if len(going_to_expire_wards_string) > 0:
            st.warning(
                f"Additionally, be aware that the following wards have Education Audits which expire on or before the end date of your schedules:\n {going_to_expire_wards_string}"
            )
            logging.warning(
                f"Additionally, be aware that the following wards have Education Audits which expire on or before the end date of your schedules: {going_to_expire_wards_string}"
            )

        run_button = st.empty()
        end_message = st.empty()
        if run_button.button("Click here to start running"):
            viableBool = main(num_schedules, numberOfChromosomes)
            if viableBool:
                st.balloons()
                end_message.success("Schedule production complete!")
            else:
                end_message.error(
                    "Schedule production complete, no viable schedules found"
                )
elif page == "Documentation":
    f = open("README_ui.md", "r")
    st.markdown(f.read())

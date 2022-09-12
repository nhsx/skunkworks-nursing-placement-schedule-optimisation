from datetime import datetime
def get_time_now():
    """
    Function to get current time
    """
    now = datetime.now().strftime(f"%d_%m_%Y_%H_%M_%S")
    return now
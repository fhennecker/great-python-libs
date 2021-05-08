import re
from datetime import datetime


def find_datetime(text):
    start_date, end_date, start_hour, end_hour = [None] * 4

    timing = re.search(r"Le (\d+\/\d+\/\d+), de (\d+:\d+) à (\d+:\d+)", text)
    if timing is not None:
        start_date, start_hour, end_hour = timing.groups()
        end_date = start_date

    timing = re.search(
        r"Du (\d+\/\d+\/\d+) à (\d+:\d+) au (\d+\/\d+\/\d+) à (\d+:\d+)", text,
    )
    if timing is not None:
        start_date, start_hour, end_date, end_hour = timing.groups()

    timing = re.search(r"Le (\d+\/\d+\/\d+), à (\d+:\d+)", text,)
    if timing is not None:
        start_date, start_hour = timing.groups()

    if start_date is None:
        assert "Cet événement n'a pas encore de date prévue" in text
    start_datetime, end_datetime = None, None
    if start_date is not None:
        start_datetime = datetime.strptime(start_date + start_hour, "%d/%m/%y%H:%M")
    if end_date is not None:
        end_datetime = datetime.strptime(end_date + end_hour, "%d/%m/%y%H:%M")

    return start_datetime, end_datetime

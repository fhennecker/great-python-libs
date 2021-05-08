from bs4 import BeautifulSoup
import requests
import re
from datetime import datetime
from dataclasses import dataclass, astuple, fields
from typing import Optional
from rich import print
from rich.progress import track
from tabulate import tabulate
import pandas as pd
import click


@dataclass
class EventDetails:
    url: str
    title: str
    organiser: str
    start_date: Optional[datetime]
    end_date: Optional[datetime]


def get_last_event_id():
    response = requests.get("https://urlab.be/events/?type=past&offset=0")
    soup = BeautifulSoup(response.text, "html.parser")

    return int(soup.find("a", {"class": "btn-primary"}).get("href").split("/")[-1])


def get_details_from_event_url(url):
    response = requests.get(url)
    if response.status_code != 200:
        print(f":poop: [bold magenta]{response.status_code}[/bold magenta] - {url}")
        return None

    html_doc = response.text

    soup = BeautifulSoup(html_doc, "html.parser")

    title = soup.h1.text.replace("Editer", "").strip()

    event_info = soup.find("div", {"class": "row"}).div
    person = event_info.a.text

    start_date, end_date, start_hour, end_hour = [None] * 4

    timing = re.search(r"Le (\d+\/\d+\/\d+), de (\d+:\d+) à (\d+:\d+)", event_info.text)
    if timing is not None:
        start_date, start_hour, end_hour = timing.groups()
        end_date = start_date

    timing = re.search(
        r"Du (\d+\/\d+\/\d+) à (\d+:\d+) au (\d+\/\d+\/\d+) à (\d+:\d+)",
        event_info.text,
    )
    if timing is not None:
        start_date, start_hour, end_date, end_hour = timing.groups()

    timing = re.search(r"Le (\d+\/\d+\/\d+), à (\d+:\d+)", event_info.text,)
    if timing is not None:
        start_date, start_hour = timing.groups()

    if start_date is None:
        assert "Cet événement n'a pas encore de date prévue" in event_info.text
    start_datetime, end_datetime = None, None
    if start_date is not None:
        start_datetime = datetime.strptime(start_date + start_hour, "%d/%m/%y%H:%M")
    if end_date is not None:
        end_datetime = datetime.strptime(end_date + end_hour, "%d/%m/%y%H:%M")

    return EventDetails(url, title, person, start_datetime, end_datetime)


def download_events_to_csv(max_event_id, output_path):

    all_events = []
    for e in track(range(max_event_id), "Getting events..."):
        details = get_details_from_event_url(f"https://urlab.be/events/{e}")
        if details is not None:
            all_events.append(details)

    print(tabulate([astuple(e) for e in all_events]))

    dataframe = pd.DataFrame(
        [astuple(e) for e in all_events], columns=[f.name for f in fields(EventDetails)]
    )

    dataframe.to_csv(output_path)


@click.command()
@click.argument("max_event_id", type=int)
@click.option("-o", "--output-path", default="events.csv")
def main(max_event_id, output_path):
    download_events_to_csv(max_event_id, output_path)


if __name__ == "__main__":
    main()

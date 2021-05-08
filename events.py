import requests
from bs4 import BeautifulSoup
from datetimeparser import find_datetime
from dataclasses import dataclass, astuple, fields
from datetime import datetime
from tabulate import tabulate
from rich.progress import track
from rich import print
import pandas as pd
import click


@dataclass
class EventDetails:
    url: str
    title: str
    organiser: str
    start_datetime: datetime
    end_datetime: datetime


def get_details_from_event_url(url):
    response = requests.get(url)

    if response.status_code != 200:
        print(f":poop: [bold magenta]{response.status_code}[/bold magenta] - {url}")
        return None

    soup = BeautifulSoup(response.text, "html.parser")

    title = soup.h1.text.replace("Editer", "").strip()

    event_info = soup.find("div", {"class": "row"}).div
    organiser = event_info.a.text
    start_datetime, end_datetime = find_datetime(event_info.text)

    return EventDetails(url, title, organiser, start_datetime, end_datetime)


def download_events(max_event_id, output_path):
    events = [
        get_details_from_event_url(f"https://urlab.be/events/{event_id}")
        for event_id in track(range(max_event_id), "Getting events...")
    ]
    events = [e for e in events if e is not None]

    print(tabulate([astuple(e) for e in events]))

    df = pd.DataFrame(
        [astuple(e) for e in events],
        columns=[field.name for field in fields(EventDetails)],
    )
    df.to_csv(output_path)


def get_last_event_id():
    response = requests.get("https://urlab.be/events/?type=past&offset=0")
    soup = BeautifulSoup(response.text, "html.parser")

    return int(soup.find("a", {"class": "btn-primary"}).get("href").split("/")[-1])


@click.command()
@click.argument("max_event_id", type=int)
@click.option("-o", "--output-path", default="events.csv")
def main(max_event_id, output_path):
    download_events(max_event_id, output_path)


if __name__ == "__main__":
    main()

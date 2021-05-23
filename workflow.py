from dagster import pipeline, solid, schedule, repository
import os
import shutil
import time
import events


@solid
def output_path(_) -> str:
    return "events.csv"


@solid
def get_last_event_id(_) -> int:
    the_id = events.get_last_event_id()
    print(the_id)
    return the_id


@solid
def make_events_backup(context, output_path: str) -> bool:
    if os.path.exists(output_path):
        shutil.copy2(output_path, output_path + ".bak")
    time.sleep(3)
    return True


@solid
def get_all_events(context, max_event_id: int, output_path: str, backup_done: bool):
    events.download_events(max_event_id, output_path)


@pipeline
def update_csv():
    path = output_path()
    get_all_events(get_last_event_id(), path, make_events_backup(path))


@schedule(
    cron_schedule="* * * * *",
    pipeline_name="update_csv",
    execution_timezone="Europe/Paris",
)
def minute_schedule(context):
    return {}


@repository
def thank_you():
    return [update_csv, minute_schedule]

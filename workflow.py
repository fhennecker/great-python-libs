from dagster import pipeline, solid, schedule, repository

import get_events
import shutil
import os
import time


@solid
def get_output_path(context) -> str:
    output = context.solid_config["path"]
    print(output)
    return output


@solid
def get_last_event_id(_) -> int:
    the_id = get_events.get_last_event_id()
    print(the_id)
    return the_id


@solid
def get_all_events_up_to(
    context, last_event_id: int, output_path: str, backup_done: bool
):
    get_events.download_events_to_csv(last_event_id, output_path)


@solid
def make_events_backup(context, output_path: str):
    if os.path.exists(output_path):
        shutil.copy2(output_path, output_path + ".bak")
    time.sleep(3)
    return True


@pipeline
def update_csv():
    output_path = get_output_path()
    get_all_events_up_to(
        get_last_event_id(), output_path, make_events_backup(output_path)
    )


@schedule(
    cron_schedule="* * * * *",
    pipeline_name="update_csv",
    execution_timezone="Europe/Paris",
)
def minute_schedule(_context):
    return {"solids": {"get_output_path": {"config": {"path": "automatic.csv"}}}}


@repository
def great_python_libs():
    return [update_csv, minute_schedule]

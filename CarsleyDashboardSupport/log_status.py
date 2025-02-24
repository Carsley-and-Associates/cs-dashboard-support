from CarsleyDashboardSupport.status_types import *


def log_status(status_entry: StatusEntry, cache_file_path: str):
    if os.path.exists(cache_file_path):
        with open(cache_file_path, "r") as file:
            try:
                logs = json.load(file)
            except json.JSONDecodeError:
                logs = []
    else:
        os.makedirs(os.path.dirname(cache_file_path), exist_ok=True)
        logs = []

    logs.append(status_entry.as_dict())

    with open(cache_file_path, "w") as file:
        json.dump(logs, file, indent=4)

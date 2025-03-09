import threading
import time
import requests
from CarsleyDashboardSupport.log_status import *
from CarsleyDashboardSupport.config import *


#TODO: url config - by package or by servers?

def _send_request(status_json):
    try:
        response = requests.get(DASHBOARD_HANDSHAKE_URL, timeout=5)
        if response.status_code != 200:
            return {
                "error": f"Remote dashboard at {DASHBOARD_HANDSHAKE_URL} is not available. Exception: {str(response)}"}
    except requests.RequestException as e:
        return {"error": f"Remote dashboard is unreachable. Exception: {str(e)}"}
    receive_url = DASHBOARD_URL + response.json()["receive_status_url"]
    try:
        response = requests.post(receive_url, json=status_json, timeout=5)
        if response.status_code == 201:
            return {"message": f"Successfully sent status to {receive_url}."}
        else:
            return {"error": f"Failed to send status to remote manager {receive_url}. Exception: {str(response)}"}
    except requests.RequestException as e:
        return {"error": f"Failed to communicate with the remote manager. Exception: {str(e)}"}


def sync_status_now(
        cache_file_path: str,
        new_status: StatusEntry,
        include_cache: bool = True,
):
    """
    Send status update to dashboard.
    Checks connection to the dashboard.
        If connection open: send status update with cached status (if exist)
        If connection close: raise exception
    """
    # By default, include cached statuses in every call
    if include_cache and os.path.exists(cache_file_path):
        with open(cache_file_path, "r") as file:
            try:
                cached_statuses = json.load(file)
            except json.JSONDecodeError:
                cached_statuses = []
    else:
        cached_statuses = []

    cached_statuses.append(new_status.as_dict())

    if not cached_statuses:
        return "There is no status to sync."

    result = _send_request(cached_statuses)
    if result and "error" in result:
        raise StatusSyncError(result["error"])

    # remove cache
    if os.path.exists(cache_file_path):
        os.remove(cache_file_path)
    return result["message"]


def start_sync_thread(
        default_update_status: StatusEntry,
        interval: int,
        cache_file_path: str,
        include_cache: bool = True,
) -> threading.Thread:
    def sync_loop():
        while True:
            default_update_status.time = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S")
            try:
                sync_status_now(
                    cache_file_path,
                    default_update_status,
                    include_cache,
                )
            except StatusSyncError as e:
                print(f"Exception: {str(e)}")
                log_status(default_update_status, cache_file_path)
            time.sleep(interval)

    sync_thread = threading.Thread(target=sync_loop, daemon=True)
    sync_thread.start()

    return sync_thread


def attempt_status_sync(status: StatusEntry, status_log_file_path: str):
    try:
        sync_status_now(cache_file_path=status_log_file_path,
                        new_status=status)
    except Exception as e:
        log_status(status_entry=status,
                   cache_file_path=status_log_file_path, )
        print(f"An error occurred while syncing status: {e}")


class StatusSyncError(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

## Carsley Dashboard Support
TODO: Readme in construction

install instruction:
```shell
pip install [--verbose] git+https://github.com/Carsley-and-Associates/cs-dashboard-support.git 
```

sample usage:
```python
import CarsleyDashboardSupport as cds
```

Public Interfaces:

    status_types:
        Relevant types (StatusEntry, etc.)

    log_status():
        Log a status to the local cache file.

    sync_status():
        Instantly send a new status and (Optionally) all available status to the dashboard.
        If failed, raise a StatusSyncError with the error message .
        If succeeded, remove the cached statuses.  
    
    schedule_status_sync():
        Create and return a thread that calls sync_status at specified time interval. 
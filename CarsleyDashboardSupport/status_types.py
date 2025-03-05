import inspect
import os
from enum import Enum
import json
from datetime import datetime
from typing import Optional


class StatusType(str, Enum):
    OK = "OK"
    ERROR = "ERROR"


class Severity(str, Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"
    DEBUG = "DEBUG"
    OTHER = "OTHER"


class StatusEntry:
    def __init__(
            self,
            status: StatusType,
            service_id: str,
            client_id: str,
            environment: str,
            time: Optional[datetime] = None,
            error_message: Optional[str] = None,
            severity: Optional[Severity] = None,
            function_name: Optional[str] = None,
            system_log_path: Optional[str] = None,
    ):
        def get_log_snapshot(log_file: str):
            if log_file and os.path.exists(log_file):
                with open(log_file, "r") as f:
                    lines = f.readlines()
                return "".join(["Last 10 lines of the system log file:\n>>>>>>>>>>\n", lines[-10:]])  # Snapshot for the last 10 lines
            return ""

        self.time = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S") if not time else time
        self.status = status
        self.service_id = service_id
        self.client_id = client_id
        self.environment = environment

        if status != StatusType.OK:
            self.error_message = error_message
            self.severity = severity
            self.function = function_name or inspect.currentframe().f_back.f_code.co_name
            self.log_snapshot = get_log_snapshot(system_log_path) if system_log_path else ""

    def as_dict(self):
        data = {
            "time": self.time,
            "status": self.status.value,
            "service_id": self.service_id,
            "client_id": self.client_id,
            "environment": self.environment,
        }
        if self.status != StatusType.OK:
            data.update({
                "error_message": self.error_message,
                "severity": self.severity.value if self.severity else None,
                "function": self.function,
                "log_snapshot": getattr(self, "log_snapshot", None),
            })
        return data

    def as_json_string(self):
        return json.dumps(self.as_dict(), indent=4)

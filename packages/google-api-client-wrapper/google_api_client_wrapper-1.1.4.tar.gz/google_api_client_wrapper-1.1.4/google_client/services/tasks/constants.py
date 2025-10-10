# API Limits and Defaults
MAX_RESULTS_LIMIT = 100
DEFAULT_MAX_RESULTS = 100

# Field Length Limits
MAX_TITLE_LENGTH = 1024
MAX_NOTES_LENGTH = 8192

# Task Status Options
TASK_STATUS_NEEDS_ACTION = "needsAction"
TASK_STATUS_COMPLETED = "completed"

VALID_TASK_STATUSES = [
    TASK_STATUS_NEEDS_ACTION,
    TASK_STATUS_COMPLETED
]

# Default Task List
DEFAULT_TASK_LIST_ID = "@default"

# API Parameter Names
API_PARAM_COMPLETED_MIN = "completedMin"
API_PARAM_COMPLETED_MAX = "completedMax"
API_PARAM_DUE_MIN = "dueMin"
API_PARAM_DUE_MAX = "dueMax"
API_PARAM_SHOW_COMPLETED = "showCompleted"
API_PARAM_SHOW_HIDDEN = "showHidden"
API_PARAM_MAX_RESULTS = "maxResults"

# DateTime Formats
ISO_DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"
RFC3339_FORMAT = "%Y-%m-%dT%H:%M:%S.000Z"
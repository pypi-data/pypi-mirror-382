# Version and package info  
__version__ = "0.1.23"

# Import utilities with graceful error handling for optional dependencies
from .pointr_logger import *
from .pointr_tools import *

# Conditional imports with error handling for system dependencies
try:
    from .pyodbc_helper import *
except ImportError as e:
    import warnings
    warnings.warn(f"pyodbc_helper not available: {e}. Install system ODBC drivers (brew install unixodbc) if needed.", ImportWarning)

try:
    from .pointr_mysql_helper import *
except ImportError as e:
    import warnings
    warnings.warn(f"pointr_mysql_helper not available: {e}", ImportWarning)

try:
    from .pointr_access_right_helper import *
except ImportError as e:
    import warnings
    warnings.warn(f"pointr_access_right_helper not available: {e}", ImportWarning)

try:
    from .pointr_git_helper import *
except ImportError as e:
    import warnings
    warnings.warn(f"pointr_git_helper not available: {e}", ImportWarning)

try:
    from .google_auth import *
except ImportError as e:
    import warnings
    warnings.warn(f"google_auth not available: {e}", ImportWarning)

try:
    from .jira_service import JiraService, create_jira_issue, search_issues
except ImportError as e:
    import warnings
    warnings.warn(f"jira_service not available: {e}", ImportWarning)

try:
    from .pointr_jira_helper import *
except ImportError as e:
    import warnings
    warnings.warn(f"pointr_jira_helper not available: {e}", ImportWarning)

try:
    from .pointr_jira_time_log_helper import *
except ImportError as e:
    import warnings
    warnings.warn(f"pointr_jira_time_log_helper not available: {e}", ImportWarning)

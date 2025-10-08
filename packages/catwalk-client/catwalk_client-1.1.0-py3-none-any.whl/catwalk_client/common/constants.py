from importlib import metadata

CATWALK_CLIENT_VERSION = metadata.version("catwalk_client")

CATWALK_AUTH_HEADER = "Catwalk-Authorization"
CATWALK_CLIENT_LOCATION = "Client-Location"
CATWALK_USER_AGENT_HEADER_VALUE = f"Catwalk-Client/{CATWALK_CLIENT_VERSION}"
CATWALK_CLIENT_THREAD_NAME_PREFIX = "catwalk_client_"

CATWALK_CASE_TRACK_ID_ENDPOINT = "/api/cases/track-id/%s"
CATWALK_GET_CASE_EVALUATIONS_BY_TRACK_ID_ENDPOINT = "/api/evaluation/case/track-id/%s"
CATWALK_CREATE_SESSION_ENDPOINT = "/api/evaluation/sessions"
CATWALK_ADD_CASES_TO_SESSION_ENDPOINT = "/api/evaluation/sessions/%s/cases"
CATWALK_START_SESSION_ENDPOINT = "/api/evaluation/sessions/%s/start"
CATWALK_GET_USERS_ENDPOINT = "/api/auth/users"
CATWALK_CLIENT_LOG_HANDLER = "catwalk_client_log_handler"
CATWALK_CLIENT_LOG_NAME = "catwalk_client"

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from json import loads

from catwalk_common import CommonCaseFormat, OpenCase, EvaluationResult
from pydantic import error_wrappers

from catwalk_client.common import CatwalkHTTPClient
from catwalk_client.common.constants import (
    CATWALK_ADD_CASES_TO_SESSION_ENDPOINT,
    CATWALK_CLIENT_THREAD_NAME_PREFIX,
    CATWALK_CASE_TRACK_ID_ENDPOINT,
    CATWALK_CREATE_SESSION_ENDPOINT,
    CATWALK_GET_CASE_EVALUATIONS_BY_TRACK_ID_ENDPOINT,
    CATWALK_CLIENT_LOG_NAME,
    CATWALK_GET_USERS_ENDPOINT,
    CATWALK_START_SESSION_ENDPOINT,
)
from catwalk_client.common.logger import init_logger
from catwalk_client.common._session import SessionConfig
from catwalk_client.tools import CaseBuilder, CaseExporter, CaseExporterV2, SORT_ORDER


class CatwalkClient:
    log = init_logger(CATWALK_CLIENT_LOG_NAME)

    def __init__(
        self,
        submitter_name: str | None = None,
        submitter_version: str | None = None,
        catwalk_url: str | None = None,
        auth_token: str | None = None,
        insecure: bool = True,
        timeout: int = 30,
        timezone: str = "UTC",
        concurrent: bool = False,
        max_workers: int = 4,
    ):
        self.http_client = CatwalkHTTPClient(
            catwalk_url, auth_token, insecure, timeout, timezone
        )
        self.submitter_name = submitter_name
        self.submitter_version = submitter_version
        self._max_workers = max_workers
        self._concurrent = concurrent

        if self._concurrent:
            self._executor = ThreadPoolExecutor(
                max_workers=self._max_workers,
                thread_name_prefix=CATWALK_CLIENT_THREAD_NAME_PREFIX,
            )
        else:
            self._executor = None

    def __setattr__(self, __name, __value):
        if __name != "http_client" and __name in self.http_client.__dict__.keys():
            self.log.warn(
                f" [DEPRECATED] Usage of 'CatwalkClient.{__name}=<value>' is DEPRECATED. Please use 'set_{__name}' method!"
            )
            self.http_client.__dict__[__name] = __value

        self.__dict__[__name] = __value

    def set_auth_token(self, auth_token: str):
        self.http_client.auth_token = auth_token

    def set_catwalk_url(self, catwalk_url: str):
        self.http_client.url = catwalk_url

    def set_insecure(self, insecure: bool):
        self.http_client.insecure = insecure

    def new_case(self) -> CaseBuilder:
        return CaseBuilder(client=self)

    def alter_case(self, track_id: str) -> CaseBuilder | None:
        """Get CaseBuilder object filled with details of desired case. It fetches
        the case with a given `track_id` and fills CaseBuilder fields with fetched
        case's query, context, response and metadata information.

        Args:
            track_id (str): Track ID of a case.

        Returns:
            CaseBuilder | None: Object filled with case details of a case with given track ID.
            Returns None on an unsuccessful case fetch operation.
        """
        case = self.get_case(track_id)

        if not case:
            return None

        case_builder = self.new_case()
        case_builder._track_id = case.track_id
        case_builder._query = [query.dict() for query in case.query]
        case_builder._context = [context.dict() for context in case.context]
        case_builder._response = [response.dict() for response in case.response]
        case_builder._metadata = case.metadata

        return case_builder

    def send(self, case: dict):
        if self._concurrent and self._executor:
            self._executor.submit(self._send, case)
        else:
            self._send(case)

    def _send(self, case: dict):
        try:
            case: CommonCaseFormat = CommonCaseFormat(
                submitter={
                    "name": self.submitter_name,
                    "version": self.submitter_version,
                },
                **case,
            )

            response, success, _ = self.http_client.post(
                "/api/cases/collect", case.dict()
            )

            if success:
                case_id = loads(response)["id"]
                self.log.info(f"Collected catwalk case: {case_id}")
            else:
                self.log.error(f"Couldn't collect the case.\n{response}")
        except error_wrappers.ValidationError as ex:
            self.log.error(f"ValidationError: \n{ex}")
        except Exception as ex:
            self.log.error(f"{type(ex).__name__}: \n{str(ex)}\n{ex.__traceback__}")

    def export_cases(
        self,
        from_datetime: datetime,
        to_datetime: datetime,
        submitter_name: str | None = None,
        submitter_version: str | None = None,
        max_retries: int = 5,
        limit: int | None = 100,
    ):
        exporter = CaseExporter(
            http_client=self.http_client,
            from_datetime=from_datetime,
            to_datetime=to_datetime,
            submitter_name=submitter_name or self.submitter_name,
            submitter_version=submitter_version or self.submitter_version,
            max_retries=max_retries,
            limit=limit,
        )
        yield from exporter.export()

    def export_cases_v2(
        self,
        submitter_name: str | None = None,
        submitter_version: str | None = None,
        datetime_from: datetime | None = None,
        datetime_to: datetime = datetime.now(),
        sort_by: list[str] | str | None = None,
        sort_order: list[SORT_ORDER] | SORT_ORDER = "desc",
        limit: int | None = 100,
        offset: int = 0,
        max_retries: int = 5,
    ):
        """Export cases using the v2 export endpoint.

        Args:
            submitter_name (Optional[str], optional): Name of submitter to export. Defaults to None.
            submitter_version (Optional[str], optional): Version of submitter to export. Defaults to None.
            datetime_from (Optional[datetime], optional): Lower boundary of case creation date. Defaults to None.
            datetime_to (datetime, optional): Upper boundary of case creation date. Defaults to current time.
            sort_by (Union[list[str], str, None], optional): Field(s) by which exported cases will be ordered. Defaults to None.
            sort_order (Union[list[SORT_ORDER], SORT_ORDER], optional): Order(s) by which exported cases will be ordered. Defaults to "desc".
            limit (int, optional): Size limit of a single batch fetched from the API (not overall limit).
                                   Defaults to 100. Must be a positive integer if not None. If a maximum limit is set, limit must obey it.
            offset (int, optional): Starting offset of fetched data. Defaults to 0.
            max_retries (int, optional): Maximum number of retries in case the request does not succeed. Defaults to 5.

        Yields:
            OpenCase: Cases returned by the API.
        """
        exporter = CaseExporterV2(
            http_client=self.http_client,
            submitter_name=submitter_name or self.submitter_name,
            submitter_version=submitter_version or self.submitter_version,
            datetime_from=datetime_from,
            datetime_to=datetime_to,
            sort_by=sort_by,
            sort_order=sort_order,
            limit=limit,
            offset=offset,
            max_retries=max_retries,
        )
        yield from exporter.export()

    def get_case(self, track_id: str) -> OpenCase | None:
        """Get case that's track_id matches a given string.

        Args:
            track_id (str): Case's track_id.

        Returns:
            OpenCase: Case in a Common Case Format with some additional information
            like creation date, id, status and archivization status. Returns None
            on HTTP error.
        """
        path = CATWALK_CASE_TRACK_ID_ENDPOINT % track_id
        response, success, _ = self.http_client.get(path)

        if success:
            case = OpenCase.parse_obj(loads(response))
            return case
        else:
            self.log.info(f"Couldn't fetch the case.\n{response}")
            return None

    def get_case_evaluation_results(
        self, track_id: str
    ) -> list[EvaluationResult] | None:
        """Get evaluation results of a case that's track_id matches a given string.

        Args:
            track_id (str): Case's track_id.

        Returns:
            list[EvaluationResult] | None: List of evaluations of a given case. Returns
            None on HTTP error.
        """
        path = CATWALK_GET_CASE_EVALUATIONS_BY_TRACK_ID_ENDPOINT % track_id
        response, success, _ = self.http_client.get(path)

        if success:
            evaluations = loads(response)["evaluations"]
            return [EvaluationResult.parse_obj(ev) for ev in evaluations]
        else:
            self.log.info(f"Couldn't fetch evaluation results.\n{response}")
            return None

    def update(self, track_id: str, case: dict):
        """Send given case details in order to update a case. `track_id` is
        required in order to update a case.

        Args:
            track_id (str): Track ID of a case.
            case (dict): New case details (`query`, `context`, `response`, `metadata`).
        """
        try:
            case: CommonCaseFormat = CommonCaseFormat(
                submitter={
                    "name": self.submitter_name,
                    "version": self.submitter_version,
                },
                **case,
            )

            path = CATWALK_CASE_TRACK_ID_ENDPOINT % track_id
            response, success, _ = self.http_client.patch(path, case.dict())

            if success:
                track_id = loads(response)["track_id"]
                self.log.info(f" Updated case with track_id: {track_id}")
            else:
                self.log.error(f" Couldn't update the case. {response}")
        except error_wrappers.ValidationError as ex:
            self.log.error(f" ValidationError: \n{ex}")
        except Exception as ex:
            self.log.error(f" {type(ex).__name__}: \n{str(ex)}\n{ex.__traceback__}")

    def create_session(self, name: str, description: str = "") -> str | None:
        """Create a Catwalk evaluation session.

        Args:
            name (str): Name of a session.
            description (str, optional): Session description. Defaults to "".

        Returns:
            str | None: Created session ID. Returns `None` when there was an
            error while creating a session.
        """
        payload = {
            "name": name,
            "description": description,
        }
        response, success, _ = self.http_client.post(
            CATWALK_CREATE_SESSION_ENDPOINT, payload
        )

        if not success:
            self.log.error(
                f"There was an error while trying to create a session.\n{response}"
            )
            return None

        session_id = loads(response)["session_id"]
        self.log.info(f'Created session "{name}" with ID: {session_id}')

        return session_id

    def add_cases_to_session(
        self, session_id: str, track_ids: list[str]
    ) -> list[str] | None:
        """Add cases to the session using track IDs.

        Args:
            session_id (str): ID of a session.
            track_ids (list[str]): List of cases' track IDs.

        Returns:
            list[str] | None: List of IDs of created session cases.
            Returns `None` when there was an error while assigning
            cases to the session.
        """
        payload = {"track_ids": track_ids}
        path = CATWALK_ADD_CASES_TO_SESSION_ENDPOINT % session_id
        response, success, _ = self.http_client.post(path, payload)

        if not success:
            self.log.error(
                f"There was an error while trying to add cases to the session.\n{response}"
            )
            return None

        session_case_ids = loads(response)["session_case_ids"]
        self.log.info(
            f"Added {len(session_case_ids)} of {len(track_ids)} cases to session with ID: {session_id}"
        )

        return session_case_ids

    def start_session(
        self,
        session_id: str,
        assign_to: list[str] = [],
        session_config: SessionConfig = SessionConfig(),
    ) -> bool:
        """Start a session.

        Args:
            session_id (str): ID of a session.
            assign_to (list[str]): List of users' emails that will be
            assigned as the session evaluators. Session is always assigned
            to the owner, even when his email is not provided. Defaults to
            [].
            session_config (SessionConfig, optional): Session configuration.
            Defaults to SessionConfig() (default configuration).

        Returns:
            bool: Boolean value that informs whether the session has
            been successfully started.
        """
        response, success, _ = self.http_client.get(CATWALK_GET_USERS_ENDPOINT)

        if not success:
            self.log.error(f"There was an error while fetching users list.\n{response}")
            return False

        users = loads(response)["users"]
        users = [user["id"] for user in users if user["email"] in assign_to]

        payload = {"assigned_users": users, "config": session_config.dict()}
        path = CATWALK_START_SESSION_ENDPOINT % session_id
        response, success, _ = self.http_client.post(path, payload)

        if not success:
            self.log.error(
                f"There was an error while trying to start the session.\n{response}"
            )
            return False

        self.log.info(f"Session {session_id} has been successfully started")
        return True

    def initiate_session(
        self,
        name: str,
        track_ids: list[str],
        assign_to: list[str] = [],
        session_config: SessionConfig = SessionConfig(),
        description: str = "",
    ) -> tuple[str | None, list[str] | None]:
        """Create, assign cases and start a session.

        Args:
            name (str): Name of a session.
            track_ids (list[str]): List of cases' track IDs.
            assign_to (list[str]): List of users' emails that will be
            assigned as the session evaluators. Session is always assigned
            to the owner, even when his email is not provided. Defaults to
            [].
            session_config (SessionConfig, optional): Session configuration.
            Defaults to SessionConfig() (default configuration).
            description (str, optional): Session description. Defaults to "".

        Returns:
            tuple[str, list[str]] | None: Tuple that contains two values. First
            one is a created session ID and a second one is a list of created
            session case ID from assigned cases. Returns `tuple[None, None]` if
            there was an error during session initiation.
        """
        if not track_ids:
            self.log.error("Session requires at least one case to be assigned to it!")
            return None, None

        response, success, _ = self.http_client.get(CATWALK_GET_USERS_ENDPOINT)

        if not success:
            self.log.error(f"There was an error while fetching users list.\n{response}")
            return None, None

        users = loads(response)["users"]
        users = [user["id"] for user in users if user["email"] in assign_to]

        response, success, _ = self.http_client.post(
            "/api/evaluation/sessions/initiate",
            {
                "name": name,
                "description": description,
                "track_ids": track_ids,
                "assigned_users": users,
                "config": session_config.dict(),
            },
        )

        if not success:
            self.log.error(
                f"There was an error while trying to initiate a session.\n{response}"
            )
            return None, None

        res = loads(response)
        session_id = res["session_id"]
        session_case_ids = res["session_case_ids"]
        self.log.info(f"Session {session_id} has been successfully initiated")
        return session_id, session_case_ids

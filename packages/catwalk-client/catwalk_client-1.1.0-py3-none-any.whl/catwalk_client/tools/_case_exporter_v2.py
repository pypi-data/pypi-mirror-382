from __future__ import annotations

import time
from json import loads
from datetime import datetime
from typing import Literal

from catwalk_common import OpenCase

from catwalk_client.common.catwalk_http_client import CatwalkHTTPClient
from catwalk_client.common.exception import CatwalkClientException
from catwalk_client.common.logger import init_logger

log = init_logger()

SORT_ORDER = Literal["asc", "desc"]


class CaseExporter:
    def __init__(
        self,
        http_client: CatwalkHTTPClient,
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
        """Create CaseExporter object (EXPORT V2).

        Args:
            submitter_name (Optional[str], optional): Name of submitter to export. Defaults to None.
            submitter_version (Optional[str], optional): Version of submitter to export. Defaults to None.
            datetime_from (Optional[datetime], optional): Lower boundary of case creation date. Defaults to None.
            datetime_to (datetime, optional): Upper boundary of case creation date. Defaults to current time.
            sort_by (Union[list[str], str, None], optional): Field(s) by which exported cases will be ordered. Defaults to None.
            sort_order (Union[list[SORT_ORDER], SORT_ORDER], optional): Order(s) by which exported cases will be ordered. Defaults to "desc".
            limit (int, optional): Limit of a single batch fetched from the API (not overall limit).
                                   Defaults to 100. Must be a postitive integer if not None. If a maximum limit is set, limit must obey it.
            offset (int, optional): Starting offset of fetched data. Defaults to 0.
            max_retries (int, optional): Maximum number of retries in case the request does not succeed. Defaults to 5.
        """
        self.path = "/api/v2/cases/export"
        self.http_client = http_client
        self.max_retries = max_retries

        self.submitter_name = submitter_name
        self.submitter_version = submitter_version
        self.datetime_from = datetime_from
        self.datetime_to = datetime_to
        self.sort_by = sort_by
        self.sort_order = sort_order
        self.limit = limit
        self.offset = offset

    def export(self):
        """Fetch cases in form of a generator where each element of is a case.

        Yields:
            OpenCase: Cases returned by the API.
        """
        current_retry = 0
        while True:
            response, success, status_code = self.http_client.get(
                self.path, self._get_query_params()
            )

            retry = status_code < 0 or status_code >= 500
            if not success and retry:
                self._handle_retry(current_retry, response)
                current_retry += 1
                continue
            elif not success:
                raise CatwalkClientException(response)

            current_retry = 0
            data = loads(response)

            for case in data["cases"]:
                yield OpenCase.parse_obj(case)

            if self.limit:
                if len(data["cases"]) < self.limit:
                    break
            else:
                break

            self.offset += self.limit

    def _handle_retry(self, retry: int, response: str):
        """Check if the unsuccessful call can be retried and apply delay to the next call.

        Args:
            retry (int): Current retry.
            response (str): Response of an unsuccessful call.

        Raises:
            CatwalkClientException: When the maximum number of retries is exceeded.
        """
        if retry < self.max_retries:
            multiplier = (retry * 2) or 1
            log.warning(
                f"Retry ({retry + 1}/{self.max_retries}) because got error {response}"
            )
            time.sleep(0.5 * multiplier)
        else:
            raise CatwalkClientException("Max retries exceeded")

    def _get_query_params(self):
        """Return query params in form of a list of tuples.

        Returns:
            list[tuple[str, Any]]: List of tuples where first element is a query param key and the second is its value.
        """
        query_params = [
            (k, v)
            for k, v in {
                "submitter_name": self.submitter_name,
                "submitter_version": self.submitter_version,
                "datetime_from": self.datetime_from.isoformat(),
                "datetime_to": self.datetime_to.isoformat(),
                "limit": self.limit,
                "offset": self.offset,
            }.items()
            if v is not None
        ]

        if self.sort_by:
            query_params += [
                ("sort_by", sb) for sb in self._parse_list_query_param(self.sort_by)
            ]

        if self.sort_order:
            query_params += [
                ("sort_order", so)
                for so in self._parse_list_query_param(self.sort_order)
            ]

        return query_params

    def _parse_list_query_param(self, list_param: list | str) -> list[str]:
        """Check if given value is a string, if yes return it as a list with a single string.

        Args:
            list_param (Union[list, str]): Value to parse.

        Returns:
            list[str]: Parsed given value to list of strings.
        """
        param = list_param
        if not isinstance(list_param, list):
            param = [list_param]
        return param

from __future__ import annotations

import time
from datetime import datetime, timedelta
from json import loads

from catwalk_common import OpenCase

from catwalk_client.common import CatwalkHTTPClient
from catwalk_client.common.exception import CatwalkClientException
from catwalk_client.common.logger import init_logger

log = init_logger()


class CaseExporter:
    def __init__(
        self,
        http_client: CatwalkHTTPClient,
        from_datetime: datetime,
        to_datetime: datetime,
        submitter_name: str | None = None,
        submitter_version: str | None = None,
        max_retries: int = 5,
        batch: int = 1,
        limit: int | None = 100,
    ):
        self.http_client = http_client

        self.from_datetime = from_datetime
        self.to_datetime = to_datetime

        self.filters = self._build_filters(
            submitter_name, submitter_version, from_datetime, to_datetime, limit
        )
        self.max_retries = max_retries
        self.batch = batch

    def export(self):
        for date in self._hour_range():
            current_retry = 0
            path = f"/api/cases/export/{date.year}/{date.month}/{date.day}/{date.hour}"
            next_part = False

            while path:
                response, success, status_code = self.http_client.get(
                    path, None if next_part else self.filters
                )
                retry = status_code < 0 or status_code >= 500
                if not success and retry:
                    self._handle_retry(current_retry, response)
                    current_retry += 1
                    continue
                elif not success:
                    raise CatwalkClientException(response)

                path = None
                next_part = False
                data = loads(response)
                for item in data["items"]:
                    yield OpenCase.parse_obj(item)

                if data["next_part"] and data["items"]:
                    next_part = True
                    path = str(data["next_part"]).replace(
                        self.http_client.get_url(""), ""
                    )

    def _handle_retry(self, current_retry: int, response):
        if current_retry < self.max_retries:
            multiplier = (current_retry * 2) or 1
            log.error(
                f"\n[catwalk-export] Retry ({current_retry + 1}/{self.max_retries}) "
                f"because got error {response} "
            )
            time.sleep(0.5 * multiplier)
        else:
            raise CatwalkClientException("Max retries exceeded")

    @staticmethod
    def _build_filters(
        submitter_name: str,
        submitter_version: str,
        from_datetime: datetime,
        to_datetime: datetime,
        limit: int | None = 100,
    ):
        filters = {
            "submitter_name": submitter_name,
            "submitter_version": submitter_version,
            "from_timestamp": from_datetime.isoformat(),
            "to_timestamp": to_datetime.isoformat(),
            "limit": limit,
        }
        return {k: v for k, v in filters.items() if v is not None}

    def _hour_range(self):
        start, end = self.from_datetime, self.to_datetime

        while start < end:
            yield start
            start += timedelta(hours=1)

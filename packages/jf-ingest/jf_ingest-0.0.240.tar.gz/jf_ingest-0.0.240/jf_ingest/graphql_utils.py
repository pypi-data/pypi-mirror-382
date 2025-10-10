import json
import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional, cast

from requests import Response, Session

from jf_ingest.utils import retry_for_status

logger = logging.getLogger(__name__)


GQL_PAGE_INFO_BLOCK = "pageInfo {hasNextPage, endCursor}"
GQL_RATELIMIT_INFO_BLOCK = "rateLimit {cost, remaining, resetAt}"


@dataclass
class GQLRateLimit:
    remaining: int
    reset_at: datetime


class GqlRateLimitedExceptionInner(Exception):
    pass


def gql_format_to_datetime(datetime_str: str) -> datetime:
    """Attempt to formate a datetime str from the GQL format to a python Datetime Object
    NOTE: This is the format shared by the Github and Gitlab GQL clients

    Args:
        datetime_str (str): The datetime from graphql

    Returns:
        datetime: A valid, timezone aware datetime
    """
    return datetime.strptime(datetime_str, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)


def _gql_query_has_next_page(objects_query: dict) -> bool:
    return bool(objects_query.get('pageInfo', {}).get('hasNextPage', False))

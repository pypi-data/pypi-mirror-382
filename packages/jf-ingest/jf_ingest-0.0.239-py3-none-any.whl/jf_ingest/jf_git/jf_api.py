import logging
from typing import Union

import requests

from jf_ingest import logging_helper
from jf_ingest.config import GitConfig, IngestionConfig
from jf_ingest.jf_git.standardized_models import StandardizedJFAPIPullRequest
from jf_ingest.jf_jira.custom_fields import JELLYFISH_API_TIMEOUT
from jf_ingest.utils import retry_for_status

JF_GHC_PR_USER_ENDPOINT = '/endpoints/agent/github-prs-with-null-users'
JF_GHC_PR_REVIEW_USER_ENDPOINT = '/endpoints/agent/github-pr-reviews-with-null-users'

logger = logging.getLogger(__name__)


def get_jf_github_null_user_pr_data(
    ingest_config: IngestionConfig, git_config: GitConfig, pr_reviews: bool = False
) -> Union[list[StandardizedJFAPIPullRequest], None]:
    """
    Get any PRs or PR reviews with missing mannequin user data in the JF database for a given GHC instance
    """
    headers = {"Jellyfish-API-Token": ingest_config.jellyfish_api_token}
    api_endpoint = JF_GHC_PR_REVIEW_USER_ENDPOINT if pr_reviews else JF_GHC_PR_USER_ENDPOINT

    logger.info(f"Making a request to the Jellyfish API at {api_endpoint}")

    try:
        r = retry_for_status(
            _make_ghc_pr_user_request,
            f"{ingest_config.jellyfish_api_base}{api_endpoint}",
            git_config.instance_slug,
            headers,
            max_retries_for_retry_for_status=2,
            statuses_to_retry=[504],
        )
    except Exception as e:
        # This isn't essential for ingest to continue, so just log the error and return
        logging_helper.send_to_agent_log_file(
            f'Error when attempting to pull PRs with missing mannequin user data from Jellyfish: {e}',
            exc_info=True,
            level=logging.ERROR,
        )
        return None

    try:
        r_json = r.json()
        return [StandardizedJFAPIPullRequest(**pr) for pr in r_json['pull_requests']]
    except Exception as e:
        logging_helper.send_to_agent_log_file(
            f'Error when attempting to parse PRs with missing mannequin user data from Jellyfish: {e}',
            exc_info=True,
            level=logging.ERROR,
        )

    return []


def _make_ghc_pr_user_request(
    api_url: str, git_instance_slug: str, headers: dict[str, str]
) -> requests.Response:
    try:
        r = requests.get(
            f"{api_url}?git-instance-slug={git_instance_slug}",
            headers=headers,
            timeout=JELLYFISH_API_TIMEOUT,
        )
        r.raise_for_status()
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 400:
            logging_helper.send_to_agent_log_file(
                f'GHC instance {git_instance_slug} is not a Github Cloud instance',
                level=logging.ERROR,
            )
            raise e
    except Exception as e:
        logging_helper.send_to_agent_log_file(
            f'Error when attempting to pull data from Jellyfish for endpoint {api_url}',
            exc_info=True,
            level=logging.ERROR,
        )
        raise e

    return r

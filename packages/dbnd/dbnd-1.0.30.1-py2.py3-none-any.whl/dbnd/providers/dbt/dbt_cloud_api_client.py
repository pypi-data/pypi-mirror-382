# © Copyright Databand.ai, an IBM Company 2022

import logging
import urllib

from http import HTTPStatus
from typing import Union

from requests import HTTPError, Session
from requests.adapters import HTTPAdapter
from requests.packages.urllib3 import __version__ as urllib_version
from requests.packages.urllib3.util.retry import Retry

from dbnd._core.errors.errors_utils import log_exception


logger = logging.getLogger(__name__)


class DbtCloudApiClient:
    ADMINISTRATIVE_API_SUFFIX = "api/v2/accounts/"
    DEFAULT_API_NETLOC = "cloud.getdbt.com"
    DEFAULT_METADATA_API_URL = "https://metadata.cloud.getdbt.com/graphql/"

    def __init__(
        self,
        account_id: int,
        dbt_cloud_api_token: str,
        dbt_api_url: str,
        max_retries=3,
        supress_exceptions=True,
    ):
        self.account_id = account_id
        self.api_token = dbt_cloud_api_token
        self.administrative_api_url = urllib.parse.urljoin(
            dbt_api_url, self.ADMINISTRATIVE_API_SUFFIX
        )
        if urllib.parse.urlparse(dbt_api_url).netloc == self.DEFAULT_API_NETLOC:
            self.metadata_api_url = self.DEFAULT_METADATA_API_URL
        else:
            self.metadata_api_url = urllib.parse.urljoin(
                dbt_api_url.replace(".", ".metadata.", 1), "/graphql/"
            )
        self._supress_exceptions = supress_exceptions
        self.session = Session()
        self.session.headers = {
            "Authorization": f"Token {self.api_token}",
            "X-dbt-partner-source": "Databand",
        }
        allowed_methods_kw = (
            "method_whitelist" if urllib_version.startswith("1.") else "allowed_methods"
        )
        retry_strategy = Retry(
            total=max_retries,
            status_forcelist=[429, 500, 502, 503, 504],
            backoff_factor=1,
            **{
                allowed_methods_kw: [
                    "HEAD",
                    "GET",
                    "PUT",
                    "DELETE",
                    "OPTIONS",
                    "TRACE",
                    "POST",
                ]
            },
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)

    def get_account_details(self):
        url = self._build_administrative_url(f"{self.account_id}")
        return self.send_request(endpoint=url)

    def send_request(self, endpoint, method="GET", data={}):
        try:
            if method == "POST":
                res = self.session.post(url=endpoint, json=data)
            elif method == "GET":
                res = self.session.get(url=endpoint, params=data)

            # raise exception for status code != 2**
            res.raise_for_status()
            deserialized_res = res.json()
        except HTTPError as http_error:
            if not self._supress_exceptions:
                raise
            # We want to send server all errors that are not 404 response
            if http_error.response.status_code != HTTPStatus.NOT_FOUND:
                logger.debug("Received unexpected response code from dbt cloud api")
                log_exception("unexpected response code from dbt cloud api", http_error)
            return None
        except Exception as e:
            if not self._supress_exceptions:
                raise
            log_exception("Something went wrong getting data dbt cloud api", e)
            return None

        return deserialized_res

    def _get_run_artifact(self, artifact_name, run_id, step=1):
        path = f"{self.account_id}/runs/{run_id}/artifacts/{artifact_name}"
        url = self._build_administrative_url(path)
        try:
            return self.send_request(endpoint=url, data={"step": step})
        except HTTPError as http_error:
            # Since we don't know if step has artifact or not, we try to get it and raise exception in case status code is not not foud error
            if http_error.response.status_code != HTTPStatus.NOT_FOUND:
                raise

            return None

    def get_manifest_artifact(self, run_id, step=1):
        return self._get_run_artifact(
            artifact_name="manifest.json", run_id=run_id, step=step
        )

    def get_run_results_artifact(self, run_id, step=1):
        return self._get_run_artifact(
            artifact_name="run_results.json", run_id=run_id, step=step
        )

    def get_run(self, run_id):
        if not run_id:
            logger.debug("Can't get run without id")
            return

        path = f"{self.account_id}/runs/{run_id}"
        url = self._build_administrative_url(path)
        res = self.send_request(
            endpoint=url, data={"include_related": '["run_steps", "job"]'}
        )
        return self._safe_get_response_data(res)

    def get_environment(self, env_id: int):
        url = self._build_administrative_url(f"{self.account_id}/environments/{env_id}")
        res = self.send_request(endpoint=url)
        return self._safe_get_response_data(res)

    def get_project_name(self, dbt_project_id: int) -> Union[str, None]:
        if not dbt_project_id:
            logger.warning("Can't locate project name without provided project id")
            return None

        path = f"{self.account_id}/projects/{dbt_project_id}"
        url = self._build_administrative_url(path)

        res = self.send_request(endpoint=url)
        project = self._safe_get_response_data(res)
        return project["name"]

    def list_environments(self):
        url = self._build_administrative_url(f"{self.account_id}/environments/")
        res = self.send_request(endpoint=url)
        return self._safe_get_response_data(res)

    def query_dbt_run_results(self, job_id, run_id):
        query = self._build_graphql_query(
            "models",
            {"runId": run_id, "jobId": job_id},
            ["uniqueId", "executionTime", "status"],
        )
        return self.query_meta_data_api(query)

    def query_dbt_test_results(self, job_id, run_id):
        query = self._build_graphql_query(
            "tests", {"runId": run_id, "jobId": job_id}, ["uniqueId", "status"]
        )
        return self.query_meta_data_api(query)

    def list_runs(self, limit, offset, order_by="-created_at", job_id=None):
        # https://docs.getdbt.com/dbt-cloud/api-v2#/operations/List%20Runs
        path = f"{self.account_id}/runs"
        url = self._build_administrative_url(path)
        data = {"limit": limit, "offset": offset, "order_by": order_by}
        if job_id:
            data["job_definition_id"] = job_id
        res = self.send_request(endpoint=url, data=data)
        safe_response = self._safe_get_response_data(res)
        return safe_response or []

    def query_meta_data_api(self, query):
        res = self.send_request(
            endpoint=self.metadata_api_url, method="POST", data={"query": query}
        )
        return self._safe_get_response_data(res)

    def _build_graphql_query(self, resource, filters={}, requested_fields=[]):
        normalized_requested_fields = ",\n".join(requested_fields)
        normalized_filters = ",".join([f"{k}: {v}" for k, v in filters.items()])
        return f"""{{
{resource}({normalized_filters}){{
{normalized_requested_fields}
}}
}}"""

    def _build_administrative_url(self, path):
        return urllib.parse.urljoin(self.administrative_api_url, path)

    def _safe_get_response_data(self, res):
        if res and isinstance(res, dict):
            return res.get("data", None)
        return None

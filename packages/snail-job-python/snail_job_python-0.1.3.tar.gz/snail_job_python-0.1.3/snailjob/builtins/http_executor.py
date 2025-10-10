import json
from typing import Any, Dict, Optional

import requests
from pydantic import BaseModel, Field

from snailjob.args import JobArgs
from snailjob.builtins._base import AbstractExecutor
from snailjob.deco import job
from snailjob.schemas import ExecuteResult

DEFAULT_TIMEOUT = 60
HTTP_SUCCESS_CODE = 200


class HttpParams(BaseModel):
    method: str = Field("GET", description="HTTP method")
    url: str = Field(..., description="URL")
    media_type: Optional[str] = Field(None, description="Content-Type")
    headers: Optional[Dict[str, str]] = Field(default_factory=dict, description="HTTP headers")
    body: Optional[str] = None
    timeout: Optional[int] = DEFAULT_TIMEOUT
    wf_context: Optional[Dict[str, Any]] = Field(
        default_factory=dict, description="Workflow context"
    )


class AbstractHttpExecutor(AbstractExecutor):
    def process(self, http_params: HttpParams) -> ExecuteResult:
        self._validate_and_set_url(http_params)
        self._set_default_method_and_body(http_params)
        self._set_default_media_type(http_params)

        self.log_info(
            f"Request URL: {http_params.url}\n"
            f"Using request method: {http_params.method}\n"
            f"Request timeout: {http_params.timeout} seconds"
        )

        return self._execute_request(http_params)

    def _execute_request(self, http_params: HttpParams) -> ExecuteResult:
        try:
            method = http_params.method
            url = http_params.url
            headers = http_params.headers
            data = http_params.body
            timeout = http_params.timeout

            response = requests.request(
                method=method,
                url=url,
                headers=headers,
                data=data,
                timeout=timeout,
            )

            if response.status_code != HTTP_SUCCESS_CODE:
                self.log_error(
                    f"{method.upper()} request to URL: {url} "
                    f"failed with code: {response.status_code}, "
                    f"response body: {response.text}"
                )
                return ExecuteResult.failure("HTTP request failed")

            return ExecuteResult.success(response.text)

        except Exception as e:
            self.log_error(f"HTTP internal executor failed: {str(e)}")
            return {"success": False, "message": str(e)}

    def _validate_and_set_url(self, http_params: HttpParams):
        if not http_params.url:
            raise ValueError("URL cannot be empty.")

        if not http_params.url.startswith(("http://", "https://")):
            http_params.url = f"http://{http_params.url}"

    def _set_default_method_and_body(self, http_params: HttpParams):
        if http_params.method in ("POST", "PUT") and http_params.body is None:
            http_params.body = json.dumps({})
            self.log_warn(f"Using default request body: {http_params.body}")

    def _set_default_media_type(self, http_params: HttpParams):
        if (
            http_params.method in ("POST", "PUT")
            and http_params.body is not None
            and not http_params.media_type
        ):
            try:
                json.loads(http_params.body)
                http_params.media_type = "application/json"
                self.log_warn("Using 'application/json' as media type")
            except json.JSONDecodeError:
                pass


class SnailJobHttpExecutor(AbstractHttpExecutor):
    def job_execute(self, job_args: JobArgs) -> ExecuteResult:
        http_params = HttpParams(**json.loads(job_args.job_params))
        http_params.wf_context = job_args.wf_context or {}
        http_params.method = http_params.method.upper()
        http_params.headers = http_params.headers or {}
        return self.process(http_params)


@job("snailJobHttpExecutor")
def executor(job_args: JobArgs) -> ExecuteResult:
    return SnailJobHttpExecutor().job_execute(job_args)

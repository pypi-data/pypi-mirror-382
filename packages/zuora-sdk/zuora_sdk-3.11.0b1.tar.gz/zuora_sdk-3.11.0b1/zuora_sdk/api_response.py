"""API response object."""

from __future__ import annotations
from typing import Optional, Generic, Mapping, TypeVar
from pydantic import Field, StrictInt, StrictBytes, BaseModel

T = TypeVar("T")

class ApiResponse(BaseModel, Generic[T]):
    """
    API response object
    """

    status_code: StrictInt = Field(description="HTTP status code")
    headers: Optional[Mapping[str, str]] = Field(None, description="HTTP headers")
    data: T = Field(description="Deserialized data given the data type")
    raw_data: StrictBytes = Field(description="Raw data (HTTP response body)")

    content_encoding: str = Field("", description="Content encoding")
    rate_limit_limit: str = Field("", description="Rate limit limit")
    rate_limit_remaining: int = Field(0, description="Number of remaining requests in the current time window")
    rate_limit_reset: int = Field(0, description="Time until the rate limit resets in seconds")
    zuora_track_id: str = Field("", description="Zuora track ID for tracing the API call")
    zuora_request_id: str = Field("", description="Zuora internal request ID")
    concurrency_limit_type: str = Field("", description="Type of concurrency limit (Default or High-volume transactions)")
    concurrency_limit_limit: int = Field(0, description="Total number of permitted concurrent requests")
    concurrency_limit_remaining: int = Field(0, description="Remaining number of permitted concurrent requests")


    model_config = {
        "arbitrary_types_allowed": True
    }

    def __init__(self, **data):
        super().__init__(**data)
        self.parse_and_set_response_headers()

    def parse_and_set_response_headers(self):
        """
        Set response header related variables by parsing response headers.
        """
        try:
            if self.headers is not None:
                for key, values in self.headers.items():
                    key = key.lower()
                    if values is None:
                        continue
                    value = values[0] if type(values) == list and len(values) > 0 else str(values)

                    if key == "content-encoding":
                        self.content_encoding = value
                    elif key == "ratelimit-limit":
                        self.rate_limit_limit = value
                    elif key == "ratelimit-remaining":
                        self.rate_limit_remaining = int(value)
                    elif key == "ratelimit-reset":
                        self.rate_limit_reset = int(value)
                    elif key == "zuora-request-id":
                        self.zuora_request_id = value
                    elif key == "zuora-track-id":
                        self.zuora_track_id = value
                    elif key == "concurrency-limit-type":
                        self.concurrency_limit_type = value
                    elif key == "concurrency-limit-limit":
                        self.concurrency_limit_limit = int(value)
                    elif key == "concurrency-limit-remaining":
                        self.concurrency_limit_remaining = int(value)
        except Exception as e:
            print(e)

    def get_status_code(self) -> int:
        """
        Get the status code.

        :return: the status code
        """
        return self.status_code

    def get_headers(self) -> Optional[Mapping[str, str]]:
        """
        Get the headers.

        :return: a dictionary of headers
        """
        return self.headers

    def get_zuora_request_id(self) -> str:
        """
        Get Zuora internal identifier of the API call. You cannot control the value of this header.

        :return: the Zuora request ID
        """
        return self.zuora_request_id

    def get_content_encoding(self) -> str:
        """
        Gets the content encoding.

        :return: the content encoding
        """
        return self.content_encoding

    def get_rate_limit_limit(self) -> str:
        """
        Gets the request limit quota for the time window closest to exhaustion.

        :return: the rate limit limit
        """
        return self.rate_limit_limit

    def get_rate_limit_remaining(self) -> int:
        """
        Gets the number of requests remaining in the time window closest to quota exhaustion.

        :return: the remaining rate limit
        """
        return self.rate_limit_remaining

    def get_rate_limit_reset(self) -> int:
        """
        Gets the number of seconds until the quota resets for the time window closest to quota exhaustion.

        :return: the rate limit reset time
        """
        return self.rate_limit_reset

    def get_zuora_track_id(self) -> str:
        """
        Gets the custom identifier for tracing the API call. If you specified a tracing identifier in the request headers,
        Zuora returns the same tracing identifier. Otherwise, Zuora does not set this header.

        :return: the Zuora track ID
        """
        return self.zuora_track_id

    def get_concurrency_limit_type(self) -> str:
        """
        Gets the type of the concurrency limit, which can be either Default or High-volume transactions.

        :return: the concurrency limit type
        """
        return self.concurrency_limit_type

    def get_concurrency_limit_limit(self) -> int:
        """
        Gets the total number of the permitted concurrent requests.

        :return: the concurrency limit
        """
        return self.concurrency_limit_limit

    def get_concurrency_limit_remaining(self) -> int:
        """
        Gets the remaining number of the permitted concurrent requests.

        :return: the remaining concurrency limit
        """
        return self.concurrency_limit_remaining

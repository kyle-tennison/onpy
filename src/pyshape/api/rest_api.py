"""Rest Api interface to OnShape server"""

import json
from pprint import pprint
from pyshape.api.endpoints import EndpointContainer
from pyshape.api.model import ApiModel
from pyshape.util.model import HttpMethod
from pyshape.util.exceptions import PyshapeApiError, PyshapeInternalError

import requests
from requests.auth import HTTPBasicAuth
import inspect
from loguru import logger
from typing import TYPE_CHECKING, Callable

if TYPE_CHECKING:
    from pyshape.client import Client


class RestApi:
    """Interface for OnShape API Requests"""

    BASE_URL = "https://cad.onshape.com/api/v6"

    def __init__(self, client: "Client") -> None:
        self.endpoints = EndpointContainer(self)
        self.client = client

    def get_auth(self) -> HTTPBasicAuth:
        """Returns the authentication object"""

        access_key, secret_key = self.client._credentials
        return HTTPBasicAuth(access_key, secret_key)

    def http_wrap[
        T: ApiModel | dict
    ](
        self,
        http_method: HttpMethod,
        endpoint: str,
        expected_response: type[T],
        payload: ApiModel | None,
    ) -> T:
        """Wraps requests' POST/GET/DELETE with pydantic serializations & deserializations.

        Args:
            http_method: The HTTP Method to use, like GET/POST/DELETE.
            endpoint: The endpoint to target. e.g., /documents/
            expected_response: The ApiModel to deserialize the response into.
            payload: The optional payload to send with the request

        Returns:
            The response deserialized into the expected_response type
        """

        # match method enum to requests function
        requests_func: Callable[..., requests.Response] = {
            HttpMethod.Post: requests.post,
            HttpMethod.Get: requests.get,
            HttpMethod.Delete: requests.delete,
            HttpMethod.Put: requests.put,
        }[http_method]

        payload_json = None

        if isinstance(payload, ApiModel):
            payload_json = payload.model_dump()

        logger.debug(f"Calling {http_method.name} {endpoint} with payload:\n{json.dumps(payload_json, indent=4)}")

        # TODO: wrap this in a try/except to catch timeouts
        r = requests_func(
            url=self.BASE_URL + endpoint, json=payload_json, auth=self.get_auth()
        )

        if not r.ok:
            raise PyshapeApiError(f"Bad response {r.status_code}", r)

        # deserialize response
        try:
            response_dict = r.json()
        except requests.JSONDecodeError as e:
            raise PyshapeApiError("Response is not json", r)

        if issubclass(expected_response, ApiModel):
            return expected_response(**response_dict)

        elif issubclass(expected_response, dict):
            return response_dict

        else:
            raise PyshapeInternalError(
                f"Illegal response type: {expected_response.__name__}"
            )

    def post[
        T: ApiModel | dict
    ](self, endpoint: str, expected_response: type[T], payload: ApiModel) -> T:
        """Runs a POST request to the specified endpoint. Deserializes into expected_response type

        Args:
            endpoint: The endpoint to target. e.g., /documents/
            expected_response: The ApiModel to deserialize the response into.
            payload: The payload to send with the request

        Returns:
            The response deserialized into the expected_response type
        """

        return self.http_wrap(HttpMethod.Post, endpoint, expected_response, payload)

    def get[
        T: ApiModel | dict
    ](
        self, endpoint: str, expected_response: type[T], payload: ApiModel | None = None
    ) -> T:
        """Runs a GET request to the specified endpoint. Deserializes into expected_response type

        Args:
            endpoint: The endpoint to target. e.g., /documents/
            expected_response: The ApiModel to deserialize the response into.

        Returns:
            The response deserialized into the expected_response type
        """

        return self.http_wrap(HttpMethod.Get, endpoint, expected_response, payload)

    def put[
        T: ApiModel | dict
    ](self, endpoint: str, expected_response: type[T], payload: ApiModel) -> T:
        """Runs a PUT request to the specified endpoint. Deserializes into expected_response type

        Args:
            endpoint: The endpoint to target. e.g., /documents/
            expected_response: The ApiModel to deserialize the response into.
            payload: The payload to send with the request

        Returns:
            The response deserialized into the expected_response type
        """

        return self.http_wrap(HttpMethod.Put, endpoint, expected_response, payload)

    def delete[
        T: ApiModel | dict
    ](
        self, endpoint: str, expected_response: type[T], payload: ApiModel | None = None
    ) -> T:
        """Runs a DELETE request to the specified endpoint. Deserializes into expected_response type

        Args:
            endpoint: The endpoint to target. e.g., /documents/
            expected_response: The ApiModel to deserialize the response into.
            payload: The payload to send with the request

        Returns:
            The response deserialized into the expected_response type
        """

        return self.http_wrap(HttpMethod.Delete, endpoint, expected_response, payload)

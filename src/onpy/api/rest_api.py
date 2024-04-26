"""Rest Api interface to OnShape server"""

import json
import sys
from onpy.api.endpoints import EndpointContainer
from onpy.api.model import ApiModel
from onpy.util.model import HttpMethod
from onpy.util.exceptions import PyshapeApiError, PyshapeInternalError

import requests
from requests.auth import HTTPBasicAuth
import inspect
from loguru import logger
from typing import TYPE_CHECKING, Callable

if TYPE_CHECKING:
    from onpy.client import Client


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
        T: ApiModel | str
    ](
        self,
        http_method: HttpMethod,
        endpoint: str,
        response_type: type[T],
        payload: ApiModel | None,
    ) -> T:
        """Wraps requests' POST/GET/DELETE with pydantic serializations & deserializations.

        Args:
            http_method: The HTTP Method to use, like GET/POST/DELETE.
            endpoint: The endpoint to target. e.g., /documents/
            response_type: The ApiModel to deserialize the response into.
            payload: The optional payload to send with the request

        Returns:
            The response deserialized into the response_type type
        """

        # check endpoint formatting
        if not endpoint.startswith("/"):
            raise PyshapeInternalError(f"Endpoint '{endpoint}' missing '/' prefix")

        # match method enum to requests function
        requests_func: Callable[..., requests.Response] = {
            HttpMethod.Post: requests.post,
            HttpMethod.Get: requests.get,
            HttpMethod.Delete: requests.delete,
            HttpMethod.Put: requests.put,
        }[http_method]

        payload_json = None

        if isinstance(payload, ApiModel):
            payload_json = payload.model_dump(exclude_none=True)

        logger.debug(f"{http_method.name} {endpoint}")
        logger.trace(
            f"Calling {http_method.name} {endpoint}"
            + (
                f" with payload:\n{json.dumps(payload_json, indent=4)}"
                if payload
                else ""
            )
        )

        # TODO: wrap this in a try/except to catch timeouts
        r = requests_func(
            url=self.BASE_URL + endpoint, json=payload_json, auth=self.get_auth()
        )

        if not r.ok:
            raise PyshapeApiError(f"Bad response {r.status_code}", r)

        # deserialize response
        try:
            if r.text.strip() == "":
                response_dict: dict = {}  # allow empty responses
            else:
                response_dict = r.json()
            logger.trace(
                f"{http_method.name} {endpoint} responded with:\n"
                f"{json.dumps(response_dict, indent=4)}"
            )
        except requests.JSONDecodeError as e:
            raise PyshapeApiError("Response is not json", r)

        if issubclass(response_type, ApiModel):
            return response_type(**response_dict)

        elif issubclass(response_type, str):
            return response_type(r.text)

        else:
            raise PyshapeInternalError(
                f"Illegal response type: {response_type.__name__}"
            )

    def http_wrap_list[
        T: ApiModel | str
    ](
        self,
        http_method: HttpMethod,
        endpoint: str,
        response_type: type[T],
        payload: ApiModel | None,
    ) -> list[T]:
        """Interfaces with http_wrap to deserialize into a list of the expected class

        Args:
            http_method: The HTTP Method to use, like GET/POST/DELETE.
            endpoint: The endpoint to target. e.g., /documents/
            response_type: The ApiModel to deserialize the response into.
            payload: The optional payload to send with the request

        Returns:
            The response deserialized into the response_type type
        """

        response_raw = self.http_wrap(http_method, endpoint, str, payload)

        response_list = json.loads(response_raw)

        if not isinstance(response_list, list):
            raise PyshapeApiError(f"Endpoint {endpoint} expected list response")

        return [response_type(**i) for i in response_list]

    def post[
        T: ApiModel | str
    ](self, endpoint: str, response_type: type[T], payload: ApiModel) -> T:
        """Runs a POST request to the specified endpoint. Deserializes into response_type type

        Args:
            endpoint: The endpoint to target. e.g., /documents/
            response_type: The ApiModel to deserialize the response into.
            payload: The payload to send with the request

        Returns:
            The response deserialized into the response_type type
        """

        return self.http_wrap(HttpMethod.Post, endpoint, response_type, payload)

    def get[
        T: ApiModel | str
    ](
        self, endpoint: str, response_type: type[T], payload: ApiModel | None = None
    ) -> T:
        """Runs a GET request to the specified endpoint. Deserializes into response_type type

        Args:
            endpoint: The endpoint to target. e.g., /documents/
            response_type: The ApiModel to deserialize the response into.

        Returns:
            The response deserialized into the response_type type
        """

        return self.http_wrap(HttpMethod.Get, endpoint, response_type, payload)

    def put[
        T: ApiModel | str
    ](self, endpoint: str, response_type: type[T], payload: ApiModel) -> T:
        """Runs a PUT request to the specified endpoint. Deserializes into response_type type

        Args:
            endpoint: The endpoint to target. e.g., /documents/
            response_type: The ApiModel to deserialize the response into.
            payload: The payload to send with the request

        Returns:
            The response deserialized into the response_type type
        """

        return self.http_wrap(HttpMethod.Put, endpoint, response_type, payload)

    def delete[
        T: ApiModel | str
    ](
        self, endpoint: str, response_type: type[T], payload: ApiModel | None = None
    ) -> T:
        """Runs a DELETE request to the specified endpoint. Deserializes into response_type type

        Args:
            endpoint: The endpoint to target. e.g., /documents/
            response_type: The ApiModel to deserialize the response into.
            payload: The payload to send with the request

        Returns:
            The response deserialized into the response_type type
        """

        return self.http_wrap(HttpMethod.Delete, endpoint, response_type, payload)

    def list_post[
        T: ApiModel | str
    ](self, endpoint: str, response_type: type[T], payload: ApiModel) -> list[T]:
        """Runs a POST request to the specified endpoint. Deserializes into
        a list of the response_type type

        Args:
            endpoint: The endpoint to target. e.g., /documents/
            response_type: The ApiModel to deserialize the response into.
            payload: The payload to send with the request

        Returns:
            The response, deserialized into a list of the response_type type
        """

        return self.http_wrap_list(HttpMethod.Post, endpoint, response_type, payload)

    def list_get[
        T: ApiModel | str
    ](
        self, endpoint: str, response_type: type[T], payload: ApiModel | None = None
    ) -> list[T]:
        """Runs a GET request to the specified endpoint. Deserializes into
        a list of the response_type type

        Args:
            endpoint: The endpoint to target. e.g., /documents/
            response_type: The ApiModel to deserialize the response into.
            payload: The payload to send with the request

        Returns:
            The response, deserialized into a list of the response_type type
        """

        return self.http_wrap_list(HttpMethod.Get, endpoint, response_type, payload)

    def list_put[
        T: ApiModel | str
    ](self, endpoint: str, response_type: type[T], payload: ApiModel) -> list[T]:
        """Runs a PUT request to the specified endpoint. Deserializes into
        a list of the response_type type

        Args:
            endpoint: The endpoint to target. e.g., /documents/
            response_type: The ApiModel to deserialize the response into.
            payload: The payload to send with the request

        Returns:
            The response, deserialized into a list of the response_type type
        """

        return self.http_wrap_list(HttpMethod.Put, endpoint, response_type, payload)

    def list_delete[
        T: ApiModel | str
    ](
        self, endpoint: str, response_type: type[T], payload: ApiModel | None = None
    ) -> list[T]:
        """Runs a DELETE request to the specified endpoint. Deserializes into
        a list of the response_type type

        Args:
            endpoint: The endpoint to target. e.g., /documents/
            response_type: The ApiModel to deserialize the response into.
            payload: The payload to send with the request

        Returns:
            The response, deserialized into a list of the response_type type
        """

        return self.http_wrap_list(HttpMethod.Delete, endpoint, response_type, payload)

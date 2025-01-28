"""RestApi interface to the OnShape server.

The api is built in two parts; a request centric, utility part, and a part
dedicated to wrapping the many OnShape endpoints. This script is the utility
part; different HTTP request methods are implemented here, based around
the Python requests module.

OnPy - May 2024 - Kyle Tennison

"""

import json
from typing import TYPE_CHECKING, cast

import requests
from loguru import logger
from requests.auth import HTTPBasicAuth

from onpy.api.endpoints import EndpointContainer
from onpy.api.schema import ApiModel, HttpMethod
from onpy.util.exceptions import OnPyApiError, OnPyInternalError

if TYPE_CHECKING:
    from collections.abc import Callable

    from onpy.client import Client


class RestApi:
    """Interface for OnShape API Requests."""

    BASE_URL = "https://cad.onshape.com/api/v6"

    def __init__(self, client: "Client") -> None:
        """Construct a new rest api interface instance.

        Args:
            client: A reference to the client.

        """
        self.endpoints = EndpointContainer(self)
        self.client = client

    def get_auth(self) -> HTTPBasicAuth:
        """Get the basic HTTP the authentication object."""
        access_key, secret_key = self.client._credentials
        return HTTPBasicAuth(access_key, secret_key)

    def http_wrap[T: ApiModel | str](
        self,
        http_method: HttpMethod,
        endpoint: str,
        response_type: type[T],
        payload: ApiModel | None,
    ) -> T:
        """Wrap requests' POST/GET/DELETE with pydantic serializations & deserializations.

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
            msg = f"Endpoint '{endpoint}' missing '/' prefix"
            raise OnPyInternalError(msg)

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
            + (f" with payload:\n{json.dumps(payload_json, indent=4)}" if payload else ""),
        )

        # TODO @kyle-tennison: wrap this in a try/except to catch timeouts
        r = requests_func(
            url=self.BASE_URL + endpoint,
            json=payload_json,
            auth=self.get_auth(),
        )

        if not r.ok:
            msg = f"Bad response {r.status_code}"
            raise OnPyApiError(msg, r)

        # deserialize response
        try:
            if r.text.strip() == "":
                response_dict: dict = {}  # allow empty responses
            else:
                response_dict = r.json()
            logger.trace(
                f"{http_method.name} {endpoint} responded with:\n"
                f"{json.dumps(response_dict, indent=4)}",
            )
        except requests.JSONDecodeError as e:
            msg = "Response is not json"
            raise OnPyApiError(msg, r) from e

        if issubclass(response_type, ApiModel):
            return cast(T, response_type(**response_dict))

        if issubclass(response_type, str):
            return cast(T, response_type(r.text))

        msg = f"Illegal response type: {response_type.__name__}"
        raise OnPyInternalError(msg)

    def http_wrap_list[T: ApiModel | str](
        self,
        http_method: HttpMethod,
        endpoint: str,
        response_type: type[T],
        payload: ApiModel | None,
    ) -> list[T]:
        """Interfaces with http_wrap to deserialize into a list of the expected class.

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
            msg = f"Endpoint {endpoint} expected list response"
            raise OnPyApiError(msg)

        return [cast(T, response_type(**i)) for i in response_list]

    def post[T: ApiModel | str](
        self, endpoint: str, response_type: type[T], payload: ApiModel
    ) -> T:
        """Run a POST request to the specified endpoint. Deserializes into response_type type.

        Args:
            endpoint: The endpoint to target. e.g., /documents/
            response_type: The ApiModel to deserialize the response into.
            payload: The payload to send with the request

        Returns:
            The response deserialized into the response_type type

        """
        return self.http_wrap(HttpMethod.Post, endpoint, response_type, payload)

    def get[T: ApiModel | str](
        self,
        endpoint: str,
        response_type: type[T],
        payload: ApiModel | None = None,
    ) -> T:
        """Run a GET request to the specified endpoint. Deserializes into response_type type.

        Args:
            endpoint: The endpoint to target. e.g., /documents/
            response_type: The ApiModel to deserialize the response into.
            payload: The payload to include with the request, if applicable.

        Returns:
            The response deserialized into the response_type type

        """
        return self.http_wrap(HttpMethod.Get, endpoint, response_type, payload)

    def put[T: ApiModel | str](self, endpoint: str, response_type: type[T], payload: ApiModel) -> T:
        """Run a PUT request to the specified endpoint. Deserializes into response_type type.

        Args:
            endpoint: The endpoint to target. e.g., /documents/
            response_type: The ApiModel to deserialize the response into.
            payload: The payload to send with the request

        Returns:
            The response deserialized into the response_type type

        """
        return self.http_wrap(HttpMethod.Put, endpoint, response_type, payload)

    def delete[T: ApiModel | str](
        self,
        endpoint: str,
        response_type: type[T],
        payload: ApiModel | None = None,
    ) -> T:
        """Run a DELETE request to the specified endpoint. Deserializes into response_type type.

        Args:
            endpoint: The endpoint to target. e.g., /documents/
            response_type: The ApiModel to deserialize the response into.
            payload: The payload to send with the request

        Returns:
            The response deserialized into the response_type type

        """
        return self.http_wrap(HttpMethod.Delete, endpoint, response_type, payload)

    def list_post[T: ApiModel | str](
        self, endpoint: str, response_type: type[T], payload: ApiModel
    ) -> list[T]:
        """Run a POST request to the specified endpoint. Deserializes into
        a list of the response_type type.

        Args:
            endpoint: The endpoint to target. e.g., /documents/
            response_type: The ApiModel to deserialize the response into.
            payload: The payload to send with the request

        Returns:
            The response, deserialized into a list of the response_type type

        """
        return self.http_wrap_list(HttpMethod.Post, endpoint, response_type, payload)

    def list_get[T: ApiModel | str](
        self,
        endpoint: str,
        response_type: type[T],
        payload: ApiModel | None = None,
    ) -> list[T]:
        """Run a GET request to the specified endpoint. Deserializes into
        a list of the response_type type.

        Args:
            endpoint: The endpoint to target. e.g., /documents/
            response_type: The ApiModel to deserialize the response into.
            payload: The payload to send with the request

        Returns:
            The response, deserialized into a list of the response_type type

        """
        return self.http_wrap_list(HttpMethod.Get, endpoint, response_type, payload)

    def list_put[T: ApiModel | str](
        self, endpoint: str, response_type: type[T], payload: ApiModel
    ) -> list[T]:
        """Run a PUT request to the specified endpoint. Deserializes into
        a list of the response_type type.

        Args:
            endpoint: The endpoint to target. e.g., /documents/
            response_type: The ApiModel to deserialize the response into.
            payload: The payload to send with the request

        Returns:
            The response, deserialized into a list of the response_type type

        """
        return self.http_wrap_list(HttpMethod.Put, endpoint, response_type, payload)

    def list_delete[T: ApiModel | str](
        self,
        endpoint: str,
        response_type: type[T],
        payload: ApiModel | None = None,
    ) -> list[T]:
        """Run a DELETE request to the specified endpoint. Deserializes into
        a list of the response_type type.

        Args:
            endpoint: The endpoint to target. e.g., /documents/
            response_type: The ApiModel to deserialize the response into.
            payload: The payload to send with the request

        Returns:
            The response, deserialized into a list of the response_type type

        """
        return self.http_wrap_list(HttpMethod.Delete, endpoint, response_type, payload)

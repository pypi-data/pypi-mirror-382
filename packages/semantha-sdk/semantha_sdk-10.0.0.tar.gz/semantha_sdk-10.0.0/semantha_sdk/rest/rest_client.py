from __future__ import annotations

import json
import time
from enum import Enum
from io import BytesIO, IOBase
from typing import Any, Dict, Type
from abc import ABC, abstractmethod

from marshmallow import Schema, EXCLUDE
import requests
from requests import Response, Request, PreparedRequest, Session
from requests.structures import CaseInsensitiveDict
import humps


class RestSchema(Schema):
    # ignore unknown properties in json, we need this for older clients to access newer servers:
    class Meta:
        unknown = EXCLUDE
    def on_bind_field(self, field_name, field_obj):
        field_obj.data_key = humps.camelize(field_obj.data_key or field_name)

class RestEndpoint(ABC):
    _session: RestClient
    _parent_endpoint: str

    def __init__(self, session: RestClient, parent_endpoint: str):
        self._session = session
        self._parent_endpoint = parent_endpoint

    @property
    @abstractmethod
    def _endpoint(self):
        pass

class RestException(Exception):

    def __init__(self, *args):
        super().__init__(args)

class RestResponse:
    def __init__(self, response: Response) -> None:
        self.__raw_response = response
        self.__content = _check_and_translate_errors(self.__raw_response).content

    def get_status_code(self) -> int:
        return self.__raw_response.status_code

    # TODO: we should parse the Dict and return something more simple
    def get_headers(self) -> CaseInsensitiveDict[str]:
        return self.__raw_response.headers

    def content_is_empty(self) -> bool:
        return len(self.__content) == 0

    def as_dict(self) -> Dict:
        response_as_dict = json.loads(self.__content.decode())
        if type(response_as_dict) is dict:
            return response_as_dict
        else:
            raise ValueError(f"Response content could not be converted to type 'dict':\n{self.__str__()}")

    def as_dict_or_none(self):
        try:
            return self.as_dict()
        except ValueError:
            return None

    def as_list(self) -> list:
        response_as_list = json.loads(self.__content.decode())
        if type(response_as_list) is list:
            return response_as_list
        else:
            raise ValueError(f"Response content could not be converted to type 'list':\n{self.__str__()}")

    def as_list_or_none(self):
        try:
            return self.as_list()
        except ValueError:
            return None

    # TODO: type hint via interface
    def to(self, schema_type: Type[RestSchema]):
        schema = schema_type()

        as_dict = self.as_dict_or_none()
        as_list = self.as_list_or_none()

        if as_dict is None and as_list is None:
            raise ValueError("response was neither and object or a list")

        return schema.load(as_dict, unknown=EXCLUDE) if as_dict is not None else schema.load(as_list, many=True, unknown=EXCLUDE)

    def as_bytes(self) -> bytes:
        return self.__raw_response.content

    def as_str(self) -> str:
        return self.__content.decode()

    def as_none(self) -> None:
        return None

    def as_bytesio(self) -> BytesIO:
        return BytesIO(self.as_bytes())

    def __str__(self) -> str:
        return self.__raw_response.__str__()


def _check_and_translate_errors(response: Response) -> Response:
    if response.status_code in [200, 201, 204]:
        return response
    else:
        if response.status_code == 400:
            err = json.loads(response.text)
            if err.get('errors') and len(err.get('errors')) > 0:
                error = err.get('errors')[0]
                raise ValueError(error.get('code') + " " + error.get('title') + ": " + error.get('detail'))
            else:
                raise ValueError("Bad request: " + response.text)
        elif response.status_code == 401:
            raise PermissionError(response.status_code, "No permission to access: " + response.url)
        elif response.status_code == 404:
            raise FileNotFoundError(response.status_code, response.text + " url: " + response.url)
        elif response.status_code == 405:
            raise NotImplementedError(response.status_code, response.text)
        elif response.status_code == 408:
            raise TimeoutError(response.status_code, response.text)
        elif response.status_code == 500:
            raise RestException(response.status_code, response.text)
        # elif response.status_code == 503:
        #     raise BusyError(response.status_code, response.text)
        else:
            raise RuntimeError(response.status_code, response.text)

class RestRequest:

    def __init__(self, prepared_request: PreparedRequest, session):
        self.__prepared_request = prepared_request
        self.__session = session

    def execute(self) -> RestResponse:
        response = self.__session.send(self.__prepared_request)
        return RestResponse(response)

def _convert_value(value: Any):
    if isinstance(value, IOBase):
        return value

    if isinstance(value, Enum):
        return value.value

    if isinstance(value, bool):
        return str(value).lower()

    if isinstance(value, list):
        return "dontcare", json.dumps(value), MediaType.JSON

    return str(value)


def _filter_and_convert_to_str(data: dict, remove_empty_lists=False):
    data = {k: v for k, v in data.items() if v is not None}

    if remove_empty_lists:
        data = {k: v for k, v in data.items() if not (isinstance(v, list) and len(v) == 0)}

    data = {k: _convert_value(v) for k, v in data.items()}
    return data


def _filter_json(data: dict):
    data = {k: v for k, v in data.items() if v is not None}
    return data


class MediaType:
    XLSX = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    JSON = "application/json"
    PDF = "application/pdf"
    DOCX = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    ZIP = "application/zip"
    REQIFZ = "application/reqifz"
    PNG = "image/png"
    BINARY = "application/octet-stream"


class RestClient:
    __expire_time: float
    # in seconds
    LEEWAY = 30
    def __init__(self, server_url: str, api_key: str = None, client_id: str = None, client_secret: str = None,
                 token_url: str = None):
        self.__server_url = server_url
        self.__api_key = api_key
        self.__client_id = client_id
        self.__client_secret = client_secret
        self.__token_url = token_url
        self.__expire_time = 0.0
        self.__access_token = None
        self.__session = Session()

    def __build_headers_for_json_request(self) -> dict[str, str]:
        return {
            'Accept': 'application/json',
            'Authorization': f'Bearer {self.__get_token()}'
        }

    def __build_headers_for_request(self) -> dict[str, str]:
        return {
            'Authorization': f'Bearer {self.__get_token()}'
        }

    def __get_token(self):
        if self.__api_key:
            return self.__api_key
        if (self.__client_id and self.__client_secret and self.__token_url and
                (self.__access_token is None or self.__expire_time < time.monotonic())):
            headers = {'Accept': 'application/json'}
            data = {'grant_type': 'client_credentials', 'client_id': self.__client_id,
                    'client_secret': self.__client_secret, 'scope': 'openid'}
            r = requests.post(self.__token_url, headers=headers, data=data)
            if r.status_code >= requests.codes.bad_request:
                # example for error response: {"error":"invalid_client","error_description":"Invalid client or Invalid client credentials"}
                # we have no token -> this leads to a permission error
                return ""
            resp = r.json()
            # example response: {"access_token":"<TOKEN>","expires_in":300,"refresh_expires_in":0,"token_type":"Bearer","id_token":"<TOKEN>","not-before-policy":0,"scope":"openid profile email"}
            self.__access_token = resp['access_token'] if 'id_token' not in resp else resp['id_token']
            self.__expire_time = time.monotonic() + (resp['expires_in'] - RestClient.LEEWAY)
        return self.__access_token

    def __request(self,
                  method,
                  url,
                  headers=None,
                  files=None,
                  data=None,
                  params=None,
                  auth=None,
                  cookies=None,
                  hooks=None,
                  json: dict | list = None
                  ) -> RestRequest:
        if headers is None:
            headers = self.__build_headers_for_json_request()
        else:
            headers = {**headers, **self.__build_headers_for_request()}

        if json is not None and type(json) is dict:
            json = _filter_json(json)

        if files is not None:
            files = _filter_and_convert_to_str(files, remove_empty_lists=True)

        if params is not None:
            params = _filter_and_convert_to_str(params)

        headers['User-Agent'] = 'semantha Python SDK; '
        request = Request(
            method=method,
            url=self.__server_url + url,
            headers=headers,
            files=files,
            data=data,
            params=params,
            auth=auth,
            cookies=cookies,
            hooks=hooks,
            json=json
        )
        prepared_request = request.prepare()
        return RestRequest(prepared_request, self.__session)

    def get(self, url: str, q_params: dict[str, str] = None, headers: dict[str, str] = None) -> RestRequest:
        return self.__request("GET", url, params=q_params, headers=headers)

    def post(
            self,
            url: str,
            body: dict = None,
            json: dict | list = None,
            q_params: dict = None,
            headers: dict[str, str] = None,
    ) -> RestRequest:
        if body is None and json is None is None:
            raise ValueError("Either a body (files/form-data) or a json must be provided!")
        data = None
        if body is not None and len(body) == 1 and 'body' in body and isinstance(body['body'], IOBase):
            data = body['body']
            body = None
        return self.__request("POST", url, files=body, json=json, data=data, params=q_params, headers=headers)

    def delete(self, url: str, q_params: dict[str, str] = None, json: dict | list = None) -> RestRequest:
        return self.__request("DELETE", url, params=q_params, json=json)

    def patch(self, url: str, body: dict = None, json: dict | list = None,
              q_params: dict[str, str] = None) -> RestRequest:
        if body is None and json is None:
            raise ValueError("Either a body (files/form-data) or a json must be provided!")
        return self.__request("PATCH", url, files=body, json=json, params=q_params)

    def put(self, url: str, body: dict = None, json: dict | list = None,
            q_params: dict[str, str] = None) -> RestRequest:
        if body is None and json is None:
            raise ValueError("Either a body (files/form-data) or a json must be provided!")
        return self.__request("PUT", url, files=body, json=json, params=q_params)

    def to_header(accept_mime_type: str, content_type: str = None):
        if content_type:
            return {"Accept": accept_mime_type, "Content-Type": content_type}
        else:
            return {"Accept": accept_mime_type}

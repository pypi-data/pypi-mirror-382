# Copyright (c) 2021 AccelByte Inc. All Rights Reserved.
# This is licensed software from AccelByte Inc, for limitations
# and restrictions contact your company contract manager.
#
# Code generated. DO NOT EDIT!

# template file: operation.j2

# pylint: disable=duplicate-code
# pylint: disable=line-too-long
# pylint: disable=missing-function-docstring
# pylint: disable=missing-module-docstring
# pylint: disable=too-many-arguments
# pylint: disable=too-many-branches
# pylint: disable=too-many-instance-attributes
# pylint: disable=too-many-lines
# pylint: disable=too-many-locals
# pylint: disable=too-many-public-methods
# pylint: disable=too-many-return-statements
# pylint: disable=too-many-statements
# pylint: disable=unused-import

# AccelByte Gaming Services Chat Service

from __future__ import annotations
from typing import Any, Dict, List, Optional, Tuple, Union

from accelbyte_py_sdk.core import ApiError, ApiResponse
from accelbyte_py_sdk.core import Operation
from accelbyte_py_sdk.core import HeaderStr
from accelbyte_py_sdk.core import HttpResponse
from accelbyte_py_sdk.core import deprecated

from ...models import ModelsDictionaryQueryResult
from ...models import RestapiErrorResponseBody


class AdminProfanityQuery(Operation):
    """admin query profanity words (adminProfanityQuery)

    Query all profanity words.

    Properties:
        url: /chat/v1/admin/profanity/namespaces/{namespace}/dictionary

        method: GET

        tags: ["profanity"]

        consumes: ["application/json"]

        produces: ["application/json"]

        securities: [BEARER_AUTH]

        namespace: (namespace) REQUIRED str in path

        filter_mask: (filterMask) OPTIONAL str in query

        include_children: (includeChildren) OPTIONAL bool in query

        limit: (limit) OPTIONAL int in query

        offset: (offset) OPTIONAL int in query

        parent_id: (parentId) OPTIONAL str in query

        start_with: (startWith) OPTIONAL str in query

        word_type: (wordType) OPTIONAL str in query

    Responses:
        200: OK - ModelsDictionaryQueryResult (OK)

        400: Bad Request - RestapiErrorResponseBody (Bad Request)

        401: Unauthorized - RestapiErrorResponseBody (Unauthorized)

        403: Forbidden - RestapiErrorResponseBody (Forbidden)

        404: Not Found - RestapiErrorResponseBody (Not Found)

        500: Internal Server Error - RestapiErrorResponseBody (Internal Server Error)
    """

    # region fields

    _url: str = "/chat/v1/admin/profanity/namespaces/{namespace}/dictionary"
    _path: str = "/chat/v1/admin/profanity/namespaces/{namespace}/dictionary"
    _base_path: str = ""
    _method: str = "GET"
    _consumes: List[str] = ["application/json"]
    _produces: List[str] = ["application/json"]
    _securities: List[List[str]] = [["BEARER_AUTH"]]
    _location_query: str = None

    service_name: Optional[str] = "chat"

    namespace: str  # REQUIRED in [path]
    filter_mask: str  # OPTIONAL in [query]
    include_children: bool  # OPTIONAL in [query]
    limit: int  # OPTIONAL in [query]
    offset: int  # OPTIONAL in [query]
    parent_id: str  # OPTIONAL in [query]
    start_with: str  # OPTIONAL in [query]
    word_type: str  # OPTIONAL in [query]

    # endregion fields

    # region properties

    @property
    def url(self) -> str:
        return self._url

    @property
    def path(self) -> str:
        return self._path

    @property
    def base_path(self) -> str:
        return self._base_path

    @property
    def method(self) -> str:
        return self._method

    @property
    def consumes(self) -> List[str]:
        return self._consumes

    @property
    def produces(self) -> List[str]:
        return self._produces

    @property
    def securities(self) -> List[List[str]]:
        return self._securities

    @property
    def location_query(self) -> str:
        return self._location_query

    # endregion properties

    # region get methods

    # endregion get methods

    # region get_x_params methods

    def get_all_params(self) -> dict:
        return {
            "path": self.get_path_params(),
            "query": self.get_query_params(),
        }

    def get_path_params(self) -> dict:
        result = {}
        if hasattr(self, "namespace"):
            result["namespace"] = self.namespace
        return result

    def get_query_params(self) -> dict:
        result = {}
        if hasattr(self, "filter_mask"):
            result["filterMask"] = self.filter_mask
        if hasattr(self, "include_children"):
            result["includeChildren"] = self.include_children
        if hasattr(self, "limit"):
            result["limit"] = self.limit
        if hasattr(self, "offset"):
            result["offset"] = self.offset
        if hasattr(self, "parent_id"):
            result["parentId"] = self.parent_id
        if hasattr(self, "start_with"):
            result["startWith"] = self.start_with
        if hasattr(self, "word_type"):
            result["wordType"] = self.word_type
        return result

    # endregion get_x_params methods

    # region is/has methods

    # endregion is/has methods

    # region with_x methods

    def with_namespace(self, value: str) -> AdminProfanityQuery:
        self.namespace = value
        return self

    def with_filter_mask(self, value: str) -> AdminProfanityQuery:
        self.filter_mask = value
        return self

    def with_include_children(self, value: bool) -> AdminProfanityQuery:
        self.include_children = value
        return self

    def with_limit(self, value: int) -> AdminProfanityQuery:
        self.limit = value
        return self

    def with_offset(self, value: int) -> AdminProfanityQuery:
        self.offset = value
        return self

    def with_parent_id(self, value: str) -> AdminProfanityQuery:
        self.parent_id = value
        return self

    def with_start_with(self, value: str) -> AdminProfanityQuery:
        self.start_with = value
        return self

    def with_word_type(self, value: str) -> AdminProfanityQuery:
        self.word_type = value
        return self

    # endregion with_x methods

    # region to methods

    def to_dict(self, include_empty: bool = False) -> dict:
        result: dict = {}
        if hasattr(self, "namespace") and self.namespace:
            result["namespace"] = str(self.namespace)
        elif include_empty:
            result["namespace"] = ""
        if hasattr(self, "filter_mask") and self.filter_mask:
            result["filterMask"] = str(self.filter_mask)
        elif include_empty:
            result["filterMask"] = ""
        if hasattr(self, "include_children") and self.include_children:
            result["includeChildren"] = bool(self.include_children)
        elif include_empty:
            result["includeChildren"] = False
        if hasattr(self, "limit") and self.limit:
            result["limit"] = int(self.limit)
        elif include_empty:
            result["limit"] = 0
        if hasattr(self, "offset") and self.offset:
            result["offset"] = int(self.offset)
        elif include_empty:
            result["offset"] = 0
        if hasattr(self, "parent_id") and self.parent_id:
            result["parentId"] = str(self.parent_id)
        elif include_empty:
            result["parentId"] = ""
        if hasattr(self, "start_with") and self.start_with:
            result["startWith"] = str(self.start_with)
        elif include_empty:
            result["startWith"] = ""
        if hasattr(self, "word_type") and self.word_type:
            result["wordType"] = str(self.word_type)
        elif include_empty:
            result["wordType"] = ""
        return result

    # endregion to methods

    # region response methods

    class Response(ApiResponse):
        data_200: Optional[ModelsDictionaryQueryResult] = None
        error_400: Optional[RestapiErrorResponseBody] = None
        error_401: Optional[RestapiErrorResponseBody] = None
        error_403: Optional[RestapiErrorResponseBody] = None
        error_404: Optional[RestapiErrorResponseBody] = None
        error_500: Optional[RestapiErrorResponseBody] = None

        def ok(self) -> AdminProfanityQuery.Response:
            if self.error_400 is not None:
                err = self.error_400.translate_to_api_error()
                exc = err.to_exception()
                if exc is not None:
                    raise exc  # pylint: disable=raising-bad-type
            if self.error_401 is not None:
                err = self.error_401.translate_to_api_error()
                exc = err.to_exception()
                if exc is not None:
                    raise exc  # pylint: disable=raising-bad-type
            if self.error_403 is not None:
                err = self.error_403.translate_to_api_error()
                exc = err.to_exception()
                if exc is not None:
                    raise exc  # pylint: disable=raising-bad-type
            if self.error_404 is not None:
                err = self.error_404.translate_to_api_error()
                exc = err.to_exception()
                if exc is not None:
                    raise exc  # pylint: disable=raising-bad-type
            if self.error_500 is not None:
                err = self.error_500.translate_to_api_error()
                exc = err.to_exception()
                if exc is not None:
                    raise exc  # pylint: disable=raising-bad-type
            return self

        def __iter__(self):
            if self.data_200 is not None:
                yield self.data_200
                yield None
            elif self.error_400 is not None:
                yield None
                yield self.error_400
            elif self.error_401 is not None:
                yield None
                yield self.error_401
            elif self.error_403 is not None:
                yield None
                yield self.error_403
            elif self.error_404 is not None:
                yield None
                yield self.error_404
            elif self.error_500 is not None:
                yield None
                yield self.error_500
            else:
                yield None
                yield self.error

    # noinspection PyMethodMayBeStatic
    def parse_response(self, code: int, content_type: str, content: Any) -> Response:
        """Parse the given response.

        200: OK - ModelsDictionaryQueryResult (OK)

        400: Bad Request - RestapiErrorResponseBody (Bad Request)

        401: Unauthorized - RestapiErrorResponseBody (Unauthorized)

        403: Forbidden - RestapiErrorResponseBody (Forbidden)

        404: Not Found - RestapiErrorResponseBody (Not Found)

        500: Internal Server Error - RestapiErrorResponseBody (Internal Server Error)

        ---: HttpResponse (Undocumented Response)

        ---: HttpResponse (Unexpected Content-Type Error)

        ---: HttpResponse (Unhandled Error)
        """
        result = AdminProfanityQuery.Response()

        pre_processed_response, error = self.pre_process_response(
            code=code, content_type=content_type, content=content
        )

        if error is not None:
            if not error.is_no_content():
                result.error = ApiError.create_from_http_response(error)
        else:
            code, content_type, content = pre_processed_response

            if code == 200:
                result.data_200 = ModelsDictionaryQueryResult.create_from_dict(content)
            elif code == 400:
                result.error_400 = RestapiErrorResponseBody.create_from_dict(content)
                result.error = result.error_400.translate_to_api_error()
            elif code == 401:
                result.error_401 = RestapiErrorResponseBody.create_from_dict(content)
                result.error = result.error_401.translate_to_api_error()
            elif code == 403:
                result.error_403 = RestapiErrorResponseBody.create_from_dict(content)
                result.error = result.error_403.translate_to_api_error()
            elif code == 404:
                result.error_404 = RestapiErrorResponseBody.create_from_dict(content)
                result.error = result.error_404.translate_to_api_error()
            elif code == 500:
                result.error_500 = RestapiErrorResponseBody.create_from_dict(content)
                result.error = result.error_500.translate_to_api_error()
            else:
                result.error = ApiError.create_from_http_response(
                    HttpResponse.create_undocumented_response(
                        code=code, content_type=content_type, content=content
                    )
                )

        result.status_code = str(code)
        result.content_type = content_type

        if 400 <= code <= 599 or result.error is not None:
            result.is_success = False

        return result

    # noinspection PyMethodMayBeStatic
    @deprecated
    def parse_response_x(
        self, code: int, content_type: str, content: Any
    ) -> Tuple[
        Union[None, ModelsDictionaryQueryResult],
        Union[None, HttpResponse, RestapiErrorResponseBody],
    ]:
        """Parse the given response.

        200: OK - ModelsDictionaryQueryResult (OK)

        400: Bad Request - RestapiErrorResponseBody (Bad Request)

        401: Unauthorized - RestapiErrorResponseBody (Unauthorized)

        403: Forbidden - RestapiErrorResponseBody (Forbidden)

        404: Not Found - RestapiErrorResponseBody (Not Found)

        500: Internal Server Error - RestapiErrorResponseBody (Internal Server Error)

        ---: HttpResponse (Undocumented Response)

        ---: HttpResponse (Unexpected Content-Type Error)

        ---: HttpResponse (Unhandled Error)
        """
        pre_processed_response, error = self.pre_process_response(
            code=code, content_type=content_type, content=content
        )
        if error is not None:
            return None, None if error.is_no_content() else error
        code, content_type, content = pre_processed_response

        if code == 200:
            return ModelsDictionaryQueryResult.create_from_dict(content), None
        if code == 400:
            return None, RestapiErrorResponseBody.create_from_dict(content)
        if code == 401:
            return None, RestapiErrorResponseBody.create_from_dict(content)
        if code == 403:
            return None, RestapiErrorResponseBody.create_from_dict(content)
        if code == 404:
            return None, RestapiErrorResponseBody.create_from_dict(content)
        if code == 500:
            return None, RestapiErrorResponseBody.create_from_dict(content)

        return self.handle_undocumented_response(
            code=code, content_type=content_type, content=content
        )

    # endregion response methods

    # region static methods

    @classmethod
    def create(
        cls,
        namespace: str,
        filter_mask: Optional[str] = None,
        include_children: Optional[bool] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        parent_id: Optional[str] = None,
        start_with: Optional[str] = None,
        word_type: Optional[str] = None,
        **kwargs,
    ) -> AdminProfanityQuery:
        instance = cls()
        instance.namespace = namespace
        if filter_mask is not None:
            instance.filter_mask = filter_mask
        if include_children is not None:
            instance.include_children = include_children
        if limit is not None:
            instance.limit = limit
        if offset is not None:
            instance.offset = offset
        if parent_id is not None:
            instance.parent_id = parent_id
        if start_with is not None:
            instance.start_with = start_with
        if word_type is not None:
            instance.word_type = word_type
        if x_flight_id := kwargs.get("x_flight_id", None):
            instance.x_flight_id = x_flight_id
        return instance

    @classmethod
    def create_from_dict(
        cls, dict_: dict, include_empty: bool = False
    ) -> AdminProfanityQuery:
        instance = cls()
        if "namespace" in dict_ and dict_["namespace"] is not None:
            instance.namespace = str(dict_["namespace"])
        elif include_empty:
            instance.namespace = ""
        if "filterMask" in dict_ and dict_["filterMask"] is not None:
            instance.filter_mask = str(dict_["filterMask"])
        elif include_empty:
            instance.filter_mask = ""
        if "includeChildren" in dict_ and dict_["includeChildren"] is not None:
            instance.include_children = bool(dict_["includeChildren"])
        elif include_empty:
            instance.include_children = False
        if "limit" in dict_ and dict_["limit"] is not None:
            instance.limit = int(dict_["limit"])
        elif include_empty:
            instance.limit = 0
        if "offset" in dict_ and dict_["offset"] is not None:
            instance.offset = int(dict_["offset"])
        elif include_empty:
            instance.offset = 0
        if "parentId" in dict_ and dict_["parentId"] is not None:
            instance.parent_id = str(dict_["parentId"])
        elif include_empty:
            instance.parent_id = ""
        if "startWith" in dict_ and dict_["startWith"] is not None:
            instance.start_with = str(dict_["startWith"])
        elif include_empty:
            instance.start_with = ""
        if "wordType" in dict_ and dict_["wordType"] is not None:
            instance.word_type = str(dict_["wordType"])
        elif include_empty:
            instance.word_type = ""
        return instance

    @staticmethod
    def get_field_info() -> Dict[str, str]:
        return {
            "namespace": "namespace",
            "filterMask": "filter_mask",
            "includeChildren": "include_children",
            "limit": "limit",
            "offset": "offset",
            "parentId": "parent_id",
            "startWith": "start_with",
            "wordType": "word_type",
        }

    @staticmethod
    def get_required_map() -> Dict[str, bool]:
        return {
            "namespace": True,
            "filterMask": False,
            "includeChildren": False,
            "limit": False,
            "offset": False,
            "parentId": False,
            "startWith": False,
            "wordType": False,
        }

    # endregion static methods

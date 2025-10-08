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

from ...models import ModelsTopicLogWithPaginationResponse
from ...models import RestapiErrorResponseBody


class AdminQueryTopicLog(Operation):
    """admin query topic log (adminQueryTopicLog)

    Get chat log of topic in a namespace.

    Properties:
        url: /chat/admin/namespaces/{namespace}/topic/log

        method: GET

        tags: ["topic"]

        consumes: ["application/json"]

        produces: ["application/json"]

        securities: [BEARER_AUTH]

        namespace: (namespace) REQUIRED str in path

        end_created_at: (endCreatedAt) OPTIONAL int in query

        limit: (limit) OPTIONAL int in query

        offset: (offset) OPTIONAL int in query

        sender_user_id: (senderUserId) OPTIONAL str in query

        start_created_at: (startCreatedAt) OPTIONAL int in query

        topic_id: (topicId) OPTIONAL str in query

        topic_ids: (topicIds) OPTIONAL List[str] in query

        user_id: (userId) OPTIONAL str in query

    Responses:
        200: OK - ModelsTopicLogWithPaginationResponse (OK)

        400: Bad Request - RestapiErrorResponseBody (Bad Request)

        401: Unauthorized - RestapiErrorResponseBody (Unauthorized)

        403: Forbidden - RestapiErrorResponseBody (Forbidden)

        500: Internal Server Error - RestapiErrorResponseBody (Internal Server Error)
    """

    # region fields

    _url: str = "/chat/admin/namespaces/{namespace}/topic/log"
    _path: str = "/chat/admin/namespaces/{namespace}/topic/log"
    _base_path: str = ""
    _method: str = "GET"
    _consumes: List[str] = ["application/json"]
    _produces: List[str] = ["application/json"]
    _securities: List[List[str]] = [["BEARER_AUTH"]]
    _location_query: str = None

    service_name: Optional[str] = "chat"

    namespace: str  # REQUIRED in [path]
    end_created_at: int  # OPTIONAL in [query]
    limit: int  # OPTIONAL in [query]
    offset: int  # OPTIONAL in [query]
    sender_user_id: str  # OPTIONAL in [query]
    start_created_at: int  # OPTIONAL in [query]
    topic_id: str  # OPTIONAL in [query]
    topic_ids: List[str]  # OPTIONAL in [query]
    user_id: str  # OPTIONAL in [query]

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
        if hasattr(self, "end_created_at"):
            result["endCreatedAt"] = self.end_created_at
        if hasattr(self, "limit"):
            result["limit"] = self.limit
        if hasattr(self, "offset"):
            result["offset"] = self.offset
        if hasattr(self, "sender_user_id"):
            result["senderUserId"] = self.sender_user_id
        if hasattr(self, "start_created_at"):
            result["startCreatedAt"] = self.start_created_at
        if hasattr(self, "topic_id"):
            result["topicId"] = self.topic_id
        if hasattr(self, "topic_ids"):
            result["topicIds"] = self.topic_ids
        if hasattr(self, "user_id"):
            result["userId"] = self.user_id
        return result

    # endregion get_x_params methods

    # region is/has methods

    # endregion is/has methods

    # region with_x methods

    def with_namespace(self, value: str) -> AdminQueryTopicLog:
        self.namespace = value
        return self

    def with_end_created_at(self, value: int) -> AdminQueryTopicLog:
        self.end_created_at = value
        return self

    def with_limit(self, value: int) -> AdminQueryTopicLog:
        self.limit = value
        return self

    def with_offset(self, value: int) -> AdminQueryTopicLog:
        self.offset = value
        return self

    def with_sender_user_id(self, value: str) -> AdminQueryTopicLog:
        self.sender_user_id = value
        return self

    def with_start_created_at(self, value: int) -> AdminQueryTopicLog:
        self.start_created_at = value
        return self

    def with_topic_id(self, value: str) -> AdminQueryTopicLog:
        self.topic_id = value
        return self

    def with_topic_ids(self, value: List[str]) -> AdminQueryTopicLog:
        self.topic_ids = value
        return self

    def with_user_id(self, value: str) -> AdminQueryTopicLog:
        self.user_id = value
        return self

    # endregion with_x methods

    # region to methods

    def to_dict(self, include_empty: bool = False) -> dict:
        result: dict = {}
        if hasattr(self, "namespace") and self.namespace:
            result["namespace"] = str(self.namespace)
        elif include_empty:
            result["namespace"] = ""
        if hasattr(self, "end_created_at") and self.end_created_at:
            result["endCreatedAt"] = int(self.end_created_at)
        elif include_empty:
            result["endCreatedAt"] = 0
        if hasattr(self, "limit") and self.limit:
            result["limit"] = int(self.limit)
        elif include_empty:
            result["limit"] = 0
        if hasattr(self, "offset") and self.offset:
            result["offset"] = int(self.offset)
        elif include_empty:
            result["offset"] = 0
        if hasattr(self, "sender_user_id") and self.sender_user_id:
            result["senderUserId"] = str(self.sender_user_id)
        elif include_empty:
            result["senderUserId"] = ""
        if hasattr(self, "start_created_at") and self.start_created_at:
            result["startCreatedAt"] = int(self.start_created_at)
        elif include_empty:
            result["startCreatedAt"] = 0
        if hasattr(self, "topic_id") and self.topic_id:
            result["topicId"] = str(self.topic_id)
        elif include_empty:
            result["topicId"] = ""
        if hasattr(self, "topic_ids") and self.topic_ids:
            result["topicIds"] = [str(i0) for i0 in self.topic_ids]
        elif include_empty:
            result["topicIds"] = []
        if hasattr(self, "user_id") and self.user_id:
            result["userId"] = str(self.user_id)
        elif include_empty:
            result["userId"] = ""
        return result

    # endregion to methods

    # region response methods

    class Response(ApiResponse):
        data_200: Optional[ModelsTopicLogWithPaginationResponse] = None
        error_400: Optional[RestapiErrorResponseBody] = None
        error_401: Optional[RestapiErrorResponseBody] = None
        error_403: Optional[RestapiErrorResponseBody] = None
        error_500: Optional[RestapiErrorResponseBody] = None

        def ok(self) -> AdminQueryTopicLog.Response:
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
            elif self.error_500 is not None:
                yield None
                yield self.error_500
            else:
                yield None
                yield self.error

    # noinspection PyMethodMayBeStatic
    def parse_response(self, code: int, content_type: str, content: Any) -> Response:
        """Parse the given response.

        200: OK - ModelsTopicLogWithPaginationResponse (OK)

        400: Bad Request - RestapiErrorResponseBody (Bad Request)

        401: Unauthorized - RestapiErrorResponseBody (Unauthorized)

        403: Forbidden - RestapiErrorResponseBody (Forbidden)

        500: Internal Server Error - RestapiErrorResponseBody (Internal Server Error)

        ---: HttpResponse (Undocumented Response)

        ---: HttpResponse (Unexpected Content-Type Error)

        ---: HttpResponse (Unhandled Error)
        """
        result = AdminQueryTopicLog.Response()

        pre_processed_response, error = self.pre_process_response(
            code=code, content_type=content_type, content=content
        )

        if error is not None:
            if not error.is_no_content():
                result.error = ApiError.create_from_http_response(error)
        else:
            code, content_type, content = pre_processed_response

            if code == 200:
                result.data_200 = ModelsTopicLogWithPaginationResponse.create_from_dict(
                    content
                )
            elif code == 400:
                result.error_400 = RestapiErrorResponseBody.create_from_dict(content)
                result.error = result.error_400.translate_to_api_error()
            elif code == 401:
                result.error_401 = RestapiErrorResponseBody.create_from_dict(content)
                result.error = result.error_401.translate_to_api_error()
            elif code == 403:
                result.error_403 = RestapiErrorResponseBody.create_from_dict(content)
                result.error = result.error_403.translate_to_api_error()
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
        Union[None, ModelsTopicLogWithPaginationResponse],
        Union[None, HttpResponse, RestapiErrorResponseBody],
    ]:
        """Parse the given response.

        200: OK - ModelsTopicLogWithPaginationResponse (OK)

        400: Bad Request - RestapiErrorResponseBody (Bad Request)

        401: Unauthorized - RestapiErrorResponseBody (Unauthorized)

        403: Forbidden - RestapiErrorResponseBody (Forbidden)

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
            return ModelsTopicLogWithPaginationResponse.create_from_dict(content), None
        if code == 400:
            return None, RestapiErrorResponseBody.create_from_dict(content)
        if code == 401:
            return None, RestapiErrorResponseBody.create_from_dict(content)
        if code == 403:
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
        end_created_at: Optional[int] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        sender_user_id: Optional[str] = None,
        start_created_at: Optional[int] = None,
        topic_id: Optional[str] = None,
        topic_ids: Optional[List[str]] = None,
        user_id: Optional[str] = None,
        **kwargs,
    ) -> AdminQueryTopicLog:
        instance = cls()
        instance.namespace = namespace
        if end_created_at is not None:
            instance.end_created_at = end_created_at
        if limit is not None:
            instance.limit = limit
        if offset is not None:
            instance.offset = offset
        if sender_user_id is not None:
            instance.sender_user_id = sender_user_id
        if start_created_at is not None:
            instance.start_created_at = start_created_at
        if topic_id is not None:
            instance.topic_id = topic_id
        if topic_ids is not None:
            instance.topic_ids = topic_ids
        if user_id is not None:
            instance.user_id = user_id
        if x_flight_id := kwargs.get("x_flight_id", None):
            instance.x_flight_id = x_flight_id
        return instance

    @classmethod
    def create_from_dict(
        cls, dict_: dict, include_empty: bool = False
    ) -> AdminQueryTopicLog:
        instance = cls()
        if "namespace" in dict_ and dict_["namespace"] is not None:
            instance.namespace = str(dict_["namespace"])
        elif include_empty:
            instance.namespace = ""
        if "endCreatedAt" in dict_ and dict_["endCreatedAt"] is not None:
            instance.end_created_at = int(dict_["endCreatedAt"])
        elif include_empty:
            instance.end_created_at = 0
        if "limit" in dict_ and dict_["limit"] is not None:
            instance.limit = int(dict_["limit"])
        elif include_empty:
            instance.limit = 0
        if "offset" in dict_ and dict_["offset"] is not None:
            instance.offset = int(dict_["offset"])
        elif include_empty:
            instance.offset = 0
        if "senderUserId" in dict_ and dict_["senderUserId"] is not None:
            instance.sender_user_id = str(dict_["senderUserId"])
        elif include_empty:
            instance.sender_user_id = ""
        if "startCreatedAt" in dict_ and dict_["startCreatedAt"] is not None:
            instance.start_created_at = int(dict_["startCreatedAt"])
        elif include_empty:
            instance.start_created_at = 0
        if "topicId" in dict_ and dict_["topicId"] is not None:
            instance.topic_id = str(dict_["topicId"])
        elif include_empty:
            instance.topic_id = ""
        if "topicIds" in dict_ and dict_["topicIds"] is not None:
            instance.topic_ids = [str(i0) for i0 in dict_["topicIds"]]
        elif include_empty:
            instance.topic_ids = []
        if "userId" in dict_ and dict_["userId"] is not None:
            instance.user_id = str(dict_["userId"])
        elif include_empty:
            instance.user_id = ""
        return instance

    @staticmethod
    def get_field_info() -> Dict[str, str]:
        return {
            "namespace": "namespace",
            "endCreatedAt": "end_created_at",
            "limit": "limit",
            "offset": "offset",
            "senderUserId": "sender_user_id",
            "startCreatedAt": "start_created_at",
            "topicId": "topic_id",
            "topicIds": "topic_ids",
            "userId": "user_id",
        }

    @staticmethod
    def get_required_map() -> Dict[str, bool]:
        return {
            "namespace": True,
            "endCreatedAt": False,
            "limit": False,
            "offset": False,
            "senderUserId": False,
            "startCreatedAt": False,
            "topicId": False,
            "topicIds": False,
            "userId": False,
        }

    @staticmethod
    def get_collection_format_map() -> Dict[str, Union[None, str]]:
        return {
            "topicIds": "multi",  # in query
        }

    # endregion static methods

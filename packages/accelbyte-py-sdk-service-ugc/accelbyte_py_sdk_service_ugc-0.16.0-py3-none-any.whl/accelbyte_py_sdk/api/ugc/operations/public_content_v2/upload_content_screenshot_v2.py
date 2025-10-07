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

# AccelByte Gaming Services Ugc Service

from __future__ import annotations
from typing import Any, Dict, List, Optional, Tuple, Union

from accelbyte_py_sdk.core import ApiError, ApiResponse
from accelbyte_py_sdk.core import Operation
from accelbyte_py_sdk.core import HeaderStr
from accelbyte_py_sdk.core import HttpResponse
from accelbyte_py_sdk.core import deprecated

from ...models import ModelsCreateScreenshotRequest
from ...models import ModelsCreateScreenshotResponse
from ...models import ResponseError


class UploadContentScreenshotV2(Operation):
    """Upload screenshots for content (UploadContentScreenshotV2)

    This endpoint used to request upload URL from content's screenshot.
    If *contentType* is not specified, it will use *fileExtension* value.
    Supported file extensions: pjp, jpg, jpeg, jfif, bmp, png.
    Maximum description length: 1024

    Properties:
        url: /ugc/v2/public/namespaces/{namespace}/users/{userId}/contents/{contentId}/screenshots

        method: POST

        tags: ["Public Content V2"]

        consumes: ["application/json", "application/octet-stream"]

        produces: ["application/json"]

        securities: [BEARER_AUTH]

        body: (body) REQUIRED ModelsCreateScreenshotRequest in body

        content_id: (contentId) REQUIRED str in path

        namespace: (namespace) REQUIRED str in path

        user_id: (userId) REQUIRED str in path

    Responses:
        201: Created - ModelsCreateScreenshotResponse (Screenshot uploaded)

        400: Bad Request - ResponseError (772601: Malformed request)

        401: Unauthorized - ResponseError (20001: unauthorized access)

        403: Forbidden - ResponseError (772604: User has been banned to update content)

        500: Internal Server Error - ResponseError (772602: Unable to check user ban status/Unable to get updated ugc content | 772605: Unable to save ugc content: failed generate upload URL)
    """

    # region fields

    _url: str = "/ugc/v2/public/namespaces/{namespace}/users/{userId}/contents/{contentId}/screenshots"
    _path: str = "/ugc/v2/public/namespaces/{namespace}/users/{userId}/contents/{contentId}/screenshots"
    _base_path: str = ""
    _method: str = "POST"
    _consumes: List[str] = ["application/json", "application/octet-stream"]
    _produces: List[str] = ["application/json"]
    _securities: List[List[str]] = [["BEARER_AUTH"]]
    _location_query: str = None

    service_name: Optional[str] = "ugc"

    body: ModelsCreateScreenshotRequest  # REQUIRED in [body]
    content_id: str  # REQUIRED in [path]
    namespace: str  # REQUIRED in [path]
    user_id: str  # REQUIRED in [path]

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
            "body": self.get_body_params(),
            "path": self.get_path_params(),
        }

    def get_body_params(self) -> Any:
        if not hasattr(self, "body") or self.body is None:
            return None
        return self.body.to_dict()

    def get_path_params(self) -> dict:
        result = {}
        if hasattr(self, "content_id"):
            result["contentId"] = self.content_id
        if hasattr(self, "namespace"):
            result["namespace"] = self.namespace
        if hasattr(self, "user_id"):
            result["userId"] = self.user_id
        return result

    # endregion get_x_params methods

    # region is/has methods

    # endregion is/has methods

    # region with_x methods

    def with_body(
        self, value: ModelsCreateScreenshotRequest
    ) -> UploadContentScreenshotV2:
        self.body = value
        return self

    def with_content_id(self, value: str) -> UploadContentScreenshotV2:
        self.content_id = value
        return self

    def with_namespace(self, value: str) -> UploadContentScreenshotV2:
        self.namespace = value
        return self

    def with_user_id(self, value: str) -> UploadContentScreenshotV2:
        self.user_id = value
        return self

    # endregion with_x methods

    # region to methods

    def to_dict(self, include_empty: bool = False) -> dict:
        result: dict = {}
        if hasattr(self, "body") and self.body:
            result["body"] = self.body.to_dict(include_empty=include_empty)
        elif include_empty:
            result["body"] = ModelsCreateScreenshotRequest()
        if hasattr(self, "content_id") and self.content_id:
            result["contentId"] = str(self.content_id)
        elif include_empty:
            result["contentId"] = ""
        if hasattr(self, "namespace") and self.namespace:
            result["namespace"] = str(self.namespace)
        elif include_empty:
            result["namespace"] = ""
        if hasattr(self, "user_id") and self.user_id:
            result["userId"] = str(self.user_id)
        elif include_empty:
            result["userId"] = ""
        return result

    # endregion to methods

    # region response methods

    class Response(ApiResponse):
        data_201: Optional[ModelsCreateScreenshotResponse] = None
        error_400: Optional[ResponseError] = None
        error_401: Optional[ResponseError] = None
        error_403: Optional[ResponseError] = None
        error_500: Optional[ResponseError] = None

        def ok(self) -> UploadContentScreenshotV2.Response:
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
            if self.data_201 is not None:
                yield self.data_201
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

        201: Created - ModelsCreateScreenshotResponse (Screenshot uploaded)

        400: Bad Request - ResponseError (772601: Malformed request)

        401: Unauthorized - ResponseError (20001: unauthorized access)

        403: Forbidden - ResponseError (772604: User has been banned to update content)

        500: Internal Server Error - ResponseError (772602: Unable to check user ban status/Unable to get updated ugc content | 772605: Unable to save ugc content: failed generate upload URL)

        ---: HttpResponse (Undocumented Response)

        ---: HttpResponse (Unexpected Content-Type Error)

        ---: HttpResponse (Unhandled Error)
        """
        result = UploadContentScreenshotV2.Response()

        pre_processed_response, error = self.pre_process_response(
            code=code, content_type=content_type, content=content
        )

        if error is not None:
            if not error.is_no_content():
                result.error = ApiError.create_from_http_response(error)
        else:
            code, content_type, content = pre_processed_response

            if code == 201:
                result.data_201 = ModelsCreateScreenshotResponse.create_from_dict(
                    content
                )
            elif code == 400:
                result.error_400 = ResponseError.create_from_dict(content)
                result.error = result.error_400.translate_to_api_error()
            elif code == 401:
                result.error_401 = ResponseError.create_from_dict(content)
                result.error = result.error_401.translate_to_api_error()
            elif code == 403:
                result.error_403 = ResponseError.create_from_dict(content)
                result.error = result.error_403.translate_to_api_error()
            elif code == 500:
                result.error_500 = ResponseError.create_from_dict(content)
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
        Union[None, ModelsCreateScreenshotResponse],
        Union[None, HttpResponse, ResponseError],
    ]:
        """Parse the given response.

        201: Created - ModelsCreateScreenshotResponse (Screenshot uploaded)

        400: Bad Request - ResponseError (772601: Malformed request)

        401: Unauthorized - ResponseError (20001: unauthorized access)

        403: Forbidden - ResponseError (772604: User has been banned to update content)

        500: Internal Server Error - ResponseError (772602: Unable to check user ban status/Unable to get updated ugc content | 772605: Unable to save ugc content: failed generate upload URL)

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

        if code == 201:
            return ModelsCreateScreenshotResponse.create_from_dict(content), None
        if code == 400:
            return None, ResponseError.create_from_dict(content)
        if code == 401:
            return None, ResponseError.create_from_dict(content)
        if code == 403:
            return None, ResponseError.create_from_dict(content)
        if code == 500:
            return None, ResponseError.create_from_dict(content)

        return self.handle_undocumented_response(
            code=code, content_type=content_type, content=content
        )

    # endregion response methods

    # region static methods

    @classmethod
    def create(
        cls,
        body: ModelsCreateScreenshotRequest,
        content_id: str,
        namespace: str,
        user_id: str,
        **kwargs,
    ) -> UploadContentScreenshotV2:
        instance = cls()
        instance.body = body
        instance.content_id = content_id
        instance.namespace = namespace
        instance.user_id = user_id
        if x_flight_id := kwargs.get("x_flight_id", None):
            instance.x_flight_id = x_flight_id
        return instance

    @classmethod
    def create_from_dict(
        cls, dict_: dict, include_empty: bool = False
    ) -> UploadContentScreenshotV2:
        instance = cls()
        if "body" in dict_ and dict_["body"] is not None:
            instance.body = ModelsCreateScreenshotRequest.create_from_dict(
                dict_["body"], include_empty=include_empty
            )
        elif include_empty:
            instance.body = ModelsCreateScreenshotRequest()
        if "contentId" in dict_ and dict_["contentId"] is not None:
            instance.content_id = str(dict_["contentId"])
        elif include_empty:
            instance.content_id = ""
        if "namespace" in dict_ and dict_["namespace"] is not None:
            instance.namespace = str(dict_["namespace"])
        elif include_empty:
            instance.namespace = ""
        if "userId" in dict_ and dict_["userId"] is not None:
            instance.user_id = str(dict_["userId"])
        elif include_empty:
            instance.user_id = ""
        return instance

    @staticmethod
    def get_field_info() -> Dict[str, str]:
        return {
            "body": "body",
            "contentId": "content_id",
            "namespace": "namespace",
            "userId": "user_id",
        }

    @staticmethod
    def get_required_map() -> Dict[str, bool]:
        return {
            "body": True,
            "contentId": True,
            "namespace": True,
            "userId": True,
        }

    # endregion static methods

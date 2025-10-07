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

# AccelByte Gaming Services Statistics Service

from __future__ import annotations
from typing import Any, Dict, List, Optional, Tuple, Union

from accelbyte_py_sdk.core import ApiError, ApiResponse
from accelbyte_py_sdk.core import Operation
from accelbyte_py_sdk.core import HeaderStr
from accelbyte_py_sdk.core import HttpResponse
from accelbyte_py_sdk.core import deprecated

from ...models import Attribute
from ...models import ErrorEntity


class PublicGetProfileAttribute(Operation):
    """[DEPRECATED] Returns game profile attribute (publicGetProfileAttribute)

    ## The endpoint is going to be deprecated


    Returns game profile attribute.
    Other detail info:
            *  Returns : attribute info

    Properties:
        url: /social/public/namespaces/{namespace}/users/{userId}/profiles/{profileId}/attributes/{attributeName}

        method: GET

        tags: ["GameProfile"]

        consumes: []

        produces: ["application/json"]

        securities: [BEARER_AUTH]

        attribute_name: (attributeName) REQUIRED str in path

        namespace: (namespace) REQUIRED str in path

        profile_id: (profileId) REQUIRED str in path

        user_id: (userId) REQUIRED str in path

    Responses:
        200: OK - Attribute (successful operation)

        401: Unauthorized - ErrorEntity (20001: Unauthorized)

        403: Forbidden - ErrorEntity (20013: insufficient permission)

        404: Not Found - ErrorEntity (12041: Game profile with id [{profileId}] is not found)

        500: Internal Server Error - ErrorEntity (20000: Internal server error)
    """

    # region fields

    _url: str = "/social/public/namespaces/{namespace}/users/{userId}/profiles/{profileId}/attributes/{attributeName}"
    _path: str = "/social/public/namespaces/{namespace}/users/{userId}/profiles/{profileId}/attributes/{attributeName}"
    _base_path: str = ""
    _method: str = "GET"
    _consumes: List[str] = []
    _produces: List[str] = ["application/json"]
    _securities: List[List[str]] = [["BEARER_AUTH"]]
    _location_query: str = None

    service_name: Optional[str] = "social"

    attribute_name: str  # REQUIRED in [path]
    namespace: str  # REQUIRED in [path]
    profile_id: str  # REQUIRED in [path]
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
            "path": self.get_path_params(),
        }

    def get_path_params(self) -> dict:
        result = {}
        if hasattr(self, "attribute_name"):
            result["attributeName"] = self.attribute_name
        if hasattr(self, "namespace"):
            result["namespace"] = self.namespace
        if hasattr(self, "profile_id"):
            result["profileId"] = self.profile_id
        if hasattr(self, "user_id"):
            result["userId"] = self.user_id
        return result

    # endregion get_x_params methods

    # region is/has methods

    # endregion is/has methods

    # region with_x methods

    def with_attribute_name(self, value: str) -> PublicGetProfileAttribute:
        self.attribute_name = value
        return self

    def with_namespace(self, value: str) -> PublicGetProfileAttribute:
        self.namespace = value
        return self

    def with_profile_id(self, value: str) -> PublicGetProfileAttribute:
        self.profile_id = value
        return self

    def with_user_id(self, value: str) -> PublicGetProfileAttribute:
        self.user_id = value
        return self

    # endregion with_x methods

    # region to methods

    def to_dict(self, include_empty: bool = False) -> dict:
        result: dict = {}
        if hasattr(self, "attribute_name") and self.attribute_name:
            result["attributeName"] = str(self.attribute_name)
        elif include_empty:
            result["attributeName"] = ""
        if hasattr(self, "namespace") and self.namespace:
            result["namespace"] = str(self.namespace)
        elif include_empty:
            result["namespace"] = ""
        if hasattr(self, "profile_id") and self.profile_id:
            result["profileId"] = str(self.profile_id)
        elif include_empty:
            result["profileId"] = ""
        if hasattr(self, "user_id") and self.user_id:
            result["userId"] = str(self.user_id)
        elif include_empty:
            result["userId"] = ""
        return result

    # endregion to methods

    # region response methods

    class Response(ApiResponse):
        data_200: Optional[Attribute] = None
        error_401: Optional[ErrorEntity] = None
        error_403: Optional[ErrorEntity] = None
        error_404: Optional[ErrorEntity] = None
        error_500: Optional[ErrorEntity] = None

        def ok(self) -> PublicGetProfileAttribute.Response:
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

        200: OK - Attribute (successful operation)

        401: Unauthorized - ErrorEntity (20001: Unauthorized)

        403: Forbidden - ErrorEntity (20013: insufficient permission)

        404: Not Found - ErrorEntity (12041: Game profile with id [{profileId}] is not found)

        500: Internal Server Error - ErrorEntity (20000: Internal server error)

        ---: HttpResponse (Undocumented Response)

        ---: HttpResponse (Unexpected Content-Type Error)

        ---: HttpResponse (Unhandled Error)
        """
        result = PublicGetProfileAttribute.Response()

        pre_processed_response, error = self.pre_process_response(
            code=code, content_type=content_type, content=content
        )

        if error is not None:
            if not error.is_no_content():
                result.error = ApiError.create_from_http_response(error)
        else:
            code, content_type, content = pre_processed_response

            if code == 200:
                result.data_200 = Attribute.create_from_dict(content)
            elif code == 401:
                result.error_401 = ErrorEntity.create_from_dict(content)
                result.error = result.error_401.translate_to_api_error()
            elif code == 403:
                result.error_403 = ErrorEntity.create_from_dict(content)
                result.error = result.error_403.translate_to_api_error()
            elif code == 404:
                result.error_404 = ErrorEntity.create_from_dict(content)
                result.error = result.error_404.translate_to_api_error()
            elif code == 500:
                result.error_500 = ErrorEntity.create_from_dict(content)
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
    ) -> Tuple[Union[None, Attribute], Union[None, ErrorEntity, HttpResponse]]:
        """Parse the given response.

        200: OK - Attribute (successful operation)

        401: Unauthorized - ErrorEntity (20001: Unauthorized)

        403: Forbidden - ErrorEntity (20013: insufficient permission)

        404: Not Found - ErrorEntity (12041: Game profile with id [{profileId}] is not found)

        500: Internal Server Error - ErrorEntity (20000: Internal server error)

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
            return Attribute.create_from_dict(content), None
        if code == 401:
            return None, ErrorEntity.create_from_dict(content)
        if code == 403:
            return None, ErrorEntity.create_from_dict(content)
        if code == 404:
            return None, ErrorEntity.create_from_dict(content)
        if code == 500:
            return None, ErrorEntity.create_from_dict(content)

        return self.handle_undocumented_response(
            code=code, content_type=content_type, content=content
        )

    # endregion response methods

    # region static methods

    @classmethod
    def create(
        cls,
        attribute_name: str,
        namespace: str,
        profile_id: str,
        user_id: str,
        **kwargs,
    ) -> PublicGetProfileAttribute:
        instance = cls()
        instance.attribute_name = attribute_name
        instance.namespace = namespace
        instance.profile_id = profile_id
        instance.user_id = user_id
        if x_flight_id := kwargs.get("x_flight_id", None):
            instance.x_flight_id = x_flight_id
        return instance

    @classmethod
    def create_from_dict(
        cls, dict_: dict, include_empty: bool = False
    ) -> PublicGetProfileAttribute:
        instance = cls()
        if "attributeName" in dict_ and dict_["attributeName"] is not None:
            instance.attribute_name = str(dict_["attributeName"])
        elif include_empty:
            instance.attribute_name = ""
        if "namespace" in dict_ and dict_["namespace"] is not None:
            instance.namespace = str(dict_["namespace"])
        elif include_empty:
            instance.namespace = ""
        if "profileId" in dict_ and dict_["profileId"] is not None:
            instance.profile_id = str(dict_["profileId"])
        elif include_empty:
            instance.profile_id = ""
        if "userId" in dict_ and dict_["userId"] is not None:
            instance.user_id = str(dict_["userId"])
        elif include_empty:
            instance.user_id = ""
        return instance

    @staticmethod
    def get_field_info() -> Dict[str, str]:
        return {
            "attributeName": "attribute_name",
            "namespace": "namespace",
            "profileId": "profile_id",
            "userId": "user_id",
        }

    @staticmethod
    def get_required_map() -> Dict[str, bool]:
        return {
            "attributeName": True,
            "namespace": True,
            "profileId": True,
            "userId": True,
        }

    # endregion static methods

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

# AccelByte Gaming Services Legal Service

from __future__ import annotations
from typing import Any, Dict, List, Optional, Tuple, Union

from accelbyte_py_sdk.core import ApiError, ApiResponse
from accelbyte_py_sdk.core import Operation
from accelbyte_py_sdk.core import HeaderStr
from accelbyte_py_sdk.core import HttpResponse
from accelbyte_py_sdk.core import deprecated

from ...models import ErrorEntity


class PublishPolicyVersion1(Operation):
    """Manually Publish a Version from Country-Specific Policy (publishPolicyVersion_1)

    Manually publish a version of a particular country-specific policy.

    Properties:
        url: /agreement/admin/namespaces/{namespace}/policies/versions/{policyVersionId}/latest

        method: PATCH

        tags: ["Policy Versions With Namespace"]

        consumes: []

        produces: ["application/json"]

        securities: [BEARER_AUTH]

        namespace: (namespace) REQUIRED str in path

        policy_version_id: (policyVersionId) REQUIRED str in path

        should_notify: (shouldNotify) OPTIONAL bool in query

    Responses:
        200: OK - (operation successful)

        400: Bad Request - ErrorEntity (40035: errors.net.accelbyte.platform.legal.invalid_policy_version | 40046: errors.net.accelbyte.platform.legal.default_selection_not_provided | 40030: errors.net.accelbyte.platform.legal.localized_policy_version_not_provided)

        409: Conflict - ErrorEntity (40039: errors.net.accelbyte.platform.legal.localized_policy_version_already_latest | 40043: errors.net.accelbyte.platform.legal.localized_policy_version_already_publish)
    """

    # region fields

    _url: str = "/agreement/admin/namespaces/{namespace}/policies/versions/{policyVersionId}/latest"
    _path: str = "/agreement/admin/namespaces/{namespace}/policies/versions/{policyVersionId}/latest"
    _base_path: str = ""
    _method: str = "PATCH"
    _consumes: List[str] = []
    _produces: List[str] = ["application/json"]
    _securities: List[List[str]] = [["BEARER_AUTH"]]
    _location_query: str = None

    service_name: Optional[str] = "legal"

    namespace: str  # REQUIRED in [path]
    policy_version_id: str  # REQUIRED in [path]
    should_notify: bool  # OPTIONAL in [query]

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
        if hasattr(self, "policy_version_id"):
            result["policyVersionId"] = self.policy_version_id
        return result

    def get_query_params(self) -> dict:
        result = {}
        if hasattr(self, "should_notify"):
            result["shouldNotify"] = self.should_notify
        return result

    # endregion get_x_params methods

    # region is/has methods

    # endregion is/has methods

    # region with_x methods

    def with_namespace(self, value: str) -> PublishPolicyVersion1:
        self.namespace = value
        return self

    def with_policy_version_id(self, value: str) -> PublishPolicyVersion1:
        self.policy_version_id = value
        return self

    def with_should_notify(self, value: bool) -> PublishPolicyVersion1:
        self.should_notify = value
        return self

    # endregion with_x methods

    # region to methods

    def to_dict(self, include_empty: bool = False) -> dict:
        result: dict = {}
        if hasattr(self, "namespace") and self.namespace:
            result["namespace"] = str(self.namespace)
        elif include_empty:
            result["namespace"] = ""
        if hasattr(self, "policy_version_id") and self.policy_version_id:
            result["policyVersionId"] = str(self.policy_version_id)
        elif include_empty:
            result["policyVersionId"] = ""
        if hasattr(self, "should_notify") and self.should_notify:
            result["shouldNotify"] = bool(self.should_notify)
        elif include_empty:
            result["shouldNotify"] = False
        return result

    # endregion to methods

    # region response methods

    class Response(ApiResponse):
        data_200: Optional[HttpResponse] = None
        error_400: Optional[ErrorEntity] = None
        error_409: Optional[ErrorEntity] = None

        def ok(self) -> PublishPolicyVersion1.Response:
            if self.error_400 is not None:
                err = self.error_400.translate_to_api_error()
                exc = err.to_exception()
                if exc is not None:
                    raise exc  # pylint: disable=raising-bad-type
            if self.error_409 is not None:
                err = self.error_409.translate_to_api_error()
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
            elif self.error_409 is not None:
                yield None
                yield self.error_409
            else:
                yield None
                yield self.error

    # noinspection PyMethodMayBeStatic
    def parse_response(self, code: int, content_type: str, content: Any) -> Response:
        """Parse the given response.

        200: OK - (operation successful)

        400: Bad Request - ErrorEntity (40035: errors.net.accelbyte.platform.legal.invalid_policy_version | 40046: errors.net.accelbyte.platform.legal.default_selection_not_provided | 40030: errors.net.accelbyte.platform.legal.localized_policy_version_not_provided)

        409: Conflict - ErrorEntity (40039: errors.net.accelbyte.platform.legal.localized_policy_version_already_latest | 40043: errors.net.accelbyte.platform.legal.localized_policy_version_already_publish)

        ---: HttpResponse (Undocumented Response)

        ---: HttpResponse (Unexpected Content-Type Error)

        ---: HttpResponse (Unhandled Error)
        """
        result = PublishPolicyVersion1.Response()

        pre_processed_response, error = self.pre_process_response(
            code=code, content_type=content_type, content=content
        )

        if error is not None:
            if not error.is_no_content():
                result.error = ApiError.create_from_http_response(error)
        else:
            code, content_type, content = pre_processed_response

            if code == 200:
                result.data_200 = HttpResponse.create(code, content)
            elif code == 400:
                result.error_400 = ErrorEntity.create_from_dict(content)
                result.error = result.error_400.translate_to_api_error()
            elif code == 409:
                result.error_409 = ErrorEntity.create_from_dict(content)
                result.error = result.error_409.translate_to_api_error()
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
    ) -> Tuple[Union[None, HttpResponse], Union[None, ErrorEntity, HttpResponse]]:
        """Parse the given response.

        200: OK - (operation successful)

        400: Bad Request - ErrorEntity (40035: errors.net.accelbyte.platform.legal.invalid_policy_version | 40046: errors.net.accelbyte.platform.legal.default_selection_not_provided | 40030: errors.net.accelbyte.platform.legal.localized_policy_version_not_provided)

        409: Conflict - ErrorEntity (40039: errors.net.accelbyte.platform.legal.localized_policy_version_already_latest | 40043: errors.net.accelbyte.platform.legal.localized_policy_version_already_publish)

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
            return HttpResponse.create(code, "OK"), None
        if code == 400:
            return None, ErrorEntity.create_from_dict(content)
        if code == 409:
            return None, ErrorEntity.create_from_dict(content)

        return self.handle_undocumented_response(
            code=code, content_type=content_type, content=content
        )

    # endregion response methods

    # region static methods

    @classmethod
    def create(
        cls,
        namespace: str,
        policy_version_id: str,
        should_notify: Optional[bool] = None,
        **kwargs,
    ) -> PublishPolicyVersion1:
        instance = cls()
        instance.namespace = namespace
        instance.policy_version_id = policy_version_id
        if should_notify is not None:
            instance.should_notify = should_notify
        if x_flight_id := kwargs.get("x_flight_id", None):
            instance.x_flight_id = x_flight_id
        return instance

    @classmethod
    def create_from_dict(
        cls, dict_: dict, include_empty: bool = False
    ) -> PublishPolicyVersion1:
        instance = cls()
        if "namespace" in dict_ and dict_["namespace"] is not None:
            instance.namespace = str(dict_["namespace"])
        elif include_empty:
            instance.namespace = ""
        if "policyVersionId" in dict_ and dict_["policyVersionId"] is not None:
            instance.policy_version_id = str(dict_["policyVersionId"])
        elif include_empty:
            instance.policy_version_id = ""
        if "shouldNotify" in dict_ and dict_["shouldNotify"] is not None:
            instance.should_notify = bool(dict_["shouldNotify"])
        elif include_empty:
            instance.should_notify = False
        return instance

    @staticmethod
    def get_field_info() -> Dict[str, str]:
        return {
            "namespace": "namespace",
            "policyVersionId": "policy_version_id",
            "shouldNotify": "should_notify",
        }

    @staticmethod
    def get_required_map() -> Dict[str, bool]:
        return {
            "namespace": True,
            "policyVersionId": True,
            "shouldNotify": False,
        }

    # endregion static methods

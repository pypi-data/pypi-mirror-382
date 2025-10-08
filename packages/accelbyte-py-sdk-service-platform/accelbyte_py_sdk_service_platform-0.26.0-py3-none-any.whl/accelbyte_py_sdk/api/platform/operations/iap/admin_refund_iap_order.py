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

# AccelByte Gaming Services Platform Service

from __future__ import annotations
from typing import Any, Dict, List, Optional, Tuple, Union

from accelbyte_py_sdk.core import ApiError, ApiResponse
from accelbyte_py_sdk.core import Operation
from accelbyte_py_sdk.core import HeaderStr
from accelbyte_py_sdk.core import HttpResponse
from accelbyte_py_sdk.core import deprecated

from ...models import ErrorEntity
from ...models import IAPOrderInfo


class AdminRefundIAPOrder(Operation):
    """Refund IAP Order (adminRefundIAPOrder)

    Only support steam transaction mode

    Properties:
        url: /platform/admin/namespaces/{namespace}/iap/steam/orders/{iapOrderNo}/refund

        method: PUT

        tags: ["IAP"]

        consumes: []

        produces: ["application/json"]

        securities: [BEARER_AUTH]

        iap_order_no: (iapOrderNo) REQUIRED str in path

        namespace: (namespace) REQUIRED str in path

    Responses:
        200: OK - IAPOrderInfo (successful operation)

        204: No Content - (Refund IAP Order successfully)

        400: Bad Request - ErrorEntity (39124: IAP request platform [{platformId}] user id is not linked with current user)

        404: Not Found - ErrorEntity (39144: Steam IAP config not found in namespace [{namespace}]. | 39151: IAP order no [{iapOrderNo}] not found in namespace [{namespace}].)

        409: Conflict - ErrorEntity (39184: Steam api exception with status code [{statusCode}] and error message [{message}] | 39185: This endpoint only works on sync mode [{workSyncMode}], but current steam iap config sync mode is [{currentSyncMode}] under namespace [{namespace}])
    """

    # region fields

    _url: str = (
        "/platform/admin/namespaces/{namespace}/iap/steam/orders/{iapOrderNo}/refund"
    )
    _path: str = (
        "/platform/admin/namespaces/{namespace}/iap/steam/orders/{iapOrderNo}/refund"
    )
    _base_path: str = ""
    _method: str = "PUT"
    _consumes: List[str] = []
    _produces: List[str] = ["application/json"]
    _securities: List[List[str]] = [["BEARER_AUTH"]]
    _location_query: str = None

    service_name: Optional[str] = "platform"

    iap_order_no: str  # REQUIRED in [path]
    namespace: str  # REQUIRED in [path]

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
        if hasattr(self, "iap_order_no"):
            result["iapOrderNo"] = self.iap_order_no
        if hasattr(self, "namespace"):
            result["namespace"] = self.namespace
        return result

    # endregion get_x_params methods

    # region is/has methods

    # endregion is/has methods

    # region with_x methods

    def with_iap_order_no(self, value: str) -> AdminRefundIAPOrder:
        self.iap_order_no = value
        return self

    def with_namespace(self, value: str) -> AdminRefundIAPOrder:
        self.namespace = value
        return self

    # endregion with_x methods

    # region to methods

    def to_dict(self, include_empty: bool = False) -> dict:
        result: dict = {}
        if hasattr(self, "iap_order_no") and self.iap_order_no:
            result["iapOrderNo"] = str(self.iap_order_no)
        elif include_empty:
            result["iapOrderNo"] = ""
        if hasattr(self, "namespace") and self.namespace:
            result["namespace"] = str(self.namespace)
        elif include_empty:
            result["namespace"] = ""
        return result

    # endregion to methods

    # region response methods

    class Response(ApiResponse):
        data_200: Optional[IAPOrderInfo] = None
        data_204: Optional[HttpResponse] = None
        error_400: Optional[ErrorEntity] = None
        error_404: Optional[ErrorEntity] = None
        error_409: Optional[ErrorEntity] = None

        def ok(self) -> AdminRefundIAPOrder.Response:
            if self.error_400 is not None:
                err = self.error_400.translate_to_api_error()
                exc = err.to_exception()
                if exc is not None:
                    raise exc  # pylint: disable=raising-bad-type
            if self.error_404 is not None:
                err = self.error_404.translate_to_api_error()
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
            elif self.data_204 is not None:
                yield self.data_204
                yield None
            elif self.error_400 is not None:
                yield None
                yield self.error_400
            elif self.error_404 is not None:
                yield None
                yield self.error_404
            elif self.error_409 is not None:
                yield None
                yield self.error_409
            else:
                yield None
                yield self.error

    # noinspection PyMethodMayBeStatic
    def parse_response(self, code: int, content_type: str, content: Any) -> Response:
        """Parse the given response.

        200: OK - IAPOrderInfo (successful operation)

        204: No Content - (Refund IAP Order successfully)

        400: Bad Request - ErrorEntity (39124: IAP request platform [{platformId}] user id is not linked with current user)

        404: Not Found - ErrorEntity (39144: Steam IAP config not found in namespace [{namespace}]. | 39151: IAP order no [{iapOrderNo}] not found in namespace [{namespace}].)

        409: Conflict - ErrorEntity (39184: Steam api exception with status code [{statusCode}] and error message [{message}] | 39185: This endpoint only works on sync mode [{workSyncMode}], but current steam iap config sync mode is [{currentSyncMode}] under namespace [{namespace}])

        ---: HttpResponse (Undocumented Response)

        ---: HttpResponse (Unexpected Content-Type Error)

        ---: HttpResponse (Unhandled Error)
        """
        result = AdminRefundIAPOrder.Response()

        pre_processed_response, error = self.pre_process_response(
            code=code, content_type=content_type, content=content
        )

        if error is not None:
            if not error.is_no_content():
                result.error = ApiError.create_from_http_response(error)
        else:
            code, content_type, content = pre_processed_response

            if code == 200:
                result.data_200 = IAPOrderInfo.create_from_dict(content)
            elif code == 204:
                result.data_204 = None
            elif code == 400:
                result.error_400 = ErrorEntity.create_from_dict(content)
                result.error = result.error_400.translate_to_api_error()
            elif code == 404:
                result.error_404 = ErrorEntity.create_from_dict(content)
                result.error = result.error_404.translate_to_api_error()
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
    ) -> Tuple[Union[None, IAPOrderInfo], Union[None, ErrorEntity, HttpResponse]]:
        """Parse the given response.

        200: OK - IAPOrderInfo (successful operation)

        204: No Content - (Refund IAP Order successfully)

        400: Bad Request - ErrorEntity (39124: IAP request platform [{platformId}] user id is not linked with current user)

        404: Not Found - ErrorEntity (39144: Steam IAP config not found in namespace [{namespace}]. | 39151: IAP order no [{iapOrderNo}] not found in namespace [{namespace}].)

        409: Conflict - ErrorEntity (39184: Steam api exception with status code [{statusCode}] and error message [{message}] | 39185: This endpoint only works on sync mode [{workSyncMode}], but current steam iap config sync mode is [{currentSyncMode}] under namespace [{namespace}])

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
            return IAPOrderInfo.create_from_dict(content), None
        if code == 204:
            return None, None
        if code == 400:
            return None, ErrorEntity.create_from_dict(content)
        if code == 404:
            return None, ErrorEntity.create_from_dict(content)
        if code == 409:
            return None, ErrorEntity.create_from_dict(content)

        return self.handle_undocumented_response(
            code=code, content_type=content_type, content=content
        )

    # endregion response methods

    # region static methods

    @classmethod
    def create(cls, iap_order_no: str, namespace: str, **kwargs) -> AdminRefundIAPOrder:
        instance = cls()
        instance.iap_order_no = iap_order_no
        instance.namespace = namespace
        if x_flight_id := kwargs.get("x_flight_id", None):
            instance.x_flight_id = x_flight_id
        return instance

    @classmethod
    def create_from_dict(
        cls, dict_: dict, include_empty: bool = False
    ) -> AdminRefundIAPOrder:
        instance = cls()
        if "iapOrderNo" in dict_ and dict_["iapOrderNo"] is not None:
            instance.iap_order_no = str(dict_["iapOrderNo"])
        elif include_empty:
            instance.iap_order_no = ""
        if "namespace" in dict_ and dict_["namespace"] is not None:
            instance.namespace = str(dict_["namespace"])
        elif include_empty:
            instance.namespace = ""
        return instance

    @staticmethod
    def get_field_info() -> Dict[str, str]:
        return {
            "iapOrderNo": "iap_order_no",
            "namespace": "namespace",
        }

    @staticmethod
    def get_required_map() -> Dict[str, bool]:
        return {
            "iapOrderNo": True,
            "namespace": True,
        }

    # endregion static methods

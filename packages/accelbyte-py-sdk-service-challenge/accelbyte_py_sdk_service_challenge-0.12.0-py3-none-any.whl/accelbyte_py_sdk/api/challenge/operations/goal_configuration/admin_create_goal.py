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

# AccelByte Gaming Services Challenge Service

from __future__ import annotations
from typing import Any, Dict, List, Optional, Tuple, Union

from accelbyte_py_sdk.core import ApiError, ApiResponse
from accelbyte_py_sdk.core import Operation
from accelbyte_py_sdk.core import HeaderStr
from accelbyte_py_sdk.core import HttpResponse
from accelbyte_py_sdk.core import deprecated

from ...models import IamErrorResponse
from ...models import ModelCreateGoalRequest
from ...models import ModelGoalResponse
from ...models import ResponseError


class AdminCreateGoal(Operation):
    """Create New Goal (adminCreateGoal)

    - Required permission: ADMIN:NAMESPACE:{namespace}:CHALLENGE [CREATE]
    Request body:
    - code: unique within a challenge.
    - name: name of the goal.
    - description: text describing the goal (optional).
    - schedule: a time range that indicated the availability of a goal within a timeframe. Used in FIXED assignment rule, this will be required in that case.
    - requirementGroups: contains array of objects consisting of operator and predicates attribute. When requirements evaluation happened, each item's predicates will be evaluated first, by operating the predicates with given operator.
    After all items evaluated, the results of the evaluation on each item then will be logically evaluated using OR operator.
    - operator: logical operator used to validate the completion of a goal. a goal is considered complete once complete predicates operated with operator result in true.
    - predicates: list of progression parameters to be tracked.
    - parameterType: the type of parameter for challenge to be progressed with. the available options are:
    - STATISTIC: progress by user statistic item value.
    - STATISTIC_CYCLE: progress user statistic cycle item value. statCycleId must be included.
    - ACHIEVEMENT: progress by user achievement.
    - USERACCOUNT: progress by user account event.
    - ENTITLEMENT: progress by user's item entitlement ownership. Supported item types are APP, CODE, INGAMEITEM, LOOTBOX, MEDIA, and OPTIONBOX.
    - parameterName: the name of the parameter for challenge to be progressed with.
    - STATISTIC: refers to stat code.
    - STATISTIC_CYCLE: refers to stat code with statCycleId must be included.
    - ACHIEVEMENT: refers to achievement code.
    - USERACCOUNT: refers to a specific event related to user accounts. The current possible events include: userAccountCreated, gameUserAccountCreated, userAccountVerified, userAccountLinked, userAccountUpgraded, thirdPartyAccountCreated, userLoggedIn, userThirdPartyLoggedIn and fullAccount.
    - For the **userAccountLinked** event, **parameterName** will utilize **platformId** rather than the event name. This will be validated against the list of active third-party accounts configuration within the namespace, such as *psn*, *steam*, or *device*.
    - ENTITLEMENT: ecommerce store's item SKU.
    - matcher: the comparison operator used to compare the current value of a parameter and targetValue to validate the completion of a predicate. Possible values are EQUAL, LESS_THAN, GREATER_THAN, LESS_THAN_EQUAL, and GREATER_THAN_EQUAL.
    - targetValue: the target number to be reached by the parameter.
    - statCycleId: specify the statCycleId used to track statistic value in a cycle with STATISTIC_CYCLE parameterType (optional).
    - rewards: list of rewards that will be claimable once a goal is complete.
    - tags: goal's labels.
    - isActive: when goal is in a schedule, isActive determine whether goal is active to progress or not.
    Goal describe set of requirements that need to be fulfilled by players in order to complete it and describe what is the rewards given to player when they complete the goal.
    The requirement will have target value and a operator that will evaluate that against an observable playerâs attribute (e.g. statistic, entitlement). Goal belongs to a challenge.
    Supported item type for ENTITLEMENT reward type: APP, BUNDLE, CODE, COINS, EXTENSION, INGAMEITEM, LOOTBOX, MEDIA, OPTIONBOX.
    Number of goals per challenge is **limited to 100 goals**.

    Properties:
        url: /challenge/v1/admin/namespaces/{namespace}/challenges/{challengeCode}/goals

        method: POST

        tags: ["Goal Configuration"]

        consumes: ["application/json"]

        produces: ["application/json"]

        securities: [BEARER_AUTH]

        body: (body) REQUIRED ModelCreateGoalRequest in body

        challenge_code: (challengeCode) REQUIRED str in path

        namespace: (namespace) REQUIRED str in path

    Responses:
        201: Created - ModelGoalResponse (Created)

        400: Bad Request - IamErrorResponse (20018: bad request: {{message}})

        401: Unauthorized - IamErrorResponse (20001: unauthorized access)

        403: Forbidden - IamErrorResponse (20013: insufficient permission)

        404: Not Found - ResponseError (20029: not found)

        409: Conflict - ResponseError (99002: duplicate key error: {{message}})

        422: Unprocessable Entity - IamErrorResponse (99004: unprocessable entity: {{message}})

        500: Internal Server Error - ResponseError (20000: internal server error: {{message}})
    """

    # region fields

    _url: str = (
        "/challenge/v1/admin/namespaces/{namespace}/challenges/{challengeCode}/goals"
    )
    _path: str = (
        "/challenge/v1/admin/namespaces/{namespace}/challenges/{challengeCode}/goals"
    )
    _base_path: str = ""
    _method: str = "POST"
    _consumes: List[str] = ["application/json"]
    _produces: List[str] = ["application/json"]
    _securities: List[List[str]] = [["BEARER_AUTH"]]
    _location_query: str = None

    service_name: Optional[str] = "challenge"

    body: ModelCreateGoalRequest  # REQUIRED in [body]
    challenge_code: str  # REQUIRED in [path]
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
            "body": self.get_body_params(),
            "path": self.get_path_params(),
        }

    def get_body_params(self) -> Any:
        if not hasattr(self, "body") or self.body is None:
            return None
        return self.body.to_dict()

    def get_path_params(self) -> dict:
        result = {}
        if hasattr(self, "challenge_code"):
            result["challengeCode"] = self.challenge_code
        if hasattr(self, "namespace"):
            result["namespace"] = self.namespace
        return result

    # endregion get_x_params methods

    # region is/has methods

    # endregion is/has methods

    # region with_x methods

    def with_body(self, value: ModelCreateGoalRequest) -> AdminCreateGoal:
        self.body = value
        return self

    def with_challenge_code(self, value: str) -> AdminCreateGoal:
        self.challenge_code = value
        return self

    def with_namespace(self, value: str) -> AdminCreateGoal:
        self.namespace = value
        return self

    # endregion with_x methods

    # region to methods

    def to_dict(self, include_empty: bool = False) -> dict:
        result: dict = {}
        if hasattr(self, "body") and self.body:
            result["body"] = self.body.to_dict(include_empty=include_empty)
        elif include_empty:
            result["body"] = ModelCreateGoalRequest()
        if hasattr(self, "challenge_code") and self.challenge_code:
            result["challengeCode"] = str(self.challenge_code)
        elif include_empty:
            result["challengeCode"] = ""
        if hasattr(self, "namespace") and self.namespace:
            result["namespace"] = str(self.namespace)
        elif include_empty:
            result["namespace"] = ""
        return result

    # endregion to methods

    # region response methods

    class Response(ApiResponse):
        data_201: Optional[ModelGoalResponse] = None
        error_400: Optional[IamErrorResponse] = None
        error_401: Optional[IamErrorResponse] = None
        error_403: Optional[IamErrorResponse] = None
        error_404: Optional[ResponseError] = None
        error_409: Optional[ResponseError] = None
        error_422: Optional[IamErrorResponse] = None
        error_500: Optional[ResponseError] = None

        def ok(self) -> AdminCreateGoal.Response:
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
            if self.error_409 is not None:
                err = self.error_409.translate_to_api_error()
                exc = err.to_exception()
                if exc is not None:
                    raise exc  # pylint: disable=raising-bad-type
            if self.error_422 is not None:
                err = self.error_422.translate_to_api_error()
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
            elif self.error_404 is not None:
                yield None
                yield self.error_404
            elif self.error_409 is not None:
                yield None
                yield self.error_409
            elif self.error_422 is not None:
                yield None
                yield self.error_422
            elif self.error_500 is not None:
                yield None
                yield self.error_500
            else:
                yield None
                yield self.error

    # noinspection PyMethodMayBeStatic
    def parse_response(self, code: int, content_type: str, content: Any) -> Response:
        """Parse the given response.

        201: Created - ModelGoalResponse (Created)

        400: Bad Request - IamErrorResponse (20018: bad request: {{message}})

        401: Unauthorized - IamErrorResponse (20001: unauthorized access)

        403: Forbidden - IamErrorResponse (20013: insufficient permission)

        404: Not Found - ResponseError (20029: not found)

        409: Conflict - ResponseError (99002: duplicate key error: {{message}})

        422: Unprocessable Entity - IamErrorResponse (99004: unprocessable entity: {{message}})

        500: Internal Server Error - ResponseError (20000: internal server error: {{message}})

        ---: HttpResponse (Undocumented Response)

        ---: HttpResponse (Unexpected Content-Type Error)

        ---: HttpResponse (Unhandled Error)
        """
        result = AdminCreateGoal.Response()

        pre_processed_response, error = self.pre_process_response(
            code=code, content_type=content_type, content=content
        )

        if error is not None:
            if not error.is_no_content():
                result.error = ApiError.create_from_http_response(error)
        else:
            code, content_type, content = pre_processed_response

            if code == 201:
                result.data_201 = ModelGoalResponse.create_from_dict(content)
            elif code == 400:
                result.error_400 = IamErrorResponse.create_from_dict(content)
                result.error = result.error_400.translate_to_api_error()
            elif code == 401:
                result.error_401 = IamErrorResponse.create_from_dict(content)
                result.error = result.error_401.translate_to_api_error()
            elif code == 403:
                result.error_403 = IamErrorResponse.create_from_dict(content)
                result.error = result.error_403.translate_to_api_error()
            elif code == 404:
                result.error_404 = ResponseError.create_from_dict(content)
                result.error = result.error_404.translate_to_api_error()
            elif code == 409:
                result.error_409 = ResponseError.create_from_dict(content)
                result.error = result.error_409.translate_to_api_error()
            elif code == 422:
                result.error_422 = IamErrorResponse.create_from_dict(content)
                result.error = result.error_422.translate_to_api_error()
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
        Union[None, ModelGoalResponse],
        Union[None, HttpResponse, IamErrorResponse, ResponseError],
    ]:
        """Parse the given response.

        201: Created - ModelGoalResponse (Created)

        400: Bad Request - IamErrorResponse (20018: bad request: {{message}})

        401: Unauthorized - IamErrorResponse (20001: unauthorized access)

        403: Forbidden - IamErrorResponse (20013: insufficient permission)

        404: Not Found - ResponseError (20029: not found)

        409: Conflict - ResponseError (99002: duplicate key error: {{message}})

        422: Unprocessable Entity - IamErrorResponse (99004: unprocessable entity: {{message}})

        500: Internal Server Error - ResponseError (20000: internal server error: {{message}})

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
            return ModelGoalResponse.create_from_dict(content), None
        if code == 400:
            return None, IamErrorResponse.create_from_dict(content)
        if code == 401:
            return None, IamErrorResponse.create_from_dict(content)
        if code == 403:
            return None, IamErrorResponse.create_from_dict(content)
        if code == 404:
            return None, ResponseError.create_from_dict(content)
        if code == 409:
            return None, ResponseError.create_from_dict(content)
        if code == 422:
            return None, IamErrorResponse.create_from_dict(content)
        if code == 500:
            return None, ResponseError.create_from_dict(content)

        return self.handle_undocumented_response(
            code=code, content_type=content_type, content=content
        )

    # endregion response methods

    # region static methods

    @classmethod
    def create(
        cls, body: ModelCreateGoalRequest, challenge_code: str, namespace: str, **kwargs
    ) -> AdminCreateGoal:
        instance = cls()
        instance.body = body
        instance.challenge_code = challenge_code
        instance.namespace = namespace
        if x_flight_id := kwargs.get("x_flight_id", None):
            instance.x_flight_id = x_flight_id
        return instance

    @classmethod
    def create_from_dict(
        cls, dict_: dict, include_empty: bool = False
    ) -> AdminCreateGoal:
        instance = cls()
        if "body" in dict_ and dict_["body"] is not None:
            instance.body = ModelCreateGoalRequest.create_from_dict(
                dict_["body"], include_empty=include_empty
            )
        elif include_empty:
            instance.body = ModelCreateGoalRequest()
        if "challengeCode" in dict_ and dict_["challengeCode"] is not None:
            instance.challenge_code = str(dict_["challengeCode"])
        elif include_empty:
            instance.challenge_code = ""
        if "namespace" in dict_ and dict_["namespace"] is not None:
            instance.namespace = str(dict_["namespace"])
        elif include_empty:
            instance.namespace = ""
        return instance

    @staticmethod
    def get_field_info() -> Dict[str, str]:
        return {
            "body": "body",
            "challengeCode": "challenge_code",
            "namespace": "namespace",
        }

    @staticmethod
    def get_required_map() -> Dict[str, bool]:
        return {
            "body": True,
            "challengeCode": True,
            "namespace": True,
        }

    # endregion static methods

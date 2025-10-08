# Copyright (c) 2024 AccelByte Inc. All Rights Reserved.
# This is licensed software from AccelByte Inc, for limitations
# and restrictions contact your company contract manager.
#
# Code generated. DO NOT EDIT!

# template file: errors.j2

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

from accelbyte_py_sdk.core import ApiError

ERROR_20000 = ApiError(code="20000", message="internal server error: {{message}}")
ERROR_20001 = ApiError(code="20001", message="unauthorized access")
ERROR_20013 = ApiError(code="20013", message="insufficient permission")
ERROR_20018 = ApiError(code="20018", message="bad request: {{message}}")
ERROR_20029 = ApiError(code="20029", message="not found")
ERROR_99002 = ApiError(code="99002", message="duplicate key error: {{message}}")
ERROR_99003 = ApiError(code="99003", message="challenge validation error: {{message}}")
ERROR_99004 = ApiError(code="99004", message="unprocessable entity: {{message}}")

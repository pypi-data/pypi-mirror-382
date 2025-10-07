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

# AccelByte Gaming Services Session Browser Service

from accelbyte_py_sdk.core import ApiError

ERROR_20000 = ApiError(code="20000", message="internal server error")
ERROR_20001 = ApiError(code="20001", message="unauthorized access")
ERROR_20002 = ApiError(code="20002", message="validation error")
ERROR_20013 = ApiError(code="20013", message="insufficient permissions")
ERROR_20014 = ApiError(code="20014", message="invalid audience")
ERROR_20015 = ApiError(code="20015", message="insufficient scope")
ERROR_20019 = ApiError(code="20019", message="unable to parse request body")

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

# AccelByte Gaming Services Group Service

from accelbyte_py_sdk.core import ApiError

ERROR_20001 = ApiError(code="20001", message="unauthorized access")
ERROR_20002 = ApiError(code="20002", message="validation error")
ERROR_20013 = ApiError(code="20013", message="insufficient permissions")
ERROR_20019 = ApiError(code="20019", message="unable to parse request body")
ERROR_20022 = ApiError(code="20022", message="token is not user token")
ERROR_73034 = ApiError(code="73034", message="user not belong to any group")
ERROR_73036 = ApiError(code="73036", message="insufficient member role permission")
ERROR_73130 = ApiError(code="73130", message="global configuration already exist")
ERROR_73131 = ApiError(code="73131", message="global configuration not found")
ERROR_73232 = ApiError(code="73232", message="member role not found")
ERROR_73333 = ApiError(code="73333", message="group not found")
ERROR_73342 = ApiError(code="73342", message="user already joined group")
ERROR_73433 = ApiError(code="73433", message="member group not found")
ERROR_73437 = ApiError(code="73437", message="user already invited")
ERROR_73438 = ApiError(code="73438", message="user already requested to join")
ERROR_73440 = ApiError(code="73440", message="group admin cannot leave group")
ERROR_73442 = ApiError(code="73442", message="user already joined in another group")
ERROR_73443 = ApiError(code="73443", message="member request not found")
ERROR_73444 = ApiError(code="73444", message="member must have role")

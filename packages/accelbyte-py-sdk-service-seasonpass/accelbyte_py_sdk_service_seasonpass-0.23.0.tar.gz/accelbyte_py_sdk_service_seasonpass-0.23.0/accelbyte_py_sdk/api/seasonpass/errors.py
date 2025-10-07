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

# AccelByte Gaming Services Seasonpass Service

from accelbyte_py_sdk.core import ApiError

ERROR_20001 = ApiError(code="20001", message="Unauthorized")
ERROR_20002 = ApiError(code="20002", message="validation error")
ERROR_20026 = ApiError(code="20026", message="publisher namespace not allowed")
ERROR_30141 = ApiError(
    code="30141", message="Store [{storeId}] does not exist in namespace [{namespace}]"
)
ERROR_30142 = ApiError(
    code="30142", message="Published store does not exist in namespace [{namespace}]"
)
ERROR_30341 = ApiError(
    code="30341", message="Item [{itemId}] does not exist in namespace [{namespace}]"
)
ERROR_36141 = ApiError(
    code="36141",
    message="Currency [{currencyCode}] does not exist in namespace [{namespace}]",
)
ERROR_49121 = ApiError(
    code="49121", message="Default language [{language}] required in localizations"
)
ERROR_49122 = ApiError(code="49122", message="Invalid time range")
ERROR_49124 = ApiError(code="49124", message="Manual claim not supported")
ERROR_49141 = ApiError(
    code="49141",
    message="Tier item does not exist in the store of namespace [{namespace}]",
)
ERROR_49142 = ApiError(
    code="49142",
    message="Pass item does not exist in the store of namespace [{namespace}]",
)
ERROR_49143 = ApiError(
    code="49143",
    message="Season [{seasonId}] does not exist in namespace [{namespace}]",
)
ERROR_49144 = ApiError(code="49144", message="Reward [{code}] does not exist")
ERROR_49145 = ApiError(code="49145", message="Pass [{code}] does not exist")
ERROR_49146 = ApiError(code="49146", message="Tier does not exist")
ERROR_49147 = ApiError(code="49147", message="Published season does not exist")
ERROR_49148 = ApiError(code="49148", message="User season does not exist")
ERROR_49171 = ApiError(code="49171", message="Invalid season status [{status}]")
ERROR_49172 = ApiError(code="49172", message="Season is already ended")
ERROR_49173 = ApiError(
    code="49173", message="Reward [{code}] already exists in the season"
)
ERROR_49174 = ApiError(
    code="49174", message="Pass [{code}] already exists in the season"
)
ERROR_49175 = ApiError(
    code="49175", message="Published season already exists in namespace [{namespace}]"
)
ERROR_49176 = ApiError(code="49176", message="Rewards are not provided")
ERROR_49177 = ApiError(code="49177", message="Passes are not provided")
ERROR_49178 = ApiError(code="49178", message="Tiers are not provided")
ERROR_49179 = ApiError(code="49179", message="Reward [{code}] is in use")
ERROR_49180 = ApiError(code="49180", message="Season is already started")
ERROR_49181 = ApiError(code="49181", message="Season has not ended")
ERROR_49182 = ApiError(code="49182", message="Reward is already claimed")
ERROR_49183 = ApiError(
    code="49183", message="Pass item does not match published season pass"
)
ERROR_49184 = ApiError(
    code="49184", message="Tier item does not match published season tier"
)
ERROR_49185 = ApiError(code="49185", message="Season has not started")
ERROR_49186 = ApiError(code="49186", message="Pass already owned")
ERROR_49187 = ApiError(code="49187", message="Exceed max tier count")
ERROR_49188 = ApiError(code="49188", message="Reward is claiming")
ERROR_49189 = ApiError(
    code="49189",
    message="Duplicate season name [{name}] for publishing in namespace [{namespace}]",
)

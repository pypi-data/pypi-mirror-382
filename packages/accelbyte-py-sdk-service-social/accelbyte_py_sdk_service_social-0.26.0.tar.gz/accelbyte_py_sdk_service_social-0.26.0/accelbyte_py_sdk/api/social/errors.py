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

# AccelByte Gaming Services Statistics Service

from accelbyte_py_sdk.core import ApiError

ERROR_12021 = ApiError(
    code="12021",
    message="{totalUser} users is requested. Cannot retrieve more than {limitUser} users at once",
)
ERROR_12022 = ApiError(
    code="12022",
    message="Game profile attribute name [{attrName1}] passed in request url mismatch the name [{attrName2}] in body",
)
ERROR_12041 = ApiError(
    code="12041", message="Game profile with id [{profileId}] is not found"
)
ERROR_12121 = ApiError(code="12121", message="Checksum mismatch for [{filename}]")
ERROR_12122 = ApiError(
    code="12122",
    message="[{filename}] exceeds the upload limit size of [{sizeLimit}] bytes",
)
ERROR_12141 = ApiError(
    code="12141", message="Slot [{slotId}] not found in namespace [{namespace}]"
)
ERROR_12171 = ApiError(
    code="12171",
    message="User [{userId}] exceed max slot count [{maxCount}] in namespace [{namespace}]",
)
ERROR_12221 = ApiError(
    code="12221",
    message="Invalid stat operator, expect [{expected}] but actual [{actual}]",
)
ERROR_12222 = ApiError(
    code="12222", message="Stats data for namespace [{namespace}] is invalid"
)
ERROR_12223 = ApiError(
    code="12223", message="Invalid stat codes in namespace [{namespace}]: [{statCodes}]"
)
ERROR_12225 = ApiError(code="12225", message="Invalid time range")
ERROR_12226 = ApiError(code="12226", message="Invalid date [{date}] of month [{month}]")
ERROR_12241 = ApiError(
    code="12241", message="Stat [{statCode}] cannot be found in namespace [{namespace}]"
)
ERROR_12242 = ApiError(
    code="12242",
    message="Stat item of [{statCode}] of user [{profileId}] cannot be found in namespace [{namespace}]",
)
ERROR_12243 = ApiError(
    code="12243", message="Stats cannot be found in namespace [{namespace}]"
)
ERROR_12244 = ApiError(
    code="12244",
    message="Global stat item of [{statCode}] cannot be found in namespace [{namespace}]",
)
ERROR_12245 = ApiError(
    code="12245", message="Stat cycle [{id}] cannot be found in namespace [{namespace}]"
)
ERROR_12271 = ApiError(
    code="12271",
    message="Stat template with code [{statCode}] already exists in namespace [{namespace}]",
)
ERROR_12273 = ApiError(code="12273", message="Stat [{statCode}] is not decreasable")
ERROR_12274 = ApiError(
    code="12274",
    message="Stat item with code [{statCode}] of user [{profileId}] already exists in namespace [{namespace}]",
)
ERROR_12275 = ApiError(
    code="12275",
    message="[{action}] value: [{value}] of stat [{statCode}] is out of range while minimum [{minimum}] and maximum [{maximum}] in namespace [{namespace}]",
)
ERROR_12276 = ApiError(
    code="12276",
    message=" Stat template with code [{statCode}] in namespace [{namespace}] not deletable due it is in an INIT status ",
)
ERROR_12277 = ApiError(
    code="12277",
    message="Stat cycle [{id}] in namespace [{namespace}] with status [{status}] cannot be updated",
)
ERROR_12279 = ApiError(
    code="12279",
    message="Invalid stat cycle status: Stat cycle [{id}], namespace [{namespace}], status [{status}]",
)
ERROR_20000 = ApiError(code="20000", message="Internal server error")
ERROR_20001 = ApiError(code="20001", message="unauthorized access")
ERROR_20002 = ApiError(code="20002", message="validation error")
ERROR_20013 = ApiError(code="20013", message="insufficient permission")

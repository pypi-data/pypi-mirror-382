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

# AccelByte Gaming Services Basic Service

from accelbyte_py_sdk.core import ApiError

ERROR_11121 = ApiError(
    code="11121", message="Unable to {action}: category {category} is not valid"
)
ERROR_11131 = ApiError(
    code="11131", message="Unable to {action}: File type is not supported"
)
ERROR_11132 = ApiError(
    code="11132",
    message="Unable to {action}: file storage exceed limitation, user ID: {userId}, namespace: {namespace}",
)
ERROR_11233 = ApiError(
    code="11233",
    message="Unable to {action}: Country group with code [{countryGroupCode}] is not found",
)
ERROR_11234 = ApiError(
    code="11234",
    message="Unable to {action}: A country can't be assigned to more than one country group",
)
ERROR_11235 = ApiError(
    code="11235",
    message="Unable to {action}: Country group with specified code is already exist",
)
ERROR_11336 = ApiError(
    code="11336", message="Unable to {action}: Namespace already exists"
)
ERROR_11337 = ApiError(code="11337", message="Unable to {action}: Namespace not found")
ERROR_11338 = ApiError(
    code="11338", message="Unable to {action}: Namespace contains invalid character(s)"
)
ERROR_11339 = ApiError(
    code="11339",
    message="Unable to {action}: Display name contains invalid character(s)",
)
ERROR_11340 = ApiError(
    code="11340",
    message="Unable to {action}: The maximum number of games namespace for studio:{studio} has been exceeded",
)
ERROR_11440 = ApiError(
    code="11440",
    message="Unable to {action}: User profile not found in namespace [{namespace}]",
)
ERROR_11441 = ApiError(
    code="11441", message="Unable to {action}: User profile already exists"
)
ERROR_11469 = ApiError(
    code="11469",
    message="User profile with publicId [{publicId}] not found in namespace [{namespace}]",
)
ERROR_11741 = ApiError(code="11741", message="Unable to {action}: Config not found")
ERROR_11771 = ApiError(
    code="11771", message="Unable to {action}: Config already exists"
)
ERROR_20000 = ApiError(code="20000", message="internal server error")
ERROR_20001 = ApiError(code="20001", message="unauthorized")
ERROR_20002 = ApiError(code="20002", message="validation error")
ERROR_20006 = ApiError(code="20006", message="optimistic lock")
ERROR_20008 = ApiError(code="20008", message="user not found")
ERROR_20013 = ApiError(code="20013", message="insufficient permission")
ERROR_20017 = ApiError(code="20017", message="user not linked")
ERROR_20019 = ApiError(code="20019", message="unable to parse request body")

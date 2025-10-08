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

# AccelByte Gaming Services Cloudsave Service

from accelbyte_py_sdk.core import ApiError

ERROR_18001 = ApiError(code="18001", message="unable to get record")
ERROR_18003 = ApiError(code="18003", message="record not found")
ERROR_18004 = ApiError(code="18004", message="unable to retrieve list of key records")
ERROR_18005 = ApiError(code="18005", message="unable to decode record")
ERROR_18006 = ApiError(code="18006", message="unable to decode record")
ERROR_18011 = ApiError(code="18011", message="invalid request body")
ERROR_18012 = ApiError(code="18012", message="unable to marshal request body")
ERROR_18013 = ApiError(code="18013", message="unable to save record")
ERROR_18015 = ApiError(
    code="18015",
    message="invalid request body: size of the request body must be less than [%d]MB",
)
ERROR_18020 = ApiError(code="18020", message="unable to get record")
ERROR_18022 = ApiError(code="18022", message="record not found")
ERROR_18023 = ApiError(
    code="18023", message="get action is forbidden on other user's record"
)
ERROR_18030 = ApiError(code="18030", message="invalid request body")
ERROR_18033 = ApiError(code="18033", message="unable to save record")
ERROR_18035 = ApiError(
    code="18035", message="post action is forbidden on other user's record"
)
ERROR_18040 = ApiError(code="18040", message="unable to delete record")
ERROR_18050 = ApiError(code="18050", message="invalid request body")
ERROR_18051 = ApiError(code="18051", message="unable to marshal request body")
ERROR_18052 = ApiError(
    code="18052",
    message="invalid request body: size of the request body must be less than [%d]MB",
)
ERROR_18053 = ApiError(code="18053", message="unable to update record")
ERROR_18056 = ApiError(code="18056", message="precondition failed: record has changed")
ERROR_18060 = ApiError(code="18060", message="invalid request body")
ERROR_18061 = ApiError(code="18061", message="unable to update record")
ERROR_18063 = ApiError(
    code="18063", message="put action is forbidden on other user's record"
)
ERROR_18064 = ApiError(code="18064", message="validation error")
ERROR_18065 = ApiError(code="18065", message="unable to update record")
ERROR_18066 = ApiError(code="18066", message="precondition failed: record has changed")
ERROR_18070 = ApiError(code="18070", message="unable to delete record")
ERROR_18072 = ApiError(
    code="18072", message="delete action is forbidden on other user's record"
)
ERROR_18080 = ApiError(code="18080", message="unable to get record")
ERROR_18081 = ApiError(code="18081", message="record not found")
ERROR_18083 = ApiError(code="18083", message="invalid request body")
ERROR_18084 = ApiError(code="18084", message="unable to get record")
ERROR_18090 = ApiError(code="18090", message="invalid request body")
ERROR_18091 = ApiError(code="18091", message="unable to save record")
ERROR_18100 = ApiError(code="18100", message="invalid request body")
ERROR_18101 = ApiError(code="18101", message="unable to update record")
ERROR_18102 = ApiError(code="18102", message="validation error")
ERROR_18103 = ApiError(code="18103", message="precondition failed: record has changed")
ERROR_18113 = ApiError(code="18113", message="invalid request body")
ERROR_18114 = ApiError(code="18114", message="unable to retrieve list of key records")
ERROR_18120 = ApiError(code="18120", message="unable to delete record")
ERROR_18122 = ApiError(code="18122", message="record not found")
ERROR_18124 = ApiError(code="18124", message="unable to get record")
ERROR_18125 = ApiError(code="18125", message="invalid request body")
ERROR_18126 = ApiError(
    code="18126", message="request record keys list exceed max size [%d]"
)
ERROR_18128 = ApiError(code="18128", message="invalid request body")
ERROR_18129 = ApiError(
    code="18129", message="request record keys list exceed max size [%d]"
)
ERROR_18130 = ApiError(code="18130", message="unable to get record")
ERROR_18131 = ApiError(code="18131", message="unable to decode record")
ERROR_18133 = ApiError(code="18133", message="record not found")
ERROR_18134 = ApiError(code="18134", message="invalid request body")
ERROR_18135 = ApiError(code="18135", message="unable to marshal request body")
ERROR_18136 = ApiError(
    code="18136",
    message="invalid request body: size of the request body must be less than [%d]MB",
)
ERROR_18138 = ApiError(code="18138", message="unable to decode record")
ERROR_18139 = ApiError(code="18139", message="unable to get record")
ERROR_18140 = ApiError(code="18140", message="record not found")
ERROR_18142 = ApiError(code="18142", message="unable to delete record")
ERROR_18144 = ApiError(code="18144", message="invalid request body")
ERROR_18145 = ApiError(code="18145", message="unable to marshal request body")
ERROR_18146 = ApiError(
    code="18146",
    message="invalid request body: size of the request body must be less than [%d]MB",
)
ERROR_18147 = ApiError(code="18147", message="unable to update record")
ERROR_18149 = ApiError(code="18149", message="invalid request body")
ERROR_18150 = ApiError(code="18150", message="invalid request body")
ERROR_18151 = ApiError(code="18151", message="unable to get record")
ERROR_18152 = ApiError(code="18152", message="record not found")
ERROR_18154 = ApiError(code="18154", message="unable to delete record")
ERROR_18156 = ApiError(code="18156", message="invalid request body")
ERROR_18157 = ApiError(code="18157", message="unable to decode record")
ERROR_18159 = ApiError(code="18159", message="invalid request body")
ERROR_18160 = ApiError(code="18160", message="unable to retrieve list of key records")
ERROR_18162 = ApiError(code="18162", message="unable to decode record")
ERROR_18163 = ApiError(code="18163", message="unable to decode record")
ERROR_18164 = ApiError(code="18164", message="unable to decode record")
ERROR_18165 = ApiError(code="18165", message="unable to decode record")
ERROR_18167 = ApiError(code="18167", message="record not found")
ERROR_18168 = ApiError(code="18168", message="invalid request body")
ERROR_18169 = ApiError(
    code="18169", message="request record keys list exceed max size [%d]"
)
ERROR_18170 = ApiError(code="18170", message="unable to get record")
ERROR_18171 = ApiError(code="18171", message="record not found")
ERROR_18172 = ApiError(code="18172", message="unable to decode record")
ERROR_18174 = ApiError(code="18174", message="invalid request body")
ERROR_18175 = ApiError(
    code="18175", message="request record keys list exceed max size [%d]"
)
ERROR_18176 = ApiError(code="18176", message="unable to get record")
ERROR_18177 = ApiError(code="18177", message="record not found")
ERROR_18178 = ApiError(code="18178", message="unable to decode record")
ERROR_18180 = ApiError(code="18180", message="precondition failed: record has changed")
ERROR_18181 = ApiError(code="18181", message="validation error")
ERROR_18182 = ApiError(code="18182", message="unable to update record")
ERROR_18183 = ApiError(code="18183", message="precondition failed: record has changed")
ERROR_18184 = ApiError(code="18184", message="invalid request body")
ERROR_18185 = ApiError(code="18185", message="unable to get record")
ERROR_18186 = ApiError(code="18186", message="record not found")
ERROR_18187 = ApiError(code="18187", message="unable to decode record")
ERROR_18201 = ApiError(
    code="18201", message="invalid record operator, expect [%s] but actual [%s]"
)
ERROR_18301 = ApiError(code="18301", message="unable to get record")
ERROR_18303 = ApiError(code="18303", message="record not found")
ERROR_18304 = ApiError(code="18304", message="invalid request body")
ERROR_18305 = ApiError(code="18305", message="invalid request body")
ERROR_18307 = ApiError(code="18307", message="unable to save record")
ERROR_18309 = ApiError(code="18309", message="key already exists")
ERROR_18310 = ApiError(code="18310", message="unable to get presigned URL")
ERROR_18311 = ApiError(code="18311", message="invalid request body")
ERROR_18312 = ApiError(code="18312", message="unable to get record")
ERROR_18313 = ApiError(code="18313", message="record not found")
ERROR_18314 = ApiError(code="18314", message="unable to get presigned URL")
ERROR_18316 = ApiError(code="18316", message="invalid request body")
ERROR_18317 = ApiError(code="18317", message="record not found")
ERROR_18318 = ApiError(code="18318", message="unable to update record")
ERROR_18320 = ApiError(code="18320", message="unable to delete record")
ERROR_18322 = ApiError(code="18322", message="record not found")
ERROR_18323 = ApiError(code="18323", message="unable to get record")
ERROR_18325 = ApiError(code="18325", message="record not found")
ERROR_18326 = ApiError(code="18326", message="invalid request body")
ERROR_18327 = ApiError(code="18327", message="invalid request body")
ERROR_18328 = ApiError(code="18328", message="unable to save record")
ERROR_18330 = ApiError(code="18330", message="key already exists")
ERROR_18331 = ApiError(code="18331", message="unable to get presigned URL")
ERROR_18332 = ApiError(code="18332", message="invalid request body")
ERROR_18333 = ApiError(code="18333", message="record not found")
ERROR_18334 = ApiError(code="18334", message="unable to update record")
ERROR_18336 = ApiError(code="18336", message="unable to delete record")
ERROR_18338 = ApiError(code="18338", message="record not found")
ERROR_18339 = ApiError(code="18339", message="unable to get record")
ERROR_18340 = ApiError(code="18340", message="record not found")
ERROR_18342 = ApiError(code="18342", message="invalid request body")
ERROR_18343 = ApiError(code="18343", message="unable to get record")
ERROR_18345 = ApiError(code="18345", message="unable to retrieve list of key records")
ERROR_18347 = ApiError(code="18347", message="invalid request body")
ERROR_18349 = ApiError(code="18349", message="unable to get record")
ERROR_18350 = ApiError(code="18350", message="invalid request body")
ERROR_18351 = ApiError(
    code="18351", message="request record keys list exceed max size [%d]"
)
ERROR_18353 = ApiError(code="18353", message="invalid request body")
ERROR_18354 = ApiError(code="18354", message="records amount exceeded max limit")
ERROR_18355 = ApiError(code="18355", message="unable to marshal request body")
ERROR_18356 = ApiError(
    code="18356",
    message="invalid request body: size of the request body must be less than [%d]MB",
)
ERROR_18401 = ApiError(code="18401", message="invalid request body")
ERROR_18402 = ApiError(code="18402", message="plugins already configured")
ERROR_18404 = ApiError(code="18404", message="plugins not found")
ERROR_18406 = ApiError(code="18406", message="plugins config not found")
ERROR_18408 = ApiError(code="18408", message="invalid request body")
ERROR_18409 = ApiError(code="18409", message="plugins config not found")
ERROR_18502 = ApiError(code="18502", message="unable to list tags")
ERROR_18503 = ApiError(code="18503", message="unable to list tags")
ERROR_18505 = ApiError(code="18505", message="invalid request body")
ERROR_18506 = ApiError(code="18506", message="tag already exists")
ERROR_18507 = ApiError(code="18507", message="unable to create tag")
ERROR_18509 = ApiError(code="18509", message="unable to delete tag")
ERROR_18510 = ApiError(code="18510", message="tag not found")
ERROR_20000 = ApiError(code="20000", message="internal server error")
ERROR_20001 = ApiError(code="20001", message="unauthorized access")
ERROR_20002 = ApiError(code="20002", message="validation error")
ERROR_20013 = ApiError(code="20013", message="insufficient permission")

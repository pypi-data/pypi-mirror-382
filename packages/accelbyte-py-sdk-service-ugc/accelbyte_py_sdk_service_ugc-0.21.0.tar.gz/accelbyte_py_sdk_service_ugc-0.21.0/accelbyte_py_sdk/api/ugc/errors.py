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

# AccelByte Gaming Services Ugc Service

from accelbyte_py_sdk.core import ApiError

ERROR_20001 = ApiError(code="20001", message="unauthorized access")
ERROR_20013 = ApiError(code="20013", message="insufficient permission")
ERROR_770100 = ApiError(
    code="770100", message="Malformed request/Invalid request body/channel do not exist"
)
ERROR_770102 = ApiError(
    code="770102",
    message="Unable to check user ban status/Unable to save ugc content: unable to get channel",
)
ERROR_770103 = ApiError(
    code="770103", message="Unable to save ugc content: shareCode exceed the limit"
)
ERROR_770104 = ApiError(code="770104", message="User has been banned to create content")
ERROR_770105 = ApiError(
    code="770105", message="Unable to save ugc content: failed generate upload URL"
)
ERROR_770106 = ApiError(code="770106", message="channel doesn't exist")
ERROR_770107 = ApiError(
    code="770107", message="Unable to update ugc content: invalid shareCode format"
)
ERROR_770200 = ApiError(code="770200", message="Content not found")
ERROR_770300 = ApiError(code="770300", message="ugc content not found")
ERROR_770301 = ApiError(
    code="770301", message="Unable to get ugc content/Unable to get creator"
)
ERROR_770303 = ApiError(code="770303", message="Failed generate download URL")
ERROR_770500 = ApiError(code="770500", message="Invalid request body")
ERROR_770502 = ApiError(code="770502", message="Unable to save channel")
ERROR_770503 = ApiError(
    code="770503", message="Invalid channel {ID}: should uuid without hypen"
)
ERROR_770504 = ApiError(code="770504", message="Channel already exist")
ERROR_770600 = ApiError(code="770600", message="Invalid request body")
ERROR_770602 = ApiError(code="770602", message="Unable to save channel")
ERROR_770603 = ApiError(code="770603", message="Channel was not found")
ERROR_770700 = ApiError(code="770700", message="Unable get user channels")
ERROR_770702 = ApiError(code="770702", message="invalid paging parameter")
ERROR_770800 = ApiError(
    code="770800",
    message="invalid paging parameter/max allowed number of tags is {maxTags}/invalid official parameter/invalid ishidden parameter",
)
ERROR_770801 = ApiError(
    code="770801", message="Unable to get ugc content: database/Unable to get creator"
)
ERROR_770803 = ApiError(code="770803", message="Failed generate download URL")
ERROR_770804 = ApiError(code="770804", message="invalid paging parameter")
ERROR_770805 = ApiError(
    code="770805", message="Unable to get ugc content: database error"
)
ERROR_770900 = ApiError(code="770900", message="invalid paging parameter")
ERROR_770901 = ApiError(
    code="770901",
    message="Unable to get ugc content: database error/Unable to get creator",
)
ERROR_770903 = ApiError(code="770903", message="Failed generate download URL")
ERROR_771000 = ApiError(
    code="771000",
    message="Malformed request/Content not found/Unable to update like status: content not found",
)
ERROR_771001 = ApiError(
    code="771001",
    message="unable to like content/Unable to update like status: database error",
)
ERROR_771003 = ApiError(
    code="771003", message="Unable to like content: too many request"
)
ERROR_771004 = ApiError(code="771004", message="invalid paging parameter")
ERROR_771006 = ApiError(
    code="771006", message="unable to get list of content like: database error"
)
ERROR_771100 = ApiError(code="771100", message="unable to parse isofficial param")
ERROR_771101 = ApiError(
    code="771101", message="Unable to get ugc content: database error"
)
ERROR_771103 = ApiError(code="771103", message="Unable to get total liked content")
ERROR_771200 = ApiError(code="771200", message="Malformed request")
ERROR_771201 = ApiError(
    code="771201", message="Unable to update follow status: database error"
)
ERROR_771300 = ApiError(code="771300", message="Unable to get creators: database error")
ERROR_771303 = ApiError(code="771303", message="Unable to get creators: database error")
ERROR_771304 = ApiError(code="771304", message="invalid paging parameter")
ERROR_771310 = ApiError(
    code="771310", message="Unable to get ugc content: database error"
)
ERROR_771311 = ApiError(code="771311", message="invalid paging parameter")
ERROR_771401 = ApiError(code="771401", message="Malformed request/Invalid request body")
ERROR_771402 = ApiError(code="771402", message="Unable to save ugc tag")
ERROR_771403 = ApiError(code="771403", message="Conflicted resource indentifier")
ERROR_771501 = ApiError(code="771501", message="invalid paging parameter")
ERROR_771502 = ApiError(code="771502", message="Unable get user tags")
ERROR_771601 = ApiError(code="771601", message="Creator not found")
ERROR_771701 = ApiError(code="771701", message="Malformed request/Invalid request body")
ERROR_771702 = ApiError(code="771702", message="Unable to save ugc type")
ERROR_771703 = ApiError(code="771703", message="Conflicted resource indentifier")
ERROR_771801 = ApiError(code="771801", message="invalid paging parameter")
ERROR_771802 = ApiError(code="771802", message="Unable get types")
ERROR_771901 = ApiError(code="771901", message="Malformed request/Invalid request body")
ERROR_771902 = ApiError(code="771902", message="Unable update types")
ERROR_771903 = ApiError(code="771903", message="Type not found")
ERROR_771904 = ApiError(code="771904", message="Proposed Type already exist")
ERROR_772002 = ApiError(code="772002", message="Unable delete tag")
ERROR_772003 = ApiError(code="772003", message="Tag not found")
ERROR_772004 = ApiError(code="772004", message="Unable delete type")
ERROR_772005 = ApiError(code="772005", message="Type not found")
ERROR_772101 = ApiError(code="772101", message="Malformed request/Invalid request body")
ERROR_772102 = ApiError(code="772102", message="Unable to create group")
ERROR_772201 = ApiError(code="772201", message="Malformed request/Invalid request body")
ERROR_772202 = ApiError(code="772202", message="Unable to update group")
ERROR_772203 = ApiError(code="772203", message="Group not found")
ERROR_772301 = ApiError(code="772301", message="invalid paging parameter")
ERROR_772302 = ApiError(code="772302", message="Unable get groups")
ERROR_772402 = ApiError(code="772402", message="Unable delete groups")
ERROR_772403 = ApiError(code="772403", message="Group not found")
ERROR_772501 = ApiError(code="772501", message="Unable to delete channel")
ERROR_772502 = ApiError(code="772502", message="Channel not found")
ERROR_772601 = ApiError(code="772601", message="Malformed request")
ERROR_772602 = ApiError(
    code="772602",
    message="Unable to check user ban status/Unable to get updated ugc content",
)
ERROR_772603 = ApiError(code="772603", message="Content not found")
ERROR_772604 = ApiError(code="772604", message="User has been banned to update content")
ERROR_772605 = ApiError(
    code="772605", message="Unable to save ugc content: failed generate upload URL"
)
ERROR_772606 = ApiError(code="772606", message="Share code already used")
ERROR_772607 = ApiError(
    code="772607", message="Unable to update ugc content: invalid shareCode format"
)
ERROR_772701 = ApiError(
    code="772701",
    message="Unable to delete content/Unable to update user liked count/Unable to delete like state/Unable to delete like state",
)
ERROR_772702 = ApiError(code="772702", message="Content not found")
ERROR_772801 = ApiError(code="772801", message="Malformed request/Invalid request body")
ERROR_772802 = ApiError(code="772802", message="Unable update tags")
ERROR_772803 = ApiError(code="772803", message="Tag not found")
ERROR_772804 = ApiError(code="772804", message="Proposed Tag already exist")
ERROR_772902 = ApiError(
    code="772902", message="Unable to add content download: database error"
)
ERROR_772903 = ApiError(
    code="772903", message="Unable to add content download: content not found"
)
ERROR_772904 = ApiError(
    code="772904", message="Unable to list content downloader: database error"
)
ERROR_772906 = ApiError(
    code="772906", message="Unable to add content download: too many request"
)
ERROR_773001 = ApiError(code="773001", message="Unable get group")
ERROR_773002 = ApiError(code="773002", message="Group not found")
ERROR_773101 = ApiError(code="773101", message="invalid paging parameter")
ERROR_773102 = ApiError(
    code="773102", message="Unable to get ugc content: database error"
)
ERROR_773103 = ApiError(code="773103", message="No group content was found")
ERROR_773200 = ApiError(code="773200", message="ugc content not found")
ERROR_773201 = ApiError(
    code="773201",
    message="Unable to get ugc content/Unable to get creator/Unable to get included group",
)
ERROR_773203 = ApiError(code="773203", message="Failed generate download URL")
ERROR_773301 = ApiError(code="773301", message="Unable to find all user group")
ERROR_773302 = ApiError(code="773302", message="Groups not found")
ERROR_773401 = ApiError(code="773401", message="Unable to get all user content")
ERROR_773402 = ApiError(code="773402", message="Content not found")
ERROR_773501 = ApiError(code="773501", message="Unable to delete channel")
ERROR_773502 = ApiError(code="773502", message="Channel not found")
ERROR_773601 = ApiError(
    code="773601",
    message="Unable to get all user contents/Unable to delete user states",
)
ERROR_773602 = ApiError(
    code="773602", message="user states are not found: content not found"
)
ERROR_773701 = ApiError(code="773701", message="Unable to get ugc content")
ERROR_773702 = ApiError(code="773702", message="ugc content not found")
ERROR_773801 = ApiError(code="773801", message="Invalid request body/Malformed request")
ERROR_773802 = ApiError(
    code="773802", message="Unable to update hide status: database error"
)
ERROR_773803 = ApiError(
    code="773803", message="Unable to update hide status: content not found"
)
ERROR_773804 = ApiError(
    code="773804", message="Unable to save ugc content: failed generate upload URL"
)
ERROR_773805 = ApiError(
    code="773805",
    message="Unable to save ugc content preview: failed generate upload URL",
)
ERROR_773900 = ApiError(code="773900", message="Malformed request/Invalid request body")
ERROR_773901 = ApiError(
    code="773901", message="Unable to get ugc content: database/Unable to get creator"
)
ERROR_773902 = ApiError(code="773902", message="Failed generate download URL")
ERROR_774001 = ApiError(
    code="774001", message="unable to read response body/unable to update file location"
)
ERROR_774002 = ApiError(
    code="774002", message="unable to update content file location: content not found"
)
ERROR_774003 = ApiError(code="774003", message="unable to update content file location")
ERROR_774004 = ApiError(code="774004", message="ugc content not found")
ERROR_774005 = ApiError(code="774005", message="unable to get ugc content")
ERROR_774101 = ApiError(code="774101", message="ugc content not found")
ERROR_774102 = ApiError(code="774102", message="version not found")
ERROR_774103 = ApiError(
    code="774103",
    message="unable to get ugc content/content cannot be restored using the current content version",
)
ERROR_774201 = ApiError(code="774201", message="Invalid request body")
ERROR_774202 = ApiError(code="774202", message="Unable to save config")
ERROR_774204 = ApiError(code="774204", message="invalid paging parameter")
ERROR_774205 = ApiError(code="774205", message="Unable to get configs")
ERROR_774301 = ApiError(code="774301", message="invalid paging parameter")
ERROR_774302 = ApiError(code="774302", message="unable to get staging content")
ERROR_774303 = ApiError(code="774303", message="unable to generate presigned URL")
ERROR_774401 = ApiError(code="774401", message="staging content not found")
ERROR_774402 = ApiError(code="774402", message="unable to get staging content")
ERROR_774403 = ApiError(code="774403", message="unable to generate presigned URL")
ERROR_774405 = ApiError(code="774405", message="Invalid request body")
ERROR_774406 = ApiError(code="774406", message="staging content not found")
ERROR_774407 = ApiError(code="774407", message="unable to approve staging content")
ERROR_774408 = ApiError(
    code="774408", message="nable to save ugc content: shareCode exceed the limit"
)
ERROR_774411 = ApiError(code="774411", message="Invalid request body")
ERROR_774412 = ApiError(code="774412", message="user has been banned to update content")
ERROR_774413 = ApiError(code="774413", message="staging content not found")
ERROR_774414 = ApiError(code="774414", message="unable to update staging content")
ERROR_774415 = ApiError(code="774415", message="unable to generate presigned URL")
ERROR_774417 = ApiError(code="774417", message="staging content not found")
ERROR_774418 = ApiError(code="774418", message="unable to delete staging content")

# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, List, Union, Optional

from pydantic import Field as FieldInfo

from .._models import BaseModel

__all__ = ["SettingGetResponse"]


class SettingGetResponse(BaseModel):
    chunk_size: Optional[int] = FieldInfo(alias="chunkSize", default=None)

    exclude_items: Union[str, float, bool, Dict[str, object], List[object], None] = FieldInfo(
        alias="excludeItems", default=None
    )

    filter_prompt: Optional[str] = FieldInfo(alias="filterPrompt", default=None)

    google_drive_client_id: Optional[str] = FieldInfo(alias="googleDriveClientId", default=None)

    google_drive_client_secret: Optional[str] = FieldInfo(alias="googleDriveClientSecret", default=None)

    google_drive_custom_key_enabled: Optional[bool] = FieldInfo(alias="googleDriveCustomKeyEnabled", default=None)

    include_items: Union[str, float, bool, Dict[str, object], List[object], None] = FieldInfo(
        alias="includeItems", default=None
    )

    notion_client_id: Optional[str] = FieldInfo(alias="notionClientId", default=None)

    notion_client_secret: Optional[str] = FieldInfo(alias="notionClientSecret", default=None)

    notion_custom_key_enabled: Optional[bool] = FieldInfo(alias="notionCustomKeyEnabled", default=None)

    onedrive_client_id: Optional[str] = FieldInfo(alias="onedriveClientId", default=None)

    onedrive_client_secret: Optional[str] = FieldInfo(alias="onedriveClientSecret", default=None)

    onedrive_custom_key_enabled: Optional[bool] = FieldInfo(alias="onedriveCustomKeyEnabled", default=None)

    should_llm_filter: Optional[bool] = FieldInfo(alias="shouldLLMFilter", default=None)

# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/7/25 21:53
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: message_do.py
import datetime
from typing import Optional

from pydantic import BaseModel, Field


class MessageDO(BaseModel):
    id: Optional[int] = Field(description="ID", default=None)
    session_id: str = Field(description="Session id")
    ext_info: Optional[dict] = Field(description="Message ext info.", default={})
    content: Optional[str] = Field(description="Message content", default='')
    gmt_created: Optional[datetime.datetime] = Field(
        description="Create time", default_factory=datetime.datetime.now)
    gmt_modified: Optional[datetime.datetime] = Field(
        description="Modified time", default_factory=datetime.datetime.now)

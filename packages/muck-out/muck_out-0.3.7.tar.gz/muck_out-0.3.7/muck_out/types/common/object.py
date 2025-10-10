from datetime import datetime
from pydantic import BaseModel, Field

from muck_out.validators import HtmlStringOrNone, IdFieldOrNone


class CommonObject(BaseModel):
    updated: datetime | None = Field(
        default=None,
        description="Moment of this object being updated",
    )
    summary: HtmlStringOrNone = Field(
        default=None,
        description="The summary of the object",
    )
    name: HtmlStringOrNone = Field(
        default=None,
        description="The name of the object",
    )
    inReplyTo: IdFieldOrNone = Field(
        None,
        description="The object being replied to. Currently a string. Not sure if this is what I want.",
    )
    context: IdFieldOrNone = Field(None, description="The context of the object")

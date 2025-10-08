from typing import Any
from pydantic import Field
from .common import Common


class Object(Common):
    attributed_to: str = Field(
        examples=["https://actor.example/"],
        description="id of the actor that authored this object",
        alias="attributedTo",
    )
    content: str = Field(description="The content of the object")

    summary: str | None = Field(
        None,
        description="The summary of the object",
    )
    name: str | None = Field(
        None,
        description="The name of the object",
    )
    attachment: list[dict[str, Any]] | None = Field(
        None,
        description="A list of objects that are attached to the original object",
    )
    tag: list[dict[str, Any]] | None = Field(
        None,
        description="A list of objects that expand on the content of the object",
    )
    url: list[dict[str, Any] | str] | None = Field(
        None,
        description="A list of urls that expand on the content of the object",
    )
    sensitive: bool | None = Field(
        None,
        description="""
    Marks the object as sensitive. Currently, used by everyone, a better way would be an element of the tag list that labels the object as sensitive due a reason
    """,
    )
    in_reply_to: str | None = Field(
        None,
        description="The object being replied to. Currently a string. Not sure if this is what I want.",
        alias="inReplyTo",
    )
    context: str | None = Field(None, description="The context of the object")

from pydantic import Field, BeforeValidator
from typing import Any, Annotated


from muck_out.validators import HtmlStringOrNone, IdFieldOrNone, UrlList
from muck_out.transform.attachment import transform_attachments

from .common import Common


class ObjectStub(Common):
    """Stub object"""

    attributedTo: IdFieldOrNone = Field(
        default=None,
        examples=["https://actor.example/"],
        description="id of the actor that authored this object",
    )
    content: HtmlStringOrNone = Field(
        default=None, description="The content of the object"
    )
    summary: HtmlStringOrNone = Field(
        default=None,
        description="The summary of the object",
    )
    name: HtmlStringOrNone = Field(
        default=None,
        description="The name of the object",
    )
    attachment: Annotated[
        list[dict[str, Any]], BeforeValidator(transform_attachments)
    ] = Field(
        default=[],
        description="A list of objects that are attached to the original object",
    )
    tag: Annotated[list[dict[str, Any]], BeforeValidator(transform_attachments)] = (
        Field(
            default=[],
            description="A list of objects that expand on the content of the object",
        )
    )
    url: UrlList = Field(
        default=[],
        description="A list of urls that expand on the content of the object",
    )
    sensitive: bool | None = Field(
        None,
        description="Marks the object as sensitive. Currently, used by everyone, a better way would be an element of the tag list that labels the object as sensitive due a reason",
    )
    inReplyTo: IdFieldOrNone = Field(
        None,
        description="The object being replied to. Currently a string. Not sure if this is what I want.",
    )
    context: IdFieldOrNone = Field(None, description="The context of the object")

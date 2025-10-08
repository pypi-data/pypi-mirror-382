from pydantic import BaseModel, ConfigDict, Field

from muck_out.validators import HtmlStringOrNone


class ActorHeaderInfo(BaseModel):
    """Derived information suitable to be displayed in a header line."""

    model_config = ConfigDict(
        serialize_by_alias=True,
        extra="forbid",
        field_title_generator=lambda field_name, field_info: "",
    )

    id: str = Field(
        examples=["https://actor.example/alice/some/id"],
        description="id of the actor, can be assumed to be globally unique. Some activities such as a Follow request will require an id to be valid. Servers may assume an id to be required. As assigning an id is 'trivial', one should assign one.",
    )

    avatar_url: str | None = Field(
        default=None,
        examples=["https://actor.example/static/alice-avatar.png"],
        description="The url of the avatar to use for the actor",
        serialization_alias="avatarUrl",
    )

    name: HtmlStringOrNone = Field(
        default=None,
        examples=["Alice"],
        description="Display name of the actor",
    )

    identifier: str = Field(
        examples=["acct:alice@actor.example"],
        description="Identifier to display for the actor",
    )

    html_url: str | None = Field(
        default=None,
        examples=["https://actor.example/@alice"],
        description="Location of a html representation of the actor",
        serialization_alias="htmlUrl",
    )

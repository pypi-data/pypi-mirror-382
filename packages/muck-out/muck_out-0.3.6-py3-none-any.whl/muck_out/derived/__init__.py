from muck_out.types import Actor
from .types import ActorHeaderInfo

__all__ = ["ActorHeaderInfo", "actor_to_header_info"]


def actor_to_header_info(actor: Actor) -> ActorHeaderInfo:
    """Turns an [Actor][muck_out.types.Actor] object into a reduced version
    suitable to display in a header lien for this actor.

    ```python
    >>> from muck_out.testing.examples import actor
    >>> result = actor_to_header_info(actor)
    >>> print(result.model_dump_json(indent=2))
    {
      "id": "http://abel/actor/AFKb0cQunSBv1fC7sWbQYg",
      "avatarUrl": "https://dev.bovine.social/assets/bull-horns.png",
      "name": "The kitty",
      "identifier": "acct:kitty@abel",
      "htmlUrl": "http://abel/@kitty"
    }

    ```
    """
    avatar_url = actor.icon.get("url") if actor.icon else None

    html_url = None
    for url in actor.url:
        if url.get("mediaType") == "text/html":
            html_url = url.get("href")
            if html_url:
                break
    if not html_url and len(actor.url) > 0:
        html_url = actor.url[0].get("href")

    return ActorHeaderInfo(
        id=actor.id,
        name=actor.name,
        identifier=actor.identifiers[0],
        avatar_url=avatar_url,
        html_url=html_url,
    )

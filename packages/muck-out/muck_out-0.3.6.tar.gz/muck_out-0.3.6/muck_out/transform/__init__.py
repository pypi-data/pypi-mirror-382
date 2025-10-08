from bovine.activitystreams.utils import id_for_object

from .list_utils import transform_to_list


def transform_url_part(url_part):
    if isinstance(url_part, str):
        url_part = {"type": "Link", "href": url_part}
    return url_part


def transform_url(url) -> list[dict] | None:
    """Transform to a list of links

    ```python
    >>> transform_url("http://remote.test/html")
    [{'type': 'Link', 'href': 'http://remote.test/html'}]

    ```
    """
    url_list = transform_to_list(url)

    return [transform_url_part(url_part) for url_part in url_list]


def transform_to_list_of_uris(data) -> list[str]:
    """Transforms to a list of URIs. As this simplifies a
    complicated data structure, some information may be lost.

    ``` python
    >>> transform_to_list_of_uris("http://remote.test/id")
    ['http://remote.test/id']

    >>> transform_to_list_of_uris({"id": "http://remote.test/id"})
    ['http://remote.test/id']

    >>> transform_to_list_of_uris({"ignored": True})
    []

    ```
    """
    to_list = transform_to_list(data)

    return [x for x in (id_for_object(to) for to in to_list) if x]

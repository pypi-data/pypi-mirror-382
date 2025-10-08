import pytest

from muck_out.process import normalize_object
from muck_out.types import ObjectStub


@pytest.fixture
def sample_object():
    return {
        "@context": [
            "https://www.w3.org/ns/activitystreams",
            {"toot": "http://joinmastodon.org/ns#", "Emoji": "toot:Emoji"},
        ],
        "id": "https://activitypub.space/post/99",
        "type": "Article",
        "to": [
            "https://www.w3.org/ns/activitystreams#Public",
            "https://activitypub.space/category/5",
        ],
        "cc": [
            "https://activitypub.space/uid/1/followers",
            "https://piefed.social/u/rimu",
            "https://community.nodebb.org/uid/2",
            "https://indieweb.social/users/phillycodehound",
            "https://mitra.social/users/silverpill",
            "https://community.nodebb.org/uid/2/followers",
            "https://indieweb.social/users/phillycodehound/followers",
            "https://mitra.social/users/silverpill/followers",
        ],
        "inReplyTo": None,
        "published": "2025-09-06T20:09:12.263Z",
        "updated": None,
        "url": "https://activitypub.space/post/99",
        "attributedTo": "https://activitypub.space/uid/1",
        "context": "https://activitypub.space/topic/18",
        "audience": "https://activitypub.space/category/5",
        "summary": " <p>Hey <a href=\"https://piefed.social/u/rimu\">@<bdi>rimu@piefed.social</bdi></a> question to you about post removal...</p> <p>If a remote user posts to a local community, and the local mod deletes it (let's say it's spam of off topic), does the local community federate a delete out?</p> <p>Technically you're not <strong>deleting</strong> the content, just removing it from the community.</p> <p>Is there a different action Piefed takes?</p>",
        "name": "Topic removal from a category/community",
        "preview": {
            "type": "Note",
            "attributedTo": "https://activitypub.space/uid/1",
            "content": "<p>Hey <a href=\"https://piefed.social/u/rimu\">@<bdi>rimu@piefed.social</bdi></a> question to you about post removal...</p>\n<p>If a remote user posts to a local community, and the local mod deletes it (let's say it's spam of off topic), does the local community federate a delete out?</p>\n<p>Technically you're not <strong>deleting</strong> the content, just removing it from the community.</p>\n<p>Is there a different action Piefed takes?</p>\n",
            "published": "2025-09-06T20:09:12.263Z",
            "attachment": [],
        },
        "content": "<p>Hey <a href=\"https://piefed.social/u/rimu\">@<bdi>rimu@piefed.social</bdi></a> question to you about post removal...</p>\n<p>If a remote user posts to a local community, and the local mod deletes it (let's say it's spam of off topic), does the local community federate a delete out?</p>\n<p>Technically you're not <strong>deleting</strong> the content, just removing it from the community.</p>\n<p>Is there a different action Piefed takes?</p>\n",
        "source": {
            "content": "Hey [rimu@piefed.social](https://activitypub.space/user/rimu%40piefed.social) question to you about post removal...\n\nIf a remote user posts to a local community, and the local mod deletes it (let's say it's spam of off topic), does the local community federate a delete out?\n\nTechnically you're not **deleting** the content, just removing it from the community.\n\nIs there a different action Piefed takes?",
            "mediaType": "text/markdown",
        },
        "tag": [
            {
                "type": "Hashtag",
                "href": "https://activitypub.space/tags/piefed",
                "name": "#piefed",
            },
            {
                "type": "Mention",
                "href": "https://piefed.social/u/rimu",
                "name": "@rimu@piefed.social",
            },
        ],
        "attachment": [],
        "replies": "https://activitypub.space/post/99/replies",
    }


def test_normalize_object(sample_object):
    result = normalize_object(sample_object)

    assert result.id == sample_object["id"]
    assert result.context == sample_object["context"]


def test_object_stub(sample_object):
    result = ObjectStub.model_validate(sample_object)

    assert result.id == sample_object["id"]
    assert result.context == sample_object["context"]

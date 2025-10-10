from muck_out.process import normalize_actor

actor_example = {
    "attachment": [
        {
            "type": "PropertyValue",
            "name": "Author",
            "value": "acct:helge@mymath.rocks",
        },
        {
            "type": "PropertyValue",
            "name": "Source",
            "value": "https://codeberg.org/bovine/roboherd",
        },
        {"type": "PropertyValue", "name": "Frequency", "value": "Every minute"},
    ],
    "published": "2025-09-17T17:02:51.088028",
    "@context": [
        "https://www.w3.org/ns/activitystreams",
        "https://w3id.org/security/v1",
        {
            "PropertyValue": {
                "@id": "https://schema.org/PropertyValue",
                "@context": {
                    "value": "https://schema.org/value",
                    "name": "https://schema.org/name",
                },
            }
        },
    ],
    "publicKey": {
        "id": "http://abel/actor/AFKb0cQunSBv1fC7sWbQYg#legacy-key-1",
        "owner": "http://abel/actor/AFKb0cQunSBv1fC7sWbQYg",
        "publicKeyPem": "-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEArmnl5tRTKzXoHsOmEPwk\nfC6BY1ZtueThLmXF9BjtIiHSKXvH0cema16EMb6efyHoLBvlAcdvEpP0QR3AKvb/\n48wArzIUnLi3RxOlANhUK+NHOuNJQxcPrnX06rt0MZ5K+3hK1XZQV559vecEyIk+\nxZxlz9KaSDEnsHKbHueNJvhrGV1TdppdCSe5qcml/Pkc3yIG9gq2aKx7XLIPORHe\nDRqJUpLyUX5XiOOGLHVUuKz3U87+ZWxK+GjHB46hMl+W4clJNLedxY81eGCeGoOV\ni6qEHRuWC68Q1IhexIXyujlBBHAOqgLRO/VNpg6anOZWDX/s6EvsQq4BBPNI3HZe\newIDAQAB\n-----END PUBLIC KEY-----\n",
    },
    "id": "http://abel/actor/AFKb0cQunSBv1fC7sWbQYg",
    "type": "Service",
    "inbox": "http://abel/inbox/3c2TKngdcWGJOj4j3ALC1g",
    "outbox": "http://abel/outbox/vCJcPoNbwkNlJU9o7O8qDA",
    "followers": "http://abel/followers/RKsezXFc1SGvQKvucioJxg",
    "following": "http://abel/following/CLwJywMuHXFIyPEz9sRBhg",
    "preferredUsername": "kitty",
    "name": "The kitty",
    "summary": "I'm a kitty.",
    "icon": {
        "mediaType": "image/png",
        "type": "Image",
        "url": "https://dev.bovine.social/assets/bull-horns.png",
    },
    "identifiers": ["acct:kitty@abel", "http://abel/actor/AFKb0cQunSBv1fC7sWbQYg"],
    "endpoints": {"sharedInbox": "http://abel/shared_inbox"},
    "url": "http://abel/@kitty",
}

actor = normalize_actor(actor_example)


mitra_actor = {
    "@context": [
        "https://www.w3.org/ns/activitystreams",
    ],
    "id": "http://mitra/users/admin",
    "type": "Person",
    "name": None,
    "preferredUsername": "admin",
    "inbox": "http://mitra/users/admin/inbox",
    "outbox": "http://mitra/users/admin/outbox",
    "followers": "http://mitra/users/admin/followers",
    "following": "http://mitra/users/admin/following",
    "subscribers": "http://mitra/users/admin/subscribers",
    "featured": "http://mitra/users/admin/collections/featured",
    "assertionMethod": [
        {
            "id": "http://mitra/users/admin#main-key",
            "type": "Multikey",
            "controller": "http://mitra/users/admin",
            "publicKeyMultibase": "z4MXj1wBzi9jUstyPBJ7qsa7G5waXG8McxXkjvAVHFLMxhGiJTGXK1EWseFfrUaH6Btt7TCSB1Entgg5SyAaHc1Ssh698puSozC41J2no8rgpMVRPzFVBoAYuNamM5FW9qCP1XV2y1cJ2y3gmuoreUVyn1jgW7Gb3NxsEcxjfs3fE1SzXjCnkxqVikYjkByqbXeB4AvYeXP1wjS1KB9xzKAzAjnRrui6RLHi6sCji2f7kdmxALcmjMbLyKjmYozhoG5ZqVkfNNZuAf4PLgyJQ84rDNKUGRgZeCeNh31hLLMUsSFYgpArfp813dbusq3A5BnnWN24rQtrj7nN9gQsxYjSTRhLpQcSLnwCQxJ1Sc2u9zfDwcJdW",
        },
        {
            "id": "http://mitra/users/admin#ed25519-key",
            "type": "Multikey",
            "controller": "http://mitra/users/admin",
            "publicKeyMultibase": "z6Mkgo38JzBJ6pLDyNz6YhnDN3ZXU6GcBWpp2c5dCEXcJtwW",
        },
    ],
    "publicKey": {
        "id": "http://mitra/users/admin#main-key",
        "owner": "http://mitra/users/admin",
        "publicKeyPem": "-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAqh38rZnS2RDft6RAGt5O\np4teGYSYmaeB2l5UGRCpnzcVf3m4v/x6LpXJXG8bDkNNnIZ/OzZ8tNPzKZJ6sKpI\nngayjowI/YzN8BBPJuKtaB3B4ImNrvG865OQl0h+TtfXaNTRWK8U108bMW2HH2/n\nTWJiaYiCcxLPzFRPLLd/TG6IYgeSKlRpYJ5TOdpZg1Hcx7/eRljFvdq7wmUcbM2W\nXmUYv1sjmwGQ92VCEy8d0biE/IesHdE6QM/5ALdAcQGtTn5QK7AEe43VmklkTfV+\nqDs38r3kVAMuHxnpASj+nuMp7Y7dRm92aKJ1vj93HxXTE1Ajh2eQYk8ulHQjcLky\nGwIDAQAB\n-----END PUBLIC KEY-----\n",
    },
    "generator": {
        "type": "Application",
        "implements": [
            {
                "name": "RFC-9421: HTTP Message Signatures",
                "href": "https://datatracker.ietf.org/doc/html/rfc9421",
            },
            {
                "name": "RFC-9421 signatures using the Ed25519 algorithm",
                "href": "https://datatracker.ietf.org/doc/html/rfc9421#name-eddsa-using-curve-edwards25",
            },
        ],
    },
    "manuallyApprovesFollowers": False,
    "url": "http://mitra/users/admin",
    "published": "2025-09-11T13:34:15.718558Z",
    "updated": "2025-09-11T13:34:15.718558Z",
}

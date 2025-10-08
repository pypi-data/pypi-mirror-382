import string

import jwt
import pytest
from faker import Faker


@pytest.fixture
def raw_jwt_payload(faker: Faker) -> dict[str, object]:
    user_name = "".join(faker.random_sample(elements=string.ascii_lowercase, length=3))
    email = f"{user_name}@ssb.no"
    first_name = faker.first_name()
    last_name = faker.last_name()
    return {
        "exp": faker.unix_time(),
        "iat": faker.unix_time(),
        "auth_time": faker.unix_time(),
        "jti": faker.uuid4(),
        "iss": faker.url(),
        "aud": [
            faker.word(),
            faker.uuid4(),
            "broker",
            "account",
        ],
        "sub": faker.uuid4(),
        "typ": "Bearer",
        "azp": "onyxia",
        "session_state": faker.uuid4(),
        "allowed-origins": ["*"],
        "realm_access": {
            "roles": [faker.word(), faker.word()],
        },
        "resource_access": {
            "broker": {"roles": [faker.word()]},
            "account": {
                "roles": [faker.word()],
            },
        },
        "scope": "openid email profile",
        "sid": faker.uuid4(),
        "email_verified": True,
        "name": f"{first_name} {last_name}",
        "short_username": f"ssb-{user_name}",
        "preferred_username": email,
        "given_name": first_name,
        "family_name": last_name,
        "email": email,
    }


@pytest.fixture
def fake_jwt(raw_jwt_payload):
    return jwt.encode(raw_jwt_payload, "test secret", algorithm="HS256")

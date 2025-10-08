import os
import json
import base64
import pytest
import uuid
import bode_logger

@pytest.fixture
def url():
    deploy_url = os.environ["DEPLOY_URL"]
    if not deploy_url.startswith("http"):
        raise ValueError(f"incorrect deploy url value '{deploy_url}' does not start with http ")
    return deploy_url


@pytest.fixture(scope="function")
def request_headers(request) -> dict[str, str]:
    test_id = request.node.nodeid.replace("/", ".").replace(".py", "")
    headers = {
        "X-Test-Id": test_id,
        "X-Session-Id": os.environ["SESSION_ID"],
    }
    if os.environ["CLOUD"] == "true":
        id_token = os.environ["IDTOKEN"]
        auth_header = {"Authorization": f"Bearer {id_token}"}
        headers = {**headers, **auth_header}
    return headers


def generate_request_id_header() -> dict[str, str]:
    return {"X-Request-Id": str(uuid.uuid4()).replace("-", "")[:8]}


def generate_admin_header() -> dict[str, bytes]:
    admin_encoded = base64.urlsafe_b64encode(json.dumps({"admin": True, "tenant": os.environ["TENANTID"]}).encode())
    firebase_auth_header = {"X-Endpoint-Api-Userinfo": admin_encoded}
    return firebase_auth_header


def generate_user_header() -> dict[str, bytes]:
    user_encoded = base64.urlsafe_b64encode(json.dumps({"user": True, "tenant": os.environ["TENANTID"]}).encode())
    firebase_auth_header = {"X-Endpoint-Api-Userinfo": user_encoded}
    return firebase_auth_header

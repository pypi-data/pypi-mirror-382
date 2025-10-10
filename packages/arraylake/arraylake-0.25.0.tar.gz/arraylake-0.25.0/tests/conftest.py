import json
import os
import pathlib
import random
import secrets
import shutil
import string
import time
from collections.abc import AsyncGenerator, Iterable
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Literal
from unittest import mock
from uuid import UUID, uuid4

import pytest
import yaml

from arraylake import AsyncClient, config
from arraylake.api_utils import ArraylakeHttpClient
from arraylake.token import TokenHandler
from arraylake.types import (
    ApiTokenInfo,
    Author,
    AuthProviderConfig,
    BucketPrefix,
    BucketResponse,
    NewBucket,
    NewRepoOperationStatus,
    OauthTokens,
    OrgName,
    RepoOperationMode,
    UserInfo,
)


# Configured not to run slow tests by default
# https://stackoverflow.com/questions/52246154/python-using-pytest-to-skip-test-unless-specified
def pytest_configure(config):
    config.addinivalue_line("markers", "runslow: run slow tests")


def pytest_addoption(parser):
    parser.addoption("--runslow", action="store_true", default=False, help="run slow tests")


def pytest_collection_modifyitems(config, items):
    if config.getoption("--runslow"):
        # --runslow given in cli: do not skip slow tests
        return
    skip_slow = pytest.mark.skip(reason="need --runslow option to run")
    for item in items:
        if "slow" in item.keywords:
            item.add_marker(skip_slow)


@pytest.fixture()
def temp_config_file(tmp_path):
    template_file = pathlib.Path(__file__).resolve().parent / "config.yaml"
    test_file = tmp_path / "config.yaml"
    shutil.copy(template_file, test_file)
    return test_file


@pytest.fixture(autouse=True)
def clean_config():
    template_file = pathlib.Path(__file__).resolve().parent / "config.yaml"
    with template_file.open() as f:
        c = yaml.safe_load(f)
    config.update(c)


@pytest.fixture(scope="function", autouse=True)  # perhaps autouse is too aggressive here?
def test_token_file(tmp_path):
    contents = {
        "access_token": "access-123",
        "id_token": "id-456",
        "refresh_token": "refresh-789",
        "expires_in": 86400,
        "token_type": "Bearer",
    }
    fname = tmp_path / "token.json"

    with fname.open(mode="w") as f:
        json.dump(contents, f)

    with config.set({"service.token_path": str(fname)}):
        yield fname


@pytest.fixture(scope="function")
def test_user():
    return UserInfo(
        id=uuid4(),
        sub=UUID("aeeb8bfa-e8f4-4724-9427-c3d5af66190e"),
        email="abc@earthmover.io",
        first_name="TestFirst",
        family_name="TestFamily",
    )


@pytest.fixture(scope="function")
def test_api_token():
    id = uuid4()
    email = "svc-email@some-earthmover-org.service.earthmover.io"
    return ApiTokenInfo(id=id, client_id=id.hex, email=email, expiration=int(time.time() + 10000))


@pytest.fixture()
def test_token():
    return "ema_token-123456789"


@pytest.fixture(
    params=["machine", "user"],
)
def token(request, test_token, test_token_file):
    if request.param == "machine":
        return test_token
    else:
        return None


def get_platforms_to_test(request):
    platforms = ("s3",)
    mark = request.node.get_closest_marker("add_object_store")
    if mark is not None:
        platforms += mark.args
    return platforms


@pytest.fixture(params=["s3", "gs"], scope="session")
def object_store_platform(request) -> Literal["s3", "gs"]:
    return request.param


@pytest.fixture(scope="session")
def object_store_config(object_store_platform):
    if object_store_platform == "s3":
        config_params = {
            "service.uri": "http://0.0.0.0:8000",
            "chunkstore.uri": "s3://testbucket",
            "s3.endpoint_url": "http://localhost:9000",
        }
    elif object_store_platform == "gs":
        config_params = {
            "service.uri": "http://0.0.0.0:8000",
            "chunkstore.uri": "gs://arraylake-test",
            "gs.endpoint_url": "http://127.0.0.1:4443",
            "gs.token": "anon",
            "gs.project": "test",
        }
    return config_params


@pytest.fixture
def client_config(object_store_platform, object_store_config, request):
    if object_store_platform not in get_platforms_to_test(request):
        pytest.skip()
    with config.set(object_store_config):
        yield


@pytest.fixture
def user():
    return Author(name="Test User", email="foo@icechunk.io")


@pytest.fixture(scope="session", autouse=True)
def aws_config():
    credentials_env = {
        "AWS_ACCESS_KEY_ID": "minio123",
        "AWS_SECRET_ACCESS_KEY": "minio123",
    }
    with mock.patch.dict(os.environ, credentials_env):
        yield


@pytest.fixture
async def org_name(client_config, test_token):
    # This fixture should be used by all client-level tests.
    # It makes things more resilient by making sure there are no repos
    # under the specified org and cleaning up any repos that might be left over.
    # But warning: if there are errors in the list / delete logic, they
    # will show up here first!
    org = "my-org"
    async_client = AsyncClient(token=test_token)
    for repo in await async_client.list_repos(org):
        await async_client.delete_repo(f"{org}/{repo.name}", imsure=True, imreallysure=True)
    yield org
    for repo in await async_client.list_repos(org):
        await async_client.delete_repo(f"{org}/{repo.name}", imsure=True, imreallysure=True)


@pytest.fixture
async def isolated_org_name(client_config, test_token):
    # This fixture should be used by all client-level tests.
    # It makes things more resilient by making sure there are no repos
    # under the specified org and cleaning up any repos that might be left over.
    # But warning: if there are errors in the list / delete logic, they
    # will show up here first!
    org_name = "".join(random.choices(string.ascii_uppercase + string.digits, k=8))
    body = {
        "name": org_name,
        "feature_flags": ["v1-write"],
    }
    client = ArraylakeHttpClient("http://localhost:8000", token=test_token)
    resp = await client._request("POST", "/orgs_test_create", content=json.dumps(body))
    assert resp.is_success, f"Failed to create isolated org {org_name}: {resp.status_code} {resp.content}"
    yield org_name

    # TODO shouldn't this delete the org after?


# TODO this doesn't need to be a fixture, it's a pure function
@pytest.fixture
def default_bucket():
    def default_bucket_request_constructor(
        *,
        nickname="test_bucket",
        name="testbucket",
        prefix: BucketPrefix = None,
        platform="minio",
        extra_config={
            "use_ssl": False,
            "endpoint_url": "http://localhost:9000",
        },
        auth_config={"method": "hmac", "access_key_id": "minio123", "secret_access_key": "minio123"},
    ):
        new_bucket_obj = NewBucket(
            nickname=nickname,
            name=name,
            platform=platform,
            extra_config=extra_config,
            auth_config=auth_config,
        )

        if prefix:
            new_bucket_obj.prefix = "prefix"

        return new_bucket_obj

    return default_bucket_request_constructor


@pytest.fixture
def anon_bucket(default_bucket):
    return default_bucket(
        auth_config={"method": "anonymous"},
        nickname="anon_bucket",
        name="name",
        prefix="prefix",
        extra_config={"region_name": "us-west-2"},
    )


@pytest.fixture
def minio_anon_bucket(default_bucket):
    """Anonymous access bucket on local MinIO for testing virtual chunks."""
    return default_bucket(
        auth_config={"method": "anonymous"},
        nickname="minio_anon_bucket",
        name="anonbucket",
        platform="minio",
        extra_config={"use_ssl": False, "endpoint_url": "http://localhost:9000", "region_name": "us-east-1"},
    )


@pytest.fixture
def delegated_creds_bucket(default_bucket):
    return default_bucket(
        nickname="delegated_creds_bucket",
        platform="s3",
        auth_config={
            "method": "aws_customer_managed_role",
            "external_customer_id": "12345678",
            "external_role_name": "my_external_role",
            "shared_secret": "our-shared-secret",
        },
        extra_config={"region_name": "us-west-2"},
    )


@pytest.fixture
async def isolated_org(isolated_org_name):
    """
    Create an isolated org with zero or more buckets.

    Deletes all the buckets after use.
    """

    @asynccontextmanager
    async def org_constructor(*bucket_requests: NewBucket) -> AsyncGenerator[tuple[OrgName, Iterable[NewBucket]], None, None]:
        org_name = isolated_org_name

        # create all the buckets
        client = ArraylakeHttpClient("http://localhost:8000", token=test_token)
        bucket_responses = []

        try:
            for new_bucket_obj in bucket_requests:
                # we cannot use async_client.create_bucket_config because it does not support minio as a platform
                resp = await client._request("POST", f"/orgs/{org_name}/buckets", content=new_bucket_obj.model_dump_json())
                assert resp.is_success, f"Failed to create bucket in isolated org {org_name}: {resp.status_code} {resp.content}"
                bucket_responses.append(resp)

            yield org_name, bucket_requests

        finally:
            # delete all the buckets even if something else went wrong
            for resp in bucket_responses:
                try:
                    bucket_id = BucketResponse.model_validate_json(resp.content).id
                    await client._request("DELETE", f"/orgs/{org_name}/buckets/{bucket_id}")
                except Exception as e:
                    print(f"Error deleting bucket {resp.content['id']} in org {org_name}: {e}")

    return org_constructor


@pytest.fixture
def new_bucket_obj(
    nickname="test_bucket",
    platform="minio",
    name="testbucket",
    extra_config={
        "use_ssl": False,
        "endpoint_url": "http://localhost:9000",
    },
    auth_config={"method": "hmac", "access_key_id": "minio123", "secret_access_key": "minio123"},
):
    return NewBucket(
        org=isolated_org_name,
        nickname=nickname,
        platform=platform,
        name=name,
        extra_config=extra_config,
        auth_config=auth_config,
    )


@pytest.fixture
def new_bucket_obj_with_prefix(new_bucket_obj):
    new_bucket_obj.prefix = "prefix"
    return new_bucket_obj


class Helpers:
    """Helper functions for tests.

    This class is made available to tests using the helpers fixture.
    """

    @staticmethod
    def random_repo_id() -> str:
        return secrets.token_hex(12)  # Generates a 24-character hex string like ObjectId

    @staticmethod
    def an_id(n: int) -> str:
        return "".join(random.choices(string.hexdigits, k=n))

    @staticmethod
    def oauth_tokens_from_file(file: Path) -> OauthTokens:
        """Utility to read an oauth tokens file"""
        with file.open() as f:
            return OauthTokens.model_validate_json(f.read())

    @staticmethod
    async def isolated_org(token, org_config):
        org_name = "".join(random.choices(string.ascii_uppercase + string.digits, k=8))
        org_config["name"] = org_name
        client = ArraylakeHttpClient("http://localhost:8000", token=token)
        resp = await client._request("POST", "/orgs_test_create", content=json.dumps(org_config))
        return org_name

    @staticmethod
    async def set_repo_system_status(token, org_name, repo_name, mode: RepoOperationMode, message: str, is_user_modifiable: bool):
        """Util to set a system status for client tests.

        System statuses and the user modifiable status are not available in the public API.
        """
        client = ArraylakeHttpClient("http://localhost:8000", token=token)
        body = dict(NewRepoOperationStatus(mode=mode, message=message))
        resp = await client._request(
            "POST",
            "/repo_status_system",
            content=json.dumps(body),
            params={"org_name": org_name, "repo_name": repo_name, "is_user_modifiable": is_user_modifiable},
        )


@pytest.fixture(scope="session")
def helpers():
    """Provide the helpers found in the Helpers class"""
    return Helpers


@pytest.fixture
def mock_auth_provider_config():
    mock_config = AuthProviderConfig(client_id="123456789", domain="auth.foo.com")

    with mock.patch.object(TokenHandler, "auth_provider_config", return_value=mock_config, new_callable=mock.PropertyMock):
        yield mock_config


@pytest.fixture
def sync_isolated_org_with_bucket(isolated_org_name, default_bucket, test_token):
    """Sync fixture that creates an org with a bucket for CLI tests."""

    def create_org_with_bucket():
        import asyncio

        async def _create():
            # Create the bucket config
            bucket_config = default_bucket()

            # Use the async isolated_org fixture logic
            client = ArraylakeHttpClient("http://localhost:8000", token=test_token)

            # Create the bucket
            resp = await client._request("POST", f"/orgs/{isolated_org_name}/buckets", content=bucket_config.model_dump_json())
            bucket_response = BucketResponse.model_validate_json(resp.content)

            return isolated_org_name, bucket_response.id

        # Run the async function synchronously
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            org_name, bucket_id = loop.run_until_complete(_create())
            return org_name, bucket_id
        finally:
            loop.close()

    return create_org_with_bucket

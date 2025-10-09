from collections.abc import Callable
from datetime import datetime, timedelta, timezone
from typing import Optional, override

import urllib3
import jwt
from pydantic import BaseModel

from .api import MemberGroupApi, PermissionApi, ResourceApi, RoleApi, TenantApi
from .api_client import ApiClient as ApiClientBase
from .configuration import Configuration
from .rest import RESTResponse

__all__ = [
    'PermissionsClient',
    'AuthenticationOptions'
]


class AuthenticationOptions(BaseModel):
    api_key: str
    client_id: str
    client_secret: str
    scope: Optional[str] = None


class SpaceBlocksAccessTokenProvider:
    _auth_url: str
    _api_key: str
    _client_id: str
    _client_secret: str
    _scope: str
    _access_token: Optional[str]

    def __init__(
            self,
            auth_url: Optional[str],
            api_key: str,
            client_id: str,
            client_secret: str,
            scope: str
    ) -> None:
        self._auth_url = auth_url or 'https://auth.spaceblocks.cloud'
        self._api_key = api_key
        self._client_id = client_id
        self._client_secret = client_secret
        self._scope = scope

        self._access_token = None

    def _get_expiration_date(self) -> datetime:
        token = jwt.decode(self._access_token, options={"verify_signature": False})
        return datetime.fromtimestamp(token['exp'], timezone.utc)

    def _is_token_expired(self) -> bool:
        return self._get_expiration_date() >= datetime.now(timezone.utc) - timedelta(seconds=10)

    def __call__(self) -> str:
        if self._access_token is None or self._is_token_expired():
            data = {
                'client_id': self._client_id,
                'client_secret': self._client_secret,
                'scope': self._scope
            }

            headers = {
                'apiKey': self._api_key
            }

            response = urllib3.request(
                method='POST',
                url=f'{self._auth_url}/token-manager/token',
                json=data,
                headers=headers
            )

            if response.status != 200:
                raise Exception(f'Failed to retrieve Space Blocks access token: {response.data.decode()}')

            self._access_token = response.json()['access_token']
        return self._access_token


class ApiClient(ApiClientBase):
    _access_token_provider: Callable[[], str]
    _api_key: str

    @override
    def __init__(
            self,
            permissions_url: str,
            authentication_url: str,
            authentication_options: AuthenticationOptions,
    ) -> None:
        super().__init__(
            Configuration(host=permissions_url),
            None,
            None,
            None
        )

        self._api_key = authentication_options.api_key
        self._access_token_provider = SpaceBlocksAccessTokenProvider(
            authentication_url,
            **authentication_options.model_dump()
        )

    @override
    def call_api(
            self,
            method,
            url,
            header_params=None,
            body=None,
            post_params=None,
            _request_timeout=None
    ) -> RESTResponse:
        access_token = self._access_token_provider()

        header_params['Authorization'] = f'Bearer {access_token}'
        header_params['apiKey'] = self._api_key

        return super().call_api(
            method,
            url,
            header_params,
            body,
            post_params,
            _request_timeout
        )


class PermissionsClient:
    _api_client: ApiClient
    member_group_api: MemberGroupApi
    permission_api: PermissionApi
    resource_api: ResourceApi
    role_api: RoleApi
    tenant_api: TenantApi

    def __init__(
            self,
            permissions_url: str,
            authentication_options: AuthenticationOptions,
            authentication_url: Optional[str] = None
    ):
        self._api_client = ApiClient(permissions_url, authentication_url, authentication_options)

        self.member_group_api = MemberGroupApi(self._api_client)
        self.permission_api = PermissionApi(self._api_client)
        self.resource_api = ResourceApi(self._api_client)
        self.role_api = RoleApi(self._api_client)
        self.tenant_api = TenantApi(self._api_client)

# Space Blocks Permissions Server SDK for Python

This is the Python server SDK for Space Blocks Permissions.

## Usage

Required Python version: 3.8 or later.

The package is published to the official Python Package Index (https://pypi.org/project/spaceblocks-permissions-server).

It can be installed with:

```bash
pip install spaceblocks-permissions-server
```

To get started, import the package and create an instance of the `PermissionsClient`:

```python
from spaceblocks_permissions_server import (
    PermissionsClient,
    ClientAuthenticationOptions
)

client = PermissionsClient(
    '<SPACE_BLOCKS_PERMISSIONS_URL>',
    ClientAuthenticationOptions(
        api_key='<YOUR_API_KEY>',
        client_id='<YOUR_CLIENT_ID>',
        client_secret='<YOUR_CLIENT_SECRET>'
    )
)

client.permission_api.check_permissions(...)
```

The code above uses a client ID and secret to issue an access token,
but a custom token can also be provided by using the `TokenAuthenticationOptions` instead.
Additionally, the client takes further options via a `SpaceBlocksClientOptions` as the third parameter.

Documentation for the platform and APIs are available here: https://docs.spaceblocks.cloud/permissions

A simple example can be found here: https://github.com/wemogy/spaceblocks-sample-helloworld/tree/main/python

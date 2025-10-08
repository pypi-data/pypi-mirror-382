# Copyright 2025 Q-CTRL. All rights reserved.
#
# Licensed under the Q-CTRL Terms of service (the "License"). Unauthorized
# copying or use of this file, via any medium, is strictly prohibited.
# Proprietary and confidential. You may not use this file except in compliance
# with the License. You may obtain a copy of the License at
#
#    https://q-ctrl.com/terms
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS. See the
# License for the specific language.

from __future__ import annotations

from typing import Optional

from qctrlclient import (
    CliAuth,
    GraphQLClient,
)
from qctrlclient.auth import BaseAuth
from qctrlclient.defaults import (
    get_default_api_url,
    get_default_cli_auth,
)
from qctrlcommons.utils import generate_user_agent

from .utils import get_installed_version


def get_authenticated_client_for_product(
    package_name: str,
    api_url: Optional[str] = None,
    auth: Optional[BaseAuth | str] = None,
) -> GraphQLClient:
    """
    Return a `GraphQLClient` using default URL and Auth (if not provided)
    and check the user has the required access for CLI usage.

    Parameters
    ----------
    package_name : str
        The package name to include in the User-Agent header.
    api_url : str, optional
        The API URL to use. If not provided, the default API URL will be used.
    auth : BaseAuth or str, optional
        The authentication object (or a URL as str to create one) to use.
        If not provided, the default authentication object will be used.
    """

    if isinstance(auth, str):
        auth = CliAuth(auth)

    headers = {
        "User-Agent": generate_user_agent(
            package_name, get_installed_version(package_name)
        ),
    }
    client = GraphQLClient(
        url=api_url or get_default_api_url(),
        headers=headers,
        auth=auth or get_default_cli_auth(),
    )

    return client

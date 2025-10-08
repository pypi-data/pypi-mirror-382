# License: MIT
# Copyright © 2025 Frequenz Energy-as-a-Service GmbH

"""
Assets API client.

This module provides a client for the Assets API.
"""

from __future__ import annotations

from frequenz.api.assets.v1 import assets_pb2, assets_pb2_grpc
from frequenz.client.base import channel
from frequenz.client.base.client import BaseApiClient, call_stub_method

from frequenz.client.assets.electrical_component._electrical_component import (
    ElectricalComponent,
)

from ._microgrid import Microgrid
from ._microgrid_proto import microgrid_from_proto
from .electrical_component._electrical_component_proto import electrical_component_proto
from .exceptions import ClientNotConnected

DEFAULT_GRPC_CALL_TIMEOUT = 60.0
"""The default timeout for gRPC calls made by this client (in seconds)."""


class AssetsApiClient(
    BaseApiClient[assets_pb2_grpc.PlatformAssetsStub]
):  # pylint: disable=too-many-arguments
    """A client for the Assets API."""

    def __init__(
        self,
        server_url: str,
        *,
        auth_key: str | None = None,
        sign_secret: str | None = None,
        channel_defaults: channel.ChannelOptions = channel.ChannelOptions(),
        connect: bool = True,
    ) -> None:
        """
        Initialize the AssetsApiClient.

        Args:
            server_url: The location of the microgrid API server in the form of a URL.
                The following format is expected:
                "grpc://hostname{:`port`}{?ssl=`ssl`}",
                where the `port` should be an int between 0 and 65535 (defaulting to
                9090) and `ssl` should be a boolean (defaulting to `true`).
                For example: `grpc://localhost:1090?ssl=true`.
            auth_key: The authentication key to use for the connection.
            sign_secret: The secret to use for signing requests.
            channel_defaults: The default options use to create the channel when not
                specified in the URL.
            connect: Whether to connect to the server as soon as a client instance is
                created. If `False`, the client will not connect to the server until
                [connect()][frequenz.client.base.client.BaseApiClient.connect] is
                called.
        """
        super().__init__(
            server_url,
            assets_pb2_grpc.PlatformAssetsStub,
            connect=connect,
            channel_defaults=channel_defaults,
            auth_key=auth_key,
            sign_secret=sign_secret,
        )

    @property
    def stub(self) -> assets_pb2_grpc.PlatformAssetsAsyncStub:
        """
        The gRPC stub for the Assets API.

        Returns:
            The gRPC stub for the Assets API.

        Raises:
            ClientNotConnected: If the client is not connected to the server.
        """
        if self._channel is None or self._stub is None:
            raise ClientNotConnected(server_url=self.server_url, operation="stub")
        # This type: ignore is needed because the stub is a sync stub, but we need to
        # use the async stub, so we cast the sync stub to the async stub.
        return self._stub  # type: ignore

    async def get_microgrid(  # noqa: DOC502 (raises ApiClientError indirectly)
        self, microgrid_id: int
    ) -> Microgrid:
        """
        Get the details of a microgrid.

        Args:
            microgrid_id: The ID of the microgrid to get the details of.

        Returns:
            The details of the microgrid.

        Raises:
            ApiClientError: If there are any errors communicating with the Assets API,
                most likely a subclass of [GrpcError][frequenz.client.base.exception.GrpcError].
        """
        response = await call_stub_method(
            self,
            lambda: self.stub.GetMicrogrid(
                assets_pb2.GetMicrogridRequest(microgrid_id=microgrid_id),
                timeout=DEFAULT_GRPC_CALL_TIMEOUT,
            ),
            method_name="GetMicrogrid",
        )

        return microgrid_from_proto(response.microgrid)

    async def list_microgrid_electrical_components(
        self, microgrid_id: int
    ) -> list[ElectricalComponent]:
        """
        Get the electrical components of a microgrid.

        Args:
            microgrid_id: The ID of the microgrid to get the electrical components of.

        Returns:
            The electrical components of the microgrid.
        """
        response = await call_stub_method(
            self,
            lambda: self.stub.ListMicrogridElectricalComponents(
                assets_pb2.ListMicrogridElectricalComponentsRequest(
                    microgrid_id=microgrid_id,
                ),
                timeout=DEFAULT_GRPC_CALL_TIMEOUT,
            ),
            method_name="ListMicrogridElectricalComponents",
        )

        return [
            electrical_component_proto(component) for component in response.components
        ]

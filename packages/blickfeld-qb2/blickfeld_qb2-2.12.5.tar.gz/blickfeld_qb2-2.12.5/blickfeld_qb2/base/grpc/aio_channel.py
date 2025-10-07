import asyncio
import contextlib
import inspect
import logging
import os
from collections.abc import Awaitable, Callable
from types import TracebackType

from grpc import (
    AuthMetadataContext,
    AuthMetadataPlugin,
    AuthMetadataPluginCallback,
    ChannelConnectivity,
    StatusCode,
    composite_channel_credentials,
    metadata_call_credentials,
    ssl_channel_credentials,
)
from grpc.aio import AioRpcError, Channel, Metadata, insecure_channel, secure_channel

from blickfeld.base.grpc.base_error import BaseError

from .constants import OPTIONS
from .device_ca_cert import ca_cert

logger = logging.getLogger("channel")


class AioChannel:
    """
    Channel class is used to securely connect to a Qb2 device.

    The connection is encrypted and authenticated.
    The serial_number can be passed additionally to authenticate a particular device.
    If it is not supplied, the authentication only checks if it is a Blickfeld device.

    ::param fqdn_or_ip: Fully qualified domain name e.g. qb2-xxxxx.blickfeld.com, hostname, or IP address
    :type fqdn_or_ip: str
    param serial_number: Unique serial number assigned to each Qb2 device (corresponding serial number is written on the device label)
    :type serial_number: str
    :param port: Port on which the Qb2 device is reachable (the default is 55551)
    :type port: uint
    :param device_ca_cert: String containing a root certificate for SSL connection
    :type device_ca_cert: str
    :param token: String containing an access token or an awaitable which is called on every method call
    """

    def __init__(
        self,
        fqdn_or_ip: str,
        serial_number: str | None = None,
        port: int | None = None,
        device_ca_cert: str = ca_cert,
        token: str | Callable[["AioChannel"], str] | Awaitable[str] | None = None,
        metadata: Metadata | None = None,
        secure: bool | None = None,
        timeout: int | None = 10,
    ) -> None:
        metadata = metadata or Metadata()

        # Store all properties to allow clone
        self.fqdn_or_ip = fqdn_or_ip
        self.serial_number = serial_number
        self.port = port
        self.device_ca_cert = device_ca_cert
        self.token = token
        self.metadata = metadata
        self.secure = (
            os.getenv("BF_ALLOW_INSECURE_CONNECTIONS") is None or token is not None if secure is None else secure
        )
        self.timeout = timeout

        self.logger = logging.getLogger("Channel")

        # Set name for hostname check to Qb2 device name
        device_name = serial_number + ".qb2.blickfeld.com" if serial_number else None

        this = self

        class TokenPlugin(AuthMetadataPlugin):
            def __call__(self, context: AuthMetadataContext, callback: AuthMetadataPluginCallback) -> None:
                async def inject() -> None:
                    try:
                        try:
                            token = this.token
                            if callable(token):
                                token = token(this)
                            if inspect.isawaitable(token):
                                token = await token

                            if token:
                                metadata.set_all("token", values=[token])

                            callback(metadata=metadata, error=None)
                        except ExceptionGroup as ex:
                            raise ex.exceptions[0]
                    except AioRpcError as ex:
                        callback(metadata=metadata, error=f"{ex.code().name}: {ex.details()}")
                    except Exception as ex:
                        callback(metadata=metadata, error=ex)

                this._task_group.create_task(inject())  # noqa: SLF001

        token_call_credentials = metadata_call_credentials(TokenPlugin())

        # Establish TLS connection to verify connectivity
        if self.secure:
            self.port = port or 55551
            credentials = composite_channel_credentials(
                ssl_channel_credentials(
                    root_certificates=device_ca_cert.encode(), private_key=None, certificate_chain=None
                ),
                token_call_credentials,
            )
            self._channel = secure_channel(
                f"{fqdn_or_ip}:{self.port}",
                credentials,
                ([("grpc.ssl_target_name_override", device_name)] if device_name else []) + OPTIONS,
            )
        else:
            self.logger.info(f"Using insecure connection for {fqdn_or_ip} as BF_ALLOW_INSECURE_CONNECTIONS is set")
            self.port = port or 50051
            self._channel = insecure_channel(f"{fqdn_or_ip}:{self.port}", options=OPTIONS)

    def clone(self, token: str | Callable[["AioChannel"], str] | Awaitable[str] | None = None) -> "AioChannel":
        return AioChannel(
            fqdn_or_ip=self.fqdn_or_ip,
            serial_number=self.serial_number,
            port=self.port,
            device_ca_cert=self.device_ca_cert,
            token=token if token != self.token else self.token,
            metadata=self.metadata,
            secure=self.secure,
            timeout=self.timeout,
        )

    async def __aenter__(self) -> Channel:
        self._task_group = await asyncio.TaskGroup().__aenter__()

        await self._channel.__aenter__()

        try:
            while True:
                last_observed_state = self._channel.get_state(try_to_connect=True)

                if last_observed_state in [
                    ChannelConnectivity.READY,
                    ChannelConnectivity.TRANSIENT_FAILURE,
                ]:
                    break

                try:
                    await asyncio.wait_for(self._channel.wait_for_state_change(last_observed_state), self.timeout)
                except TimeoutError:
                    raise BaseError(
                        StatusCode.UNAVAILABLE,
                        f"Connection to Qb device '{self.fqdn_or_ip}' failed. Deadline exceeded.",
                    )

            if last_observed_state != ChannelConnectivity.READY:
                raise BaseError(
                    StatusCode.UNAVAILABLE, f"Connection to Qb device '{self.fqdn_or_ip}' failed. Network failure."
                )
        except Exception:
            await self.__aexit__(None, None, None)
            raise

        return self._channel

    async def __aexit__(
        self,
        exception_type: type[BaseException] | None,
        exception_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> bool | None:
        with contextlib.suppress(Exception):
            await self._task_group.__aexit__(exception_type, exception_value, traceback)

        await self._channel.close()

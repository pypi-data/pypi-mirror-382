import inspect
import logging
import os
import ssl
from types import TracebackType
from typing import Awaitable, Callable, Optional, Type, Union

from grpclib.client import Channel as gRPClibChannel
from grpclib.config import Configuration
from grpclib.events import SendRequest, listen
from grpclib.metadata import _Metadata as Metadata

from .device_ca_cert import ca_cert


class Channel(gRPClibChannel):
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
        serial_number: Optional[str] = None,
        port: Optional[int] = None,
        device_ca_cert: str = ca_cert,
        token: Optional[Union[str, Callable[["Channel"], str], Awaitable[str]]] = None,
        metadata: Optional[Metadata] = None,
        secure: Optional[bool] = None,
    ) -> None:
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

        self.logger = logging.getLogger("Channel")

        # create SSL context for client
        ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)  # client side context
        ctx.verify_mode = ssl.CERT_REQUIRED  # TLS
        ctx.check_hostname = serial_number is not None
        ctx.set_alpn_protocols(["h2"])
        try:
            ctx.load_verify_locations(cadata=device_ca_cert)
        except ssl.SSLError as error:
            raise RuntimeError("Device CA certificate is of incorrect format:" + error.reason)

        # Set name for hostname check to Qb2 device name
        device_name = serial_number + ".qb2.blickfeld.com" if serial_number else None
        config = Configuration(ssl_target_name_override=device_name) if device_name else None

        # Establish TLS connection to verify connectivity
        channel_port = port or 55551
        if not self.secure:
            self.logger.info(f"Using insecure connection for {fqdn_or_ip} as BF_ALLOW_INSECURE_CONNECTIONS is set")
            channel_port = port or 50051
            ctx = None
            config = None

        # establish gRPC secured channel
        super().__init__(host=fqdn_or_ip, port=channel_port, ssl=ctx, config=config)
        # if token is provided -> inject it to every outgoing send request
        if token:
            listen(self, SendRequest, self.__inject_token)

        if metadata:
            listen(self, SendRequest, self.__inject_metadata)

    def clone(self, token: Optional[Union[str, Callable[["Channel"], str], Awaitable[str]]] = None) -> "Channel":
        return Channel(
            fqdn_or_ip=self.fqdn_or_ip,
            serial_number=self.serial_number,
            port=self.port,
            device_ca_cert=self.device_ca_cert,
            token=token if token != self.token else self.token,
            metadata=self.metadata,
            secure=self.secure,
        )

    async def __inject_token(self, event: SendRequest) -> None:
        # if token is method, call it to get token
        token = self.token
        if callable(token):
            token = token(self)
        if inspect.isawaitable(token):
            token = await token
        event.metadata["token"] = token

    async def __inject_metadata(self, event: SendRequest) -> None:
        event.metadata.update(self.metadata)

    async def __aenter__(self) -> "Channel":
        return self

    async def __aexit__(
        self,
        exception_type: Optional[Type[BaseException]],
        exception_value: Optional[BaseException],
        traceback: Optional[TracebackType],
    ) -> Optional[bool]:
        self.close()

    # Allow synchronous usage
    def __enter__(self) -> "Channel":
        return self

    def __exit__(
        self,
        exception_type: Optional[Type[BaseException]],
        exception_value: Optional[BaseException],
        traceback: Optional[TracebackType],
    ) -> Optional[bool]:
        self.close()

from typing import Self

from grpc import (
    ChannelCredentials,
    CallCredentials,
    ssl_channel_credentials,
    composite_channel_credentials,
    insecure_channel,
    secure_channel,
)
from grpc.aio import (
    insecure_channel as insecure_channel_async,
    secure_channel as secure_channel_async,
)
from grpc.experimental import insecure_channel_credentials, ChannelOptions
from kessel.grpc import oauth2_call_credentials


class ClientBuilder:
    _stub_class = None

    def __init__(self, target: str):
        self._target = target
        self._call_credentials = None
        self._channel_credentials = None

        if not self._target or type(self._target) is not str:
            raise "Invalid target type"

    def oauth2_client_authenticated(
        self,
        oauth2_client_credentials: "kessel.auth.OAuth2ClientCredentials",
        channel_credentials: ChannelCredentials = None,
    ) -> Self:
        self._call_credentials = oauth2_call_credentials(oauth2_client_credentials)
        self._channel_credentials = channel_credentials
        self._validate_credentials()
        return self

    def authenticated(
        self,
        call_credentials: CallCredentials = None,
        channel_credentials: ChannelCredentials = None,
    ) -> Self:
        self._call_credentials = call_credentials
        self._channel_credentials = channel_credentials
        return self

    def unauthenticated(self, channel_credentials: ChannelCredentials = None) -> Self:
        self._call_credentials = None
        self._channel_credentials = channel_credentials
        return self

    def insecure(self) -> Self:
        self._call_credentials = None
        self._channel_credentials = insecure_channel_credentials()
        return self

    def build(self):
        credentials = self._build_credentials()

        # Enable single-threaded unary streams
        channel_options = [(ChannelOptions.SingleThreadedUnaryStream, 1)]

        if self._channel_credentials is insecure_channel_credentials():
            channel = insecure_channel(self._target, options=channel_options)
        else:
            channel = secure_channel(self._target, credentials=credentials, options=channel_options)

        return self._stub_class(channel), channel

    def build_async(self):
        credentials = self._build_credentials()

        if self._channel_credentials is insecure_channel_credentials():
            channel = insecure_channel_async(self._target)
        else:
            channel = secure_channel_async(self._target, credentials=credentials)

        return self._stub_class(channel), channel

    def _build_credentials(self):
        if self._channel_credentials is None:
            self._channel_credentials = ssl_channel_credentials()

        if self._call_credentials is not None:
            return composite_channel_credentials(self._channel_credentials, self._call_credentials)

        return self._channel_credentials

    def _validate_credentials(self):
        if (
            self._call_credentials is not None
            and self._channel_credentials is insecure_channel_credentials()
        ):
            raise "Invalid credential configuration: can not authenticate with insecure channel"


def client_builder_for_stub(stub_class) -> type[ClientBuilder]:
    class ConcreteClientBuilder(ClientBuilder):
        _stub_class = stub_class

    return ConcreteClientBuilder

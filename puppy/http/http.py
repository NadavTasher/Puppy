from puppy.http.mixins import (
    HTTPGzipReceiverMixIn,
    HTTPGzipTransmitterMixIn,
    HTTPConnectionStateReceiverMixIn,
    HTTPConnectionStateTransmitterMixIn,
    HTTPHostTransmitterMixIn,
)  # NOQA


class HTTP(
    HTTPGzipReceiverMixIn,
    HTTPGzipTransmitterMixIn,
    HTTPConnectionStateReceiverMixIn,
    HTTPConnectionStateTransmitterMixIn,
    HTTPHostTransmitterMixIn,
):
    pass

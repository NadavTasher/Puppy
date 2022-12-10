from puppy.http.mixins import (
    HTTPGzipReceiverMixIn,
    HTTPGzipTransmitterMixIn,
    HTTPConnectionStateReceiverMixIn,
    HTTPConnectionStateTransmitterMixIn,
    HTTPHostTransmitterMixIn,
)


class HTTP(
        HTTPGzipReceiverMixIn,
        HTTPGzipTransmitterMixIn,
        HTTPConnectionStateReceiverMixIn,
        HTTPConnectionStateTransmitterMixIn,
        HTTPHostTransmitterMixIn,
):
    pass

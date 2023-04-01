from puppy.http.mixins.host import HTTPHostTransmitterMixIn
from puppy.http.mixins.safety import HTTPSafeReceiverMixIn
from puppy.http.mixins.connection import HTTPConnectionStateTransmitterMixIn, HTTPConnectionStateReceiverMixIn
from puppy.http.mixins.compression import HTTPCompressionTransmitterMixIn, HTTPCompressionReceiverMixIn
from puppy.http.mixins.compatibility import HTTPCompatibleReceiverMixIn, HTTPBufferedTransmitterMixIn


class HTTP(
        HTTPCompressionReceiverMixIn,
        HTTPCompressionTransmitterMixIn,
        HTTPConnectionStateReceiverMixIn,
        HTTPConnectionStateTransmitterMixIn,
        HTTPHostTransmitterMixIn,
):
    pass


class SafeHTTP(HTTP, HTTPSafeReceiverMixIn):
    pass


class CompatibleHTTP(HTTP, HTTPCompatibleReceiverMixIn, HTTPBufferedTransmitterMixIn):
    pass

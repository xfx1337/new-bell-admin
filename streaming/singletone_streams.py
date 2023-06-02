from streaming.stream import Stream
from singleton import singleton

@singleton
class DeviceRefreshingStream(Stream):
    pass

@singleton
class DeviceRequestStream(Stream):
    pass

@singleton
class DeviceResponseStream(Stream):
    pass
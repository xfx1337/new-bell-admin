from singleton import singleton
from streaming.stream import Stream

@singleton
class StatStream(Stream):
    def set_monitoring_callback(self, callback):
        self._callback = callback
        self._enable_callback = True
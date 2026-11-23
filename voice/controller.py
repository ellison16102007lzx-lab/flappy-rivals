"""Microphone access starts in the browser. Unit tests can import this module directly."""
from math import sqrt


def volume_from_samples(samples, sensitivity=1.0):
    rms = sqrt(sum(x * x for x in samples) / max(1, len(samples)))
    return min(1.0, max(0.0, (rms - 0.008) * max(0.25, min(3.0, sensitivity)) / 0.12))


class Microphone:
    def __init__(self):
        self.context = self.stream = self.analyser = self.source = None
        self.buffer = None

    async def start(self):
        """Call from a user click and disable the button while the request is pending."""
        from js import AudioContext, Float32Array, JSON, navigator
        if self.stream is not None:
            return
        try:
            self.context = AudioContext.new()
            await self.context.resume()
            self.stream = await navigator.mediaDevices.getUserMedia(
                JSON.parse('{"audio":true}')
            )
            self.source = self.context.createMediaStreamSource(self.stream)
            self.analyser = self.context.createAnalyser()
            self.analyser.fftSize = 512
            self.buffer = Float32Array.new(512)
            self.source.connect(self.analyser)
        except Exception:
            await self.stop()
            raise

    def read(self, sensitivity=1.0):
        if self.analyser is None:
            return 0.0
        self.analyser.getFloatTimeDomainData(self.buffer)
        return volume_from_samples(self.buffer.to_py(), sensitivity)

    async def stop(self):
        if self.stream is not None:
            for track in self.stream.getTracks():
                track.stop()
        context = self.context
        self.context = self.stream = self.analyser = self.source = self.buffer = None
        if context is not None and context.state != "closed":
            await context.close()

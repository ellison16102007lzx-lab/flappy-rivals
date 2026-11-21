"""麦克风接口仅在浏览器内启动。Python 单元测试可直接导入本模块。"""
from math import sqrt


def volume_from_samples(samples):
    rms = sqrt(sum(x * x for x in samples) / max(1, len(samples)))
    return min(1.0, max(0.0, (rms - 0.008) / 0.12))


class Microphone:
    def __init__(self):
        self.context = self.stream = self.analyser = self.source = None
        self.buffer = None

    async def start(self):
        """绑定到用户点击事件；调用方在等待期间禁用按钮。"""
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

    def read(self):
        if self.analyser is None:
            return 0.0
        self.analyser.getFloatTimeDomainData(self.buffer)
        return volume_from_samples(self.buffer.to_py())

    async def stop(self):
        if self.stream is not None:
            for track in self.stream.getTracks():
                track.stop()
        context = self.context
        self.context = self.stream = self.analyser = self.source = self.buffer = None
        if context is not None and context.state != "closed":
            await context.close()

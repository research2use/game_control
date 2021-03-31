import collections


class FrameBuffer:

    def __init__(self, maxlen=5):
        self._frames = collections.deque(maxlen=maxlen)

    @property
    def frames(self):
        return self._frames

    @property
    def is_full(self):
        return len(self.frames) == self.frames.maxlen

    @property
    def last_frame(self):
        return self.frames[-1] if len(self.frames) > 0 else None

    def add_frame(self, frame):
        self.frames.append(frame)

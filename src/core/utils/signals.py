from typing import Callable, List

from blinker import Signal


class SignalGroup:
    def __init__(self):
        self._signals: List[Signal] = []
        self._receivers: List[Callable] = []

    def add(self, signal: Signal):
        def inner(func):
            self._signals.append(signal)
            self._receivers.append(func)
            return func

        return inner

    def connect(self):
        for signal, receiver in zip(self._signals, self._receivers):
            signal.connect(receiver)

    def disconnect(self):
        for signal, receiver in zip(self._signals, self._receivers):
            signal.disconnect(receiver)

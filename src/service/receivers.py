from blinker import Namespace

from core.utils.signals import SignalGroup

group = SignalGroup()
signals_namespace = Namespace()
some_signal = signals_namespace.signal("some-signal")


@group.add(some_signal)
def signal_callback(user_id, **kw):
    pass

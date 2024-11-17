import os
from typing import Any

import pytest

disabled = pytest.mark.skipif(True, reason="disabled")
eos_v1_photos = pytest.mark.skipif(True, reason="v1 photos end of service")
slow = pytest.mark.skipif(not os.environ.get("SLOW"), reason="slow")

try:
    _columns = int(os.popen("stty size", "r").read().split()[1])
except Exception:  # noqa
    _columns = 80

leader = "-> "
width = int(_columns) - len(leader)


def ptrunc(s: str) -> None:
    """Print string with a leader truncated to width."""
    print(leader + str(s)[:width])


def tprint(*args: str, **kwargs: Any) -> None:
    if args:
        print(leader, end="")
        print(*args, **kwargs)
    else:
        print()


def horzrule(fill: str = "-") -> None:
    """Print a horizontal ruler."""
    print(fill * width)

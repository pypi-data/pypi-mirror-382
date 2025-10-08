from collections.abc import Coroutine
from typing import Any


type SimpleCoroutine[R] = Coroutine[Any, Any, R]

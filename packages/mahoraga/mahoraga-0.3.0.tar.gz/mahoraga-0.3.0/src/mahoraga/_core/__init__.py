# Copyright 2025 hingebase

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

__all__ = [
    "APIRoute",
    "Address",
    "AsyncClient",
    "Config",
    "GitHubRelease",
    "NPMBase",
    "Predicate",
    "Response",
    "Server",
    "Statistics",
    "StreamingResponse",
    "WeakValueDictionary",
    "cache_action",
    "context",
    "get",
    "load_balance",
    "schedule_exit",
    "stream",
    "unreachable",
]

from typing import NoReturn

from ._config import Address, Config, Predicate, Server
from ._context import (
    AsyncClient,
    Context,
    Statistics,
    WeakValueDictionary,
    cache_action,
    schedule_exit,
)
from ._metadata import GitHubRelease, NPMBase
from ._stream import (
    APIRoute,
    Response,
    StreamingResponse,
    get,
    load_balance,
    stream,
)

context = Context("context")


def unreachable(message: str = "Unreachable") -> NoReturn:
    raise AssertionError(message)

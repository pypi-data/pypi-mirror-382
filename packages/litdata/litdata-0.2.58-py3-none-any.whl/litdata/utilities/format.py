# Copyright The Lightning AI team.
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from typing import Any

from litdata.constants import _TQDM_AVAILABLE

_FORMAT_TO_RATIO = {
    "kb": 1000,
    "mb": 1000**2,
    "gb": 1000**3,
    "tb": 1000**4,
}


def _convert_bytes_to_int(bytes_str: str) -> int:
    """Convert human-readable byte format to an integer."""
    for suffix in _FORMAT_TO_RATIO:
        bytes_str = bytes_str.lower().strip()
        if bytes_str.lower().endswith(suffix):
            try:
                return int(float(bytes_str[0 : -len(suffix)]) * _FORMAT_TO_RATIO[suffix])
            except ValueError:
                raise ValueError(
                    f"Unsupported value/suffix {bytes_str}. Supported suffix are "
                    f"{['b'] + list(_FORMAT_TO_RATIO.keys())}."
                )
    raise ValueError(f"The supported units are {_FORMAT_TO_RATIO.keys()}")


def _human_readable_bytes(num_bytes: float) -> str:
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if abs(num_bytes) < 1000.0:
            return f"{num_bytes:3.1f} {unit}"
        num_bytes /= 1000.0
    return f"{num_bytes:.1f} PB"


def _get_tqdm_iterator_if_available() -> Any:
    if _TQDM_AVAILABLE:
        from tqdm.auto import tqdm as _tqdm

        return _tqdm

    def _pass_through(iterator: Any) -> Any:
        yield from iterator

    return _pass_through

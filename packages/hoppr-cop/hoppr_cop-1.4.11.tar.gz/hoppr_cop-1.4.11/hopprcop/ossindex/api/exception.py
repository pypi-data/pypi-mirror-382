# ruff: noqa
"""Exceptions that can be thrown from API interaction."""
#
# Copyright 2022-Present Sonatype Inc.
#
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
#
from __future__ import annotations


class OssIndexException(Exception):
    """Base exception which all exceptions raised by this library extend."""


class AccessDeniedException(OssIndexException):
    """Raised if supplied credentials for Oss Index are invalid."""


class RateLimitException(OssIndexException):
    """Raised if oss index returns a 429 too many requests exception."""

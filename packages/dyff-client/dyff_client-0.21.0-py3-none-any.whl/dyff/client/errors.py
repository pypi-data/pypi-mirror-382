# SPDX-FileCopyrightText: 2024 UL Research Institutes
# SPDX-License-Identifier: Apache-2.0

# We bring this into our namespace so that people can catch it without being
# confused by having to import 'azure.core'
from azure.core.exceptions import HttpResponseError

__all__ = [
    "HttpResponseError",
]

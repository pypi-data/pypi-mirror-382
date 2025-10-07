# SPDX-FileCopyrightText: 2024 UL Research Institutes
# SPDX-License-Identifier: Apache-2.0

import importlib

import pytest


@pytest.mark.parametrize(
    "module_name",
    [
        "dyff.client._generated._serialization",
        "dyff.client._generated._configuration",
        "dyff.client._generated._client",
        "dyff.client._generated.operations",
        "dyff.client._generated.operations._patch",
        "dyff.client._generated.operations._operations",
        "dyff.client._generated",
        "dyff.client._generated._patch",
        "dyff.client._generated.aio._configuration",
        "dyff.client._generated.aio._client",
        "dyff.client._generated.aio.operations",
        "dyff.client._generated.aio.operations._patch",
        "dyff.client._generated.aio.operations._operations",
        "dyff.client._generated.aio",
        "dyff.client._generated.aio._patch",
        "dyff.client.client",
        "dyff.client",
    ],
)
def test_import_module(module_name):
    importlib.import_module(module_name)

# SPDX-FileCopyrightText: 2024 UL Research Institutes
# SPDX-License-Identifier: Apache-2.0

# mypy: disable-error-code="import-untyped"
from __future__ import annotations

import os
import warnings
from typing import Any, Optional, Union

from azure.core.credentials import AccessToken, TokenCredential
from azure.core.pipeline.policies import BearerTokenCredentialPolicy
from httpx import Timeout

from dyff.schema.platform import (
    DyffEntityType,
    Entities,
    EntityIdentifier,
    EntityKindLiteral,
)

from ._apigroups import (
    _Artifacts,
    _Datasets,
    _Evaluations,
    _Families,
    _InferenceServices,
    _InferenceSessions,
    _Measurements,
    _Methods,
    _Models,
    _Modules,
    _Reports,
    _SafetyCases,
    _UseCases,
)
from ._generated import DyffV0API as RawClient


class _APIKeyCredential(TokenCredential):
    def __init__(self, *, api_token: str):
        self.api_token = api_token

    def get_token(
        self,
        *scopes: str,
        claims: Optional[str] = None,
        tenant_id: Optional[str] = None,
        **kwargs: Any,
    ) -> AccessToken:
        return AccessToken(self.api_token, -1)


_APIGroupType = Union[
    _Artifacts,
    _Datasets,
    _Evaluations,
    _Families,
    _InferenceServices,
    _InferenceSessions,
    _Measurements,
    _Methods,
    _Models,
    _Modules,
    _Reports,
    _SafetyCases,
    _UseCases,
]


class Client:
    """The Python client for the Dyff Platform API.

    API operations are grouped by the resource type that they manipulate. For
    example, all operations on ``Evaluation`` resources are accessed like
    ``client.evaluations.create()``.

    The Python API functions may have somewhat different behavior from the
    corresponding API endpoints, and the Python client also adds several
    higher-level API functions that are implemented with multiple endpoint
    calls.
    """

    def __init__(
        self,
        *,
        api_token: Optional[str] = None,
        api_key: Optional[str] = None,
        endpoint: Optional[str] = None,
        registry_url: Optional[str] = None,
        verify_ssl_certificates: bool = True,
        insecure: bool = False,
        timeout: Optional[Timeout] = None,
    ):
        """
        :param str api_token: An API token to use for authentication. If not
            set, the token is read from the DYFF_API_TOKEN environment variable.
        :param str api_key: Deprecated alias for 'api_token'

            .. deprecated:: 0.13.1
                Use api_token instead
        :param str endpoint: The URL where the Dyff Platform API is hosted.
            Defaults to the UL DSRI-hosted Dyff instance.
        :param bool verify_ssl_certificates: You can disable certificate
            verification for testing; you should do this only if you have
            also changed ``endpoint`` to point to a trusted local server.

            .. deprecated:: 0.2.2
                Use insecure instead
        :param bool insecure: Disable certificate verification for testing.
            you should do this only if you have
            also changed ``endpoint`` to point to a trusted local server.
        """
        if not verify_ssl_certificates and insecure:
            raise ValueError("verify_ssl_certificates is deprecated; use insecure")
        if not verify_ssl_certificates:
            warnings.warn(
                "verify_ssl_certificates is deprecated; use insecure",
                DeprecationWarning,
            )
        self._insecure = insecure or not verify_ssl_certificates

        if api_token is None:
            api_token = api_key or os.environ.get("DYFF_API_TOKEN")
        if api_token is None:
            raise ValueError(
                "Must provide api_token or set DYFF_API_TOKEN environment variable"
            )
        self._api_token = api_token

        if endpoint is None:
            endpoint = os.environ.get("DYFF_API_ENDPOINT", "https://api.dyff.io/v0")
        self._endpoint = endpoint

        if registry_url is None:
            registry_url = os.environ.get(
                "DYFF_REGISTRY_URL", "https://registry.dyff.io"
            )
        self._registry_url = registry_url

        self._timeout = timeout or Timeout(5.0)  # Same as httpx default

        credential = _APIKeyCredential(api_token=api_token)
        authentication_policy = BearerTokenCredentialPolicy(credential)
        self._raw = RawClient(
            endpoint=endpoint,
            credential=credential,
            authentication_policy=authentication_policy,
        )

        # We want the ability to disable SSL certificate verification for testing
        # on localhost. It should be possible to do this via the Configuration object:
        # e.g., config.<some_field> = azure.core.configuration.ConnectionConfiguration(connection_verify=False)
        #
        # The docs state that the ConnectionConfiguration class is "Found in the Configuration object."
        # https://learn.microsoft.com/en-us/python/api/azure-core/azure.core.configuration.connectionconfiguration?view=azure-python
        #
        # But at no point do they say what the name of the field should be! The
        # docs for azure.core.configuration.Configuration don't mention any
        # connection configuration. The field is called 'connection_config' in the
        # _transport member of _pipeline, but _transport will not pick up the
        # altered ConnectionConfiguration if it is set on 'config.connection_config'
        #
        # Example:
        # client._config.connection_config = ConnectionConfiguration(connection_verify=False)
        # [in Client:]
        # >>> print(self._config.connection_config.verify)
        # False
        # >> print(self._pipeline._transport.connection_config.verify)
        # True

        # Note: self._raw._client._pipeline._transport usually is an
        # ``azure.core.pipeline.transport.RequestsTransport``
        self._raw._client._pipeline._transport.connection_config.verify = (  # type: ignore
            not self.insecure
        )

        self._artifacts = _Artifacts(self)
        self._datasets = _Datasets(self)
        self._evaluations = _Evaluations(self)
        self._families = _Families(self)
        self._inferenceservices = _InferenceServices(self)
        self._inferencesessions = _InferenceSessions(self)
        self._measurements = _Measurements(self)
        self._methods = _Methods(self)
        self._models = _Models(self)
        self._modules = _Modules(self)
        self._reports = _Reports(self)
        self._safetycases = _SafetyCases(self)
        self._usecases = _UseCases(self)

        self._apigroups_by_kind: dict[Entities, _APIGroupType] = {
            Entities.Artifact: self._artifacts,
            Entities.Dataset: self._datasets,
            Entities.Evaluation: self._evaluations,
            Entities.Family: self._families,
            Entities.InferenceService: self._inferenceservices,
            Entities.InferenceSession: self._inferencesessions,
            Entities.Measurement: self._measurements,
            Entities.Method: self._methods,
            Entities.Module: self._modules,
            Entities.Report: self._reports,
            Entities.SafetyCase: self._safetycases,
            Entities.UseCase: self._usecases,
        }

    @property
    def insecure(self) -> bool:
        return self._insecure

    @property
    def timeout(self) -> Timeout:
        return self._timeout

    @property
    def raw(self) -> RawClient:
        """The "raw" API client, which can be used to send JSON requests directly."""
        return self._raw

    def apigroup(self, kind: Entities | EntityKindLiteral) -> _APIGroupType:
        """Get the API group by kind.

        For example, ``dyffapi.apigroup("Dataset").get()`` is the same as
        ``dyffapi.datasets.get()``.
        """
        kind = Entities(kind)
        return self._apigroups_by_kind[kind]  # type: ignore

    def get(self, entity: EntityIdentifier) -> DyffEntityType:
        """Get an entity by identifier (id + kind).

        The return type will always match the kind.
        """
        return self.apigroup(entity.kind).get(entity.id)

    @property
    def artifacts(self) -> _Artifacts:
        """Operations on :class:`~dyff.schema.platform.OCIArtifact` entities."""
        return self._artifacts

    @property
    def datasets(self) -> _Datasets:
        """Operations on :class:`~dyff.schema.platform.Dataset` entities."""
        return self._datasets

    @property
    def evaluations(self) -> _Evaluations:
        """Operations on :class:`~dyff.schema.platform.Evaluation` entities."""
        return self._evaluations

    @property
    def families(self) -> _Families:
        """Operations on :class:`~dyff.schema.platform.Family` entities."""
        return self._families

    @property
    def inferenceservices(self) -> _InferenceServices:
        """Operations on :class:`~dyff.schema.platform.InferenceService` entities."""
        return self._inferenceservices

    @property
    def inferencesessions(self) -> _InferenceSessions:
        """Operations on :class:`~dyff.schema.platform.InferenceSession` entities."""
        return self._inferencesessions

    @property
    def methods(self) -> _Methods:
        """Operations on :class:`~dyff.schema.platform.Method` entities."""
        return self._methods

    @property
    def measurements(self) -> _Measurements:
        """Operations on :class:`~dyff.schema.platform.Measurement` entities."""
        return self._measurements

    @property
    def models(self) -> _Models:
        """Operations on :class:`~dyff.schema.platform.Model` entities."""
        return self._models

    @property
    def modules(self) -> _Modules:
        """Operations on :class:`~dyff.schema.platform.Module` entities."""
        return self._modules

    @property
    def reports(self) -> _Reports:
        """Operations on :class:`~dyff.schema.platform.Report` entities."""
        return self._reports

    @property
    def safetycases(self) -> _SafetyCases:
        """Operations on :class:`~dyff.schema.platform.SafetyCase` entities."""
        return self._safetycases

    @property
    def usecases(self) -> _UseCases:
        """Operations on :class:`~dyff.schema.platform.UseCase` entities."""
        return self._usecases


__all__ = [
    "Client",
    "RawClient",
    "Timeout",
]

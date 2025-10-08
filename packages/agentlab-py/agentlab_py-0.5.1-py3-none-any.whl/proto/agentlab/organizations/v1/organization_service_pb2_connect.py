# Generated Connect client code

from __future__ import annotations
from collections.abc import AsyncIterator
from collections.abc import Iterator
from collections.abc import Iterable
import aiohttp
import urllib3
import typing
import sys

from connectrpc.client_async import AsyncConnectClient
from connectrpc.client_sync import ConnectClient
from connectrpc.client_protocol import ConnectProtocol
from connectrpc.client_connect import ConnectProtocolError
from connectrpc.headers import HeaderInput
from connectrpc.server import ClientRequest
from connectrpc.server import ClientStream
from connectrpc.server import ServerResponse
from connectrpc.server import ServerStream
from connectrpc.server_sync import ConnectWSGI
from connectrpc.streams import StreamInput
from connectrpc.streams import AsyncStreamOutput
from connectrpc.streams import StreamOutput
from connectrpc.unary import UnaryOutput
from connectrpc.unary import ClientStreamingOutput

if typing.TYPE_CHECKING:
    # wsgiref.types was added in Python 3.11.
    if sys.version_info >= (3, 11):
        from wsgiref.types import WSGIApplication
    else:
        from _typeshed.wsgi import WSGIApplication

import google.protobuf.empty_pb2
import proto.agentlab.organizations.v1.organization_pb2
import proto.agentlab.organizations.v1.organization_service_pb2

class OrganizationServiceClient:
    def __init__(
        self,
        base_url: str,
        http_client: urllib3.PoolManager | None = None,
        protocol: ConnectProtocol = ConnectProtocol.CONNECT_PROTOBUF,
    ):
        self.base_url = base_url
        self._connect_client = ConnectClient(http_client, protocol)
    def call_create_organization(
        self, req: proto.agentlab.organizations.v1.organization_service_pb2.CreateOrganizationRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[proto.agentlab.organizations.v1.organization_pb2.Organization]:
        """Low-level method to call CreateOrganization, granting access to errors and metadata"""
        url = self.base_url + "/agentlab.organizations.v1.OrganizationService/CreateOrganization"
        return self._connect_client.call_unary(url, req, proto.agentlab.organizations.v1.organization_pb2.Organization,extra_headers, timeout_seconds)


    def create_organization(
        self, req: proto.agentlab.organizations.v1.organization_service_pb2.CreateOrganizationRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> proto.agentlab.organizations.v1.organization_pb2.Organization:
        response = self.call_create_organization(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_get_organization(
        self, req: proto.agentlab.organizations.v1.organization_service_pb2.GetOrganizationRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[proto.agentlab.organizations.v1.organization_pb2.Organization]:
        """Low-level method to call GetOrganization, granting access to errors and metadata"""
        url = self.base_url + "/agentlab.organizations.v1.OrganizationService/GetOrganization"
        return self._connect_client.call_unary(url, req, proto.agentlab.organizations.v1.organization_pb2.Organization,extra_headers, timeout_seconds)


    def get_organization(
        self, req: proto.agentlab.organizations.v1.organization_service_pb2.GetOrganizationRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> proto.agentlab.organizations.v1.organization_pb2.Organization:
        response = self.call_get_organization(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_list_organizations(
        self, req: proto.agentlab.organizations.v1.organization_service_pb2.ListOrganizationsRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[proto.agentlab.organizations.v1.organization_service_pb2.ListOrganizationsResponse]:
        """Low-level method to call ListOrganizations, granting access to errors and metadata"""
        url = self.base_url + "/agentlab.organizations.v1.OrganizationService/ListOrganizations"
        return self._connect_client.call_unary(url, req, proto.agentlab.organizations.v1.organization_service_pb2.ListOrganizationsResponse,extra_headers, timeout_seconds)


    def list_organizations(
        self, req: proto.agentlab.organizations.v1.organization_service_pb2.ListOrganizationsRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> proto.agentlab.organizations.v1.organization_service_pb2.ListOrganizationsResponse:
        response = self.call_list_organizations(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_update_organization(
        self, req: proto.agentlab.organizations.v1.organization_service_pb2.UpdateOrganizationRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[proto.agentlab.organizations.v1.organization_pb2.Organization]:
        """Low-level method to call UpdateOrganization, granting access to errors and metadata"""
        url = self.base_url + "/agentlab.organizations.v1.OrganizationService/UpdateOrganization"
        return self._connect_client.call_unary(url, req, proto.agentlab.organizations.v1.organization_pb2.Organization,extra_headers, timeout_seconds)


    def update_organization(
        self, req: proto.agentlab.organizations.v1.organization_service_pb2.UpdateOrganizationRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> proto.agentlab.organizations.v1.organization_pb2.Organization:
        response = self.call_update_organization(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_delete_organization(
        self, req: proto.agentlab.organizations.v1.organization_service_pb2.DeleteOrganizationRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[google.protobuf.empty_pb2.Empty]:
        """Low-level method to call DeleteOrganization, granting access to errors and metadata"""
        url = self.base_url + "/agentlab.organizations.v1.OrganizationService/DeleteOrganization"
        return self._connect_client.call_unary(url, req, google.protobuf.empty_pb2.Empty,extra_headers, timeout_seconds)


    def delete_organization(
        self, req: proto.agentlab.organizations.v1.organization_service_pb2.DeleteOrganizationRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> google.protobuf.empty_pb2.Empty:
        response = self.call_delete_organization(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_add_domain_to_allowlist(
        self, req: proto.agentlab.organizations.v1.organization_service_pb2.AddDomainToAllowlistRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[proto.agentlab.organizations.v1.organization_pb2.DomainAllowlistEntry]:
        """Low-level method to call AddDomainToAllowlist, granting access to errors and metadata"""
        url = self.base_url + "/agentlab.organizations.v1.OrganizationService/AddDomainToAllowlist"
        return self._connect_client.call_unary(url, req, proto.agentlab.organizations.v1.organization_pb2.DomainAllowlistEntry,extra_headers, timeout_seconds)


    def add_domain_to_allowlist(
        self, req: proto.agentlab.organizations.v1.organization_service_pb2.AddDomainToAllowlistRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> proto.agentlab.organizations.v1.organization_pb2.DomainAllowlistEntry:
        response = self.call_add_domain_to_allowlist(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_remove_domain_from_allowlist(
        self, req: proto.agentlab.organizations.v1.organization_service_pb2.RemoveDomainFromAllowlistRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[google.protobuf.empty_pb2.Empty]:
        """Low-level method to call RemoveDomainFromAllowlist, granting access to errors and metadata"""
        url = self.base_url + "/agentlab.organizations.v1.OrganizationService/RemoveDomainFromAllowlist"
        return self._connect_client.call_unary(url, req, google.protobuf.empty_pb2.Empty,extra_headers, timeout_seconds)


    def remove_domain_from_allowlist(
        self, req: proto.agentlab.organizations.v1.organization_service_pb2.RemoveDomainFromAllowlistRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> google.protobuf.empty_pb2.Empty:
        response = self.call_remove_domain_from_allowlist(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_list_domain_allowlist(
        self, req: proto.agentlab.organizations.v1.organization_service_pb2.ListDomainAllowlistRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[proto.agentlab.organizations.v1.organization_service_pb2.ListDomainAllowlistResponse]:
        """Low-level method to call ListDomainAllowlist, granting access to errors and metadata"""
        url = self.base_url + "/agentlab.organizations.v1.OrganizationService/ListDomainAllowlist"
        return self._connect_client.call_unary(url, req, proto.agentlab.organizations.v1.organization_service_pb2.ListDomainAllowlistResponse,extra_headers, timeout_seconds)


    def list_domain_allowlist(
        self, req: proto.agentlab.organizations.v1.organization_service_pb2.ListDomainAllowlistRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> proto.agentlab.organizations.v1.organization_service_pb2.ListDomainAllowlistResponse:
        response = self.call_list_domain_allowlist(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg


class AsyncOrganizationServiceClient:
    def __init__(
        self,
        base_url: str,
        http_client: aiohttp.ClientSession,
        protocol: ConnectProtocol = ConnectProtocol.CONNECT_PROTOBUF,
    ):
        self.base_url = base_url
        self._connect_client = AsyncConnectClient(http_client, protocol)

    async def call_create_organization(
        self, req: proto.agentlab.organizations.v1.organization_service_pb2.CreateOrganizationRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[proto.agentlab.organizations.v1.organization_pb2.Organization]:
        """Low-level method to call CreateOrganization, granting access to errors and metadata"""
        url = self.base_url + "/agentlab.organizations.v1.OrganizationService/CreateOrganization"
        return await self._connect_client.call_unary(url, req, proto.agentlab.organizations.v1.organization_pb2.Organization,extra_headers, timeout_seconds)

    async def create_organization(
        self, req: proto.agentlab.organizations.v1.organization_service_pb2.CreateOrganizationRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> proto.agentlab.organizations.v1.organization_pb2.Organization:
        response = await self.call_create_organization(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_get_organization(
        self, req: proto.agentlab.organizations.v1.organization_service_pb2.GetOrganizationRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[proto.agentlab.organizations.v1.organization_pb2.Organization]:
        """Low-level method to call GetOrganization, granting access to errors and metadata"""
        url = self.base_url + "/agentlab.organizations.v1.OrganizationService/GetOrganization"
        return await self._connect_client.call_unary(url, req, proto.agentlab.organizations.v1.organization_pb2.Organization,extra_headers, timeout_seconds)

    async def get_organization(
        self, req: proto.agentlab.organizations.v1.organization_service_pb2.GetOrganizationRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> proto.agentlab.organizations.v1.organization_pb2.Organization:
        response = await self.call_get_organization(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_list_organizations(
        self, req: proto.agentlab.organizations.v1.organization_service_pb2.ListOrganizationsRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[proto.agentlab.organizations.v1.organization_service_pb2.ListOrganizationsResponse]:
        """Low-level method to call ListOrganizations, granting access to errors and metadata"""
        url = self.base_url + "/agentlab.organizations.v1.OrganizationService/ListOrganizations"
        return await self._connect_client.call_unary(url, req, proto.agentlab.organizations.v1.organization_service_pb2.ListOrganizationsResponse,extra_headers, timeout_seconds)

    async def list_organizations(
        self, req: proto.agentlab.organizations.v1.organization_service_pb2.ListOrganizationsRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> proto.agentlab.organizations.v1.organization_service_pb2.ListOrganizationsResponse:
        response = await self.call_list_organizations(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_update_organization(
        self, req: proto.agentlab.organizations.v1.organization_service_pb2.UpdateOrganizationRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[proto.agentlab.organizations.v1.organization_pb2.Organization]:
        """Low-level method to call UpdateOrganization, granting access to errors and metadata"""
        url = self.base_url + "/agentlab.organizations.v1.OrganizationService/UpdateOrganization"
        return await self._connect_client.call_unary(url, req, proto.agentlab.organizations.v1.organization_pb2.Organization,extra_headers, timeout_seconds)

    async def update_organization(
        self, req: proto.agentlab.organizations.v1.organization_service_pb2.UpdateOrganizationRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> proto.agentlab.organizations.v1.organization_pb2.Organization:
        response = await self.call_update_organization(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_delete_organization(
        self, req: proto.agentlab.organizations.v1.organization_service_pb2.DeleteOrganizationRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[google.protobuf.empty_pb2.Empty]:
        """Low-level method to call DeleteOrganization, granting access to errors and metadata"""
        url = self.base_url + "/agentlab.organizations.v1.OrganizationService/DeleteOrganization"
        return await self._connect_client.call_unary(url, req, google.protobuf.empty_pb2.Empty,extra_headers, timeout_seconds)

    async def delete_organization(
        self, req: proto.agentlab.organizations.v1.organization_service_pb2.DeleteOrganizationRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> google.protobuf.empty_pb2.Empty:
        response = await self.call_delete_organization(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_add_domain_to_allowlist(
        self, req: proto.agentlab.organizations.v1.organization_service_pb2.AddDomainToAllowlistRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[proto.agentlab.organizations.v1.organization_pb2.DomainAllowlistEntry]:
        """Low-level method to call AddDomainToAllowlist, granting access to errors and metadata"""
        url = self.base_url + "/agentlab.organizations.v1.OrganizationService/AddDomainToAllowlist"
        return await self._connect_client.call_unary(url, req, proto.agentlab.organizations.v1.organization_pb2.DomainAllowlistEntry,extra_headers, timeout_seconds)

    async def add_domain_to_allowlist(
        self, req: proto.agentlab.organizations.v1.organization_service_pb2.AddDomainToAllowlistRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> proto.agentlab.organizations.v1.organization_pb2.DomainAllowlistEntry:
        response = await self.call_add_domain_to_allowlist(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_remove_domain_from_allowlist(
        self, req: proto.agentlab.organizations.v1.organization_service_pb2.RemoveDomainFromAllowlistRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[google.protobuf.empty_pb2.Empty]:
        """Low-level method to call RemoveDomainFromAllowlist, granting access to errors and metadata"""
        url = self.base_url + "/agentlab.organizations.v1.OrganizationService/RemoveDomainFromAllowlist"
        return await self._connect_client.call_unary(url, req, google.protobuf.empty_pb2.Empty,extra_headers, timeout_seconds)

    async def remove_domain_from_allowlist(
        self, req: proto.agentlab.organizations.v1.organization_service_pb2.RemoveDomainFromAllowlistRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> google.protobuf.empty_pb2.Empty:
        response = await self.call_remove_domain_from_allowlist(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_list_domain_allowlist(
        self, req: proto.agentlab.organizations.v1.organization_service_pb2.ListDomainAllowlistRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[proto.agentlab.organizations.v1.organization_service_pb2.ListDomainAllowlistResponse]:
        """Low-level method to call ListDomainAllowlist, granting access to errors and metadata"""
        url = self.base_url + "/agentlab.organizations.v1.OrganizationService/ListDomainAllowlist"
        return await self._connect_client.call_unary(url, req, proto.agentlab.organizations.v1.organization_service_pb2.ListDomainAllowlistResponse,extra_headers, timeout_seconds)

    async def list_domain_allowlist(
        self, req: proto.agentlab.organizations.v1.organization_service_pb2.ListDomainAllowlistRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> proto.agentlab.organizations.v1.organization_service_pb2.ListDomainAllowlistResponse:
        response = await self.call_list_domain_allowlist(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg


@typing.runtime_checkable
class OrganizationServiceProtocol(typing.Protocol):
    def create_organization(self, req: ClientRequest[proto.agentlab.organizations.v1.organization_service_pb2.CreateOrganizationRequest]) -> ServerResponse[proto.agentlab.organizations.v1.organization_pb2.Organization]:
        ...
    def get_organization(self, req: ClientRequest[proto.agentlab.organizations.v1.organization_service_pb2.GetOrganizationRequest]) -> ServerResponse[proto.agentlab.organizations.v1.organization_pb2.Organization]:
        ...
    def list_organizations(self, req: ClientRequest[proto.agentlab.organizations.v1.organization_service_pb2.ListOrganizationsRequest]) -> ServerResponse[proto.agentlab.organizations.v1.organization_service_pb2.ListOrganizationsResponse]:
        ...
    def update_organization(self, req: ClientRequest[proto.agentlab.organizations.v1.organization_service_pb2.UpdateOrganizationRequest]) -> ServerResponse[proto.agentlab.organizations.v1.organization_pb2.Organization]:
        ...
    def delete_organization(self, req: ClientRequest[proto.agentlab.organizations.v1.organization_service_pb2.DeleteOrganizationRequest]) -> ServerResponse[google.protobuf.empty_pb2.Empty]:
        ...
    def add_domain_to_allowlist(self, req: ClientRequest[proto.agentlab.organizations.v1.organization_service_pb2.AddDomainToAllowlistRequest]) -> ServerResponse[proto.agentlab.organizations.v1.organization_pb2.DomainAllowlistEntry]:
        ...
    def remove_domain_from_allowlist(self, req: ClientRequest[proto.agentlab.organizations.v1.organization_service_pb2.RemoveDomainFromAllowlistRequest]) -> ServerResponse[google.protobuf.empty_pb2.Empty]:
        ...
    def list_domain_allowlist(self, req: ClientRequest[proto.agentlab.organizations.v1.organization_service_pb2.ListDomainAllowlistRequest]) -> ServerResponse[proto.agentlab.organizations.v1.organization_service_pb2.ListDomainAllowlistResponse]:
        ...

ORGANIZATION_SERVICE_PATH_PREFIX = "/agentlab.organizations.v1.OrganizationService"

def wsgi_organization_service(implementation: OrganizationServiceProtocol) -> WSGIApplication:
    app = ConnectWSGI()
    app.register_unary_rpc("/agentlab.organizations.v1.OrganizationService/CreateOrganization", implementation.create_organization, proto.agentlab.organizations.v1.organization_service_pb2.CreateOrganizationRequest)
    app.register_unary_rpc("/agentlab.organizations.v1.OrganizationService/GetOrganization", implementation.get_organization, proto.agentlab.organizations.v1.organization_service_pb2.GetOrganizationRequest)
    app.register_unary_rpc("/agentlab.organizations.v1.OrganizationService/ListOrganizations", implementation.list_organizations, proto.agentlab.organizations.v1.organization_service_pb2.ListOrganizationsRequest)
    app.register_unary_rpc("/agentlab.organizations.v1.OrganizationService/UpdateOrganization", implementation.update_organization, proto.agentlab.organizations.v1.organization_service_pb2.UpdateOrganizationRequest)
    app.register_unary_rpc("/agentlab.organizations.v1.OrganizationService/DeleteOrganization", implementation.delete_organization, proto.agentlab.organizations.v1.organization_service_pb2.DeleteOrganizationRequest)
    app.register_unary_rpc("/agentlab.organizations.v1.OrganizationService/AddDomainToAllowlist", implementation.add_domain_to_allowlist, proto.agentlab.organizations.v1.organization_service_pb2.AddDomainToAllowlistRequest)
    app.register_unary_rpc("/agentlab.organizations.v1.OrganizationService/RemoveDomainFromAllowlist", implementation.remove_domain_from_allowlist, proto.agentlab.organizations.v1.organization_service_pb2.RemoveDomainFromAllowlistRequest)
    app.register_unary_rpc("/agentlab.organizations.v1.OrganizationService/ListDomainAllowlist", implementation.list_domain_allowlist, proto.agentlab.organizations.v1.organization_service_pb2.ListDomainAllowlistRequest)
    return app

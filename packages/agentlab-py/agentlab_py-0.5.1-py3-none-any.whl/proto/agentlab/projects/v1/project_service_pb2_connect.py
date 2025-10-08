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
import proto.agentlab.projects.v1.project_pb2
import proto.agentlab.projects.v1.project_service_pb2

class ProjectServiceClient:
    def __init__(
        self,
        base_url: str,
        http_client: urllib3.PoolManager | None = None,
        protocol: ConnectProtocol = ConnectProtocol.CONNECT_PROTOBUF,
    ):
        self.base_url = base_url
        self._connect_client = ConnectClient(http_client, protocol)
    def call_create_project(
        self, req: proto.agentlab.projects.v1.project_service_pb2.CreateProjectRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[proto.agentlab.projects.v1.project_pb2.Project]:
        """Low-level method to call CreateProject, granting access to errors and metadata"""
        url = self.base_url + "/agentlab.projects.v1.ProjectService/CreateProject"
        return self._connect_client.call_unary(url, req, proto.agentlab.projects.v1.project_pb2.Project,extra_headers, timeout_seconds)


    def create_project(
        self, req: proto.agentlab.projects.v1.project_service_pb2.CreateProjectRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> proto.agentlab.projects.v1.project_pb2.Project:
        response = self.call_create_project(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_get_project(
        self, req: proto.agentlab.projects.v1.project_service_pb2.GetProjectRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[proto.agentlab.projects.v1.project_pb2.Project]:
        """Low-level method to call GetProject, granting access to errors and metadata"""
        url = self.base_url + "/agentlab.projects.v1.ProjectService/GetProject"
        return self._connect_client.call_unary(url, req, proto.agentlab.projects.v1.project_pb2.Project,extra_headers, timeout_seconds)


    def get_project(
        self, req: proto.agentlab.projects.v1.project_service_pb2.GetProjectRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> proto.agentlab.projects.v1.project_pb2.Project:
        response = self.call_get_project(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_list_projects(
        self, req: proto.agentlab.projects.v1.project_service_pb2.ListProjectsRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[proto.agentlab.projects.v1.project_service_pb2.ListProjectsResponse]:
        """Low-level method to call ListProjects, granting access to errors and metadata"""
        url = self.base_url + "/agentlab.projects.v1.ProjectService/ListProjects"
        return self._connect_client.call_unary(url, req, proto.agentlab.projects.v1.project_service_pb2.ListProjectsResponse,extra_headers, timeout_seconds)


    def list_projects(
        self, req: proto.agentlab.projects.v1.project_service_pb2.ListProjectsRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> proto.agentlab.projects.v1.project_service_pb2.ListProjectsResponse:
        response = self.call_list_projects(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_update_project(
        self, req: proto.agentlab.projects.v1.project_service_pb2.UpdateProjectRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[proto.agentlab.projects.v1.project_pb2.Project]:
        """Low-level method to call UpdateProject, granting access to errors and metadata"""
        url = self.base_url + "/agentlab.projects.v1.ProjectService/UpdateProject"
        return self._connect_client.call_unary(url, req, proto.agentlab.projects.v1.project_pb2.Project,extra_headers, timeout_seconds)


    def update_project(
        self, req: proto.agentlab.projects.v1.project_service_pb2.UpdateProjectRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> proto.agentlab.projects.v1.project_pb2.Project:
        response = self.call_update_project(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_delete_project(
        self, req: proto.agentlab.projects.v1.project_service_pb2.DeleteProjectRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[google.protobuf.empty_pb2.Empty]:
        """Low-level method to call DeleteProject, granting access to errors and metadata"""
        url = self.base_url + "/agentlab.projects.v1.ProjectService/DeleteProject"
        return self._connect_client.call_unary(url, req, google.protobuf.empty_pb2.Empty,extra_headers, timeout_seconds)


    def delete_project(
        self, req: proto.agentlab.projects.v1.project_service_pb2.DeleteProjectRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> google.protobuf.empty_pb2.Empty:
        response = self.call_delete_project(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg


class AsyncProjectServiceClient:
    def __init__(
        self,
        base_url: str,
        http_client: aiohttp.ClientSession,
        protocol: ConnectProtocol = ConnectProtocol.CONNECT_PROTOBUF,
    ):
        self.base_url = base_url
        self._connect_client = AsyncConnectClient(http_client, protocol)

    async def call_create_project(
        self, req: proto.agentlab.projects.v1.project_service_pb2.CreateProjectRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[proto.agentlab.projects.v1.project_pb2.Project]:
        """Low-level method to call CreateProject, granting access to errors and metadata"""
        url = self.base_url + "/agentlab.projects.v1.ProjectService/CreateProject"
        return await self._connect_client.call_unary(url, req, proto.agentlab.projects.v1.project_pb2.Project,extra_headers, timeout_seconds)

    async def create_project(
        self, req: proto.agentlab.projects.v1.project_service_pb2.CreateProjectRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> proto.agentlab.projects.v1.project_pb2.Project:
        response = await self.call_create_project(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_get_project(
        self, req: proto.agentlab.projects.v1.project_service_pb2.GetProjectRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[proto.agentlab.projects.v1.project_pb2.Project]:
        """Low-level method to call GetProject, granting access to errors and metadata"""
        url = self.base_url + "/agentlab.projects.v1.ProjectService/GetProject"
        return await self._connect_client.call_unary(url, req, proto.agentlab.projects.v1.project_pb2.Project,extra_headers, timeout_seconds)

    async def get_project(
        self, req: proto.agentlab.projects.v1.project_service_pb2.GetProjectRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> proto.agentlab.projects.v1.project_pb2.Project:
        response = await self.call_get_project(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_list_projects(
        self, req: proto.agentlab.projects.v1.project_service_pb2.ListProjectsRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[proto.agentlab.projects.v1.project_service_pb2.ListProjectsResponse]:
        """Low-level method to call ListProjects, granting access to errors and metadata"""
        url = self.base_url + "/agentlab.projects.v1.ProjectService/ListProjects"
        return await self._connect_client.call_unary(url, req, proto.agentlab.projects.v1.project_service_pb2.ListProjectsResponse,extra_headers, timeout_seconds)

    async def list_projects(
        self, req: proto.agentlab.projects.v1.project_service_pb2.ListProjectsRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> proto.agentlab.projects.v1.project_service_pb2.ListProjectsResponse:
        response = await self.call_list_projects(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_update_project(
        self, req: proto.agentlab.projects.v1.project_service_pb2.UpdateProjectRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[proto.agentlab.projects.v1.project_pb2.Project]:
        """Low-level method to call UpdateProject, granting access to errors and metadata"""
        url = self.base_url + "/agentlab.projects.v1.ProjectService/UpdateProject"
        return await self._connect_client.call_unary(url, req, proto.agentlab.projects.v1.project_pb2.Project,extra_headers, timeout_seconds)

    async def update_project(
        self, req: proto.agentlab.projects.v1.project_service_pb2.UpdateProjectRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> proto.agentlab.projects.v1.project_pb2.Project:
        response = await self.call_update_project(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_delete_project(
        self, req: proto.agentlab.projects.v1.project_service_pb2.DeleteProjectRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[google.protobuf.empty_pb2.Empty]:
        """Low-level method to call DeleteProject, granting access to errors and metadata"""
        url = self.base_url + "/agentlab.projects.v1.ProjectService/DeleteProject"
        return await self._connect_client.call_unary(url, req, google.protobuf.empty_pb2.Empty,extra_headers, timeout_seconds)

    async def delete_project(
        self, req: proto.agentlab.projects.v1.project_service_pb2.DeleteProjectRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> google.protobuf.empty_pb2.Empty:
        response = await self.call_delete_project(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg


@typing.runtime_checkable
class ProjectServiceProtocol(typing.Protocol):
    def create_project(self, req: ClientRequest[proto.agentlab.projects.v1.project_service_pb2.CreateProjectRequest]) -> ServerResponse[proto.agentlab.projects.v1.project_pb2.Project]:
        ...
    def get_project(self, req: ClientRequest[proto.agentlab.projects.v1.project_service_pb2.GetProjectRequest]) -> ServerResponse[proto.agentlab.projects.v1.project_pb2.Project]:
        ...
    def list_projects(self, req: ClientRequest[proto.agentlab.projects.v1.project_service_pb2.ListProjectsRequest]) -> ServerResponse[proto.agentlab.projects.v1.project_service_pb2.ListProjectsResponse]:
        ...
    def update_project(self, req: ClientRequest[proto.agentlab.projects.v1.project_service_pb2.UpdateProjectRequest]) -> ServerResponse[proto.agentlab.projects.v1.project_pb2.Project]:
        ...
    def delete_project(self, req: ClientRequest[proto.agentlab.projects.v1.project_service_pb2.DeleteProjectRequest]) -> ServerResponse[google.protobuf.empty_pb2.Empty]:
        ...

PROJECT_SERVICE_PATH_PREFIX = "/agentlab.projects.v1.ProjectService"

def wsgi_project_service(implementation: ProjectServiceProtocol) -> WSGIApplication:
    app = ConnectWSGI()
    app.register_unary_rpc("/agentlab.projects.v1.ProjectService/CreateProject", implementation.create_project, proto.agentlab.projects.v1.project_service_pb2.CreateProjectRequest)
    app.register_unary_rpc("/agentlab.projects.v1.ProjectService/GetProject", implementation.get_project, proto.agentlab.projects.v1.project_service_pb2.GetProjectRequest)
    app.register_unary_rpc("/agentlab.projects.v1.ProjectService/ListProjects", implementation.list_projects, proto.agentlab.projects.v1.project_service_pb2.ListProjectsRequest)
    app.register_unary_rpc("/agentlab.projects.v1.ProjectService/UpdateProject", implementation.update_project, proto.agentlab.projects.v1.project_service_pb2.UpdateProjectRequest)
    app.register_unary_rpc("/agentlab.projects.v1.ProjectService/DeleteProject", implementation.delete_project, proto.agentlab.projects.v1.project_service_pb2.DeleteProjectRequest)
    return app

# Generated Connect client code

from __future__ import annotations
from collections.abc import AsyncIterator
from collections.abc import Iterator
from collections.abc import Iterable
import aiohttp
import urllib3
import typing
import sys

from proto.connect_compat import AsyncConnectClient
from proto.connect_compat import ConnectClient
from proto.connect_compat import ConnectProtocol
from proto.connect_compat import ConnectProtocolError
from proto.connect_compat import HeaderInput
from proto.connect_compat import ClientRequest
from proto.connect_compat import ClientStream
from proto.connect_compat import ServerResponse
from proto.connect_compat import ServerStream
from proto.connect_compat import ConnectWSGI
from proto.connect_compat import StreamInput
from proto.connect_compat import AsyncStreamOutput
from proto.connect_compat import StreamOutput
from proto.connect_compat import UnaryOutput
from proto.connect_compat import ClientStreamingOutput

if typing.TYPE_CHECKING:
    # wsgiref.types was added in Python 3.11.
    if sys.version_info >= (3, 11):
        from wsgiref.types import WSGIApplication
    else:
        from _typeshed.wsgi import WSGIApplication

import google.protobuf.empty_pb2
import proto.agentlab.agent.v1.agent_pb2
import proto.agentlab.agent.v1.agent_service_pb2

class AgentServiceClient:
    def __init__(
        self,
        base_url: str,
        http_client: urllib3.PoolManager | None = None,
        protocol: ConnectProtocol = ConnectProtocol.CONNECT_PROTOBUF,
    ):
        self.base_url = base_url
        self._connect_client = ConnectClient(http_client, protocol)
    def call_create_agent(
        self, req: proto.agentlab.agent.v1.agent_service_pb2.CreateAgentRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[proto.agentlab.agent.v1.agent_pb2.Agent]:
        """Low-level method to call CreateAgent, granting access to errors and metadata"""
        url = self.base_url + "/agentlab.agent.v1.AgentService/CreateAgent"
        return self._connect_client.call_unary(url, req, proto.agentlab.agent.v1.agent_pb2.Agent,extra_headers, timeout_seconds)


    def create_agent(
        self, req: proto.agentlab.agent.v1.agent_service_pb2.CreateAgentRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> proto.agentlab.agent.v1.agent_pb2.Agent:
        response = self.call_create_agent(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_get_agent(
        self, req: proto.agentlab.agent.v1.agent_service_pb2.GetAgentRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[proto.agentlab.agent.v1.agent_pb2.Agent]:
        """Low-level method to call GetAgent, granting access to errors and metadata"""
        url = self.base_url + "/agentlab.agent.v1.AgentService/GetAgent"
        return self._connect_client.call_unary(url, req, proto.agentlab.agent.v1.agent_pb2.Agent,extra_headers, timeout_seconds)


    def get_agent(
        self, req: proto.agentlab.agent.v1.agent_service_pb2.GetAgentRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> proto.agentlab.agent.v1.agent_pb2.Agent:
        response = self.call_get_agent(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_list_agents(
        self, req: proto.agentlab.agent.v1.agent_service_pb2.ListAgentsRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[proto.agentlab.agent.v1.agent_service_pb2.ListAgentsResponse]:
        """Low-level method to call ListAgents, granting access to errors and metadata"""
        url = self.base_url + "/agentlab.agent.v1.AgentService/ListAgents"
        return self._connect_client.call_unary(url, req, proto.agentlab.agent.v1.agent_service_pb2.ListAgentsResponse,extra_headers, timeout_seconds)


    def list_agents(
        self, req: proto.agentlab.agent.v1.agent_service_pb2.ListAgentsRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> proto.agentlab.agent.v1.agent_service_pb2.ListAgentsResponse:
        response = self.call_list_agents(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_update_agent(
        self, req: proto.agentlab.agent.v1.agent_service_pb2.UpdateAgentRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[proto.agentlab.agent.v1.agent_pb2.Agent]:
        """Low-level method to call UpdateAgent, granting access to errors and metadata"""
        url = self.base_url + "/agentlab.agent.v1.AgentService/UpdateAgent"
        return self._connect_client.call_unary(url, req, proto.agentlab.agent.v1.agent_pb2.Agent,extra_headers, timeout_seconds)


    def update_agent(
        self, req: proto.agentlab.agent.v1.agent_service_pb2.UpdateAgentRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> proto.agentlab.agent.v1.agent_pb2.Agent:
        response = self.call_update_agent(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_delete_agent(
        self, req: proto.agentlab.agent.v1.agent_service_pb2.DeleteAgentRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[google.protobuf.empty_pb2.Empty]:
        """Low-level method to call DeleteAgent, granting access to errors and metadata"""
        url = self.base_url + "/agentlab.agent.v1.AgentService/DeleteAgent"
        return self._connect_client.call_unary(url, req, google.protobuf.empty_pb2.Empty,extra_headers, timeout_seconds)


    def delete_agent(
        self, req: proto.agentlab.agent.v1.agent_service_pb2.DeleteAgentRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> google.protobuf.empty_pb2.Empty:
        response = self.call_delete_agent(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_get_agent_version(
        self, req: proto.agentlab.agent.v1.agent_service_pb2.GetAgentVersionRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[proto.agentlab.agent.v1.agent_pb2.AgentVersion]:
        """Low-level method to call GetAgentVersion, granting access to errors and metadata"""
        url = self.base_url + "/agentlab.agent.v1.AgentService/GetAgentVersion"
        return self._connect_client.call_unary(url, req, proto.agentlab.agent.v1.agent_pb2.AgentVersion,extra_headers, timeout_seconds)


    def get_agent_version(
        self, req: proto.agentlab.agent.v1.agent_service_pb2.GetAgentVersionRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> proto.agentlab.agent.v1.agent_pb2.AgentVersion:
        response = self.call_get_agent_version(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_list_agent_versions(
        self, req: proto.agentlab.agent.v1.agent_service_pb2.ListAgentVersionsRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[proto.agentlab.agent.v1.agent_service_pb2.ListAgentVersionsResponse]:
        """Low-level method to call ListAgentVersions, granting access to errors and metadata"""
        url = self.base_url + "/agentlab.agent.v1.AgentService/ListAgentVersions"
        return self._connect_client.call_unary(url, req, proto.agentlab.agent.v1.agent_service_pb2.ListAgentVersionsResponse,extra_headers, timeout_seconds)


    def list_agent_versions(
        self, req: proto.agentlab.agent.v1.agent_service_pb2.ListAgentVersionsRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> proto.agentlab.agent.v1.agent_service_pb2.ListAgentVersionsResponse:
        response = self.call_list_agent_versions(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_delete_agent_version(
        self, req: proto.agentlab.agent.v1.agent_service_pb2.DeleteAgentVersionRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[google.protobuf.empty_pb2.Empty]:
        """Low-level method to call DeleteAgentVersion, granting access to errors and metadata"""
        url = self.base_url + "/agentlab.agent.v1.AgentService/DeleteAgentVersion"
        return self._connect_client.call_unary(url, req, google.protobuf.empty_pb2.Empty,extra_headers, timeout_seconds)


    def delete_agent_version(
        self, req: proto.agentlab.agent.v1.agent_service_pb2.DeleteAgentVersionRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> google.protobuf.empty_pb2.Empty:
        response = self.call_delete_agent_version(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_publish_agent_version(
        self, req: proto.agentlab.agent.v1.agent_service_pb2.PublishAgentVersionRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[proto.agentlab.agent.v1.agent_pb2.AgentVersion]:
        """Low-level method to call PublishAgentVersion, granting access to errors and metadata"""
        url = self.base_url + "/agentlab.agent.v1.AgentService/PublishAgentVersion"
        return self._connect_client.call_unary(url, req, proto.agentlab.agent.v1.agent_pb2.AgentVersion,extra_headers, timeout_seconds)


    def publish_agent_version(
        self, req: proto.agentlab.agent.v1.agent_service_pb2.PublishAgentVersionRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> proto.agentlab.agent.v1.agent_pb2.AgentVersion:
        response = self.call_publish_agent_version(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_create_agent_version(
        self, req: proto.agentlab.agent.v1.agent_service_pb2.CreateAgentVersionRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[proto.agentlab.agent.v1.agent_pb2.AgentVersion]:
        """Low-level method to call CreateAgentVersion, granting access to errors and metadata"""
        url = self.base_url + "/agentlab.agent.v1.AgentService/CreateAgentVersion"
        return self._connect_client.call_unary(url, req, proto.agentlab.agent.v1.agent_pb2.AgentVersion,extra_headers, timeout_seconds)


    def create_agent_version(
        self, req: proto.agentlab.agent.v1.agent_service_pb2.CreateAgentVersionRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> proto.agentlab.agent.v1.agent_pb2.AgentVersion:
        response = self.call_create_agent_version(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_update_agent_version(
        self, req: proto.agentlab.agent.v1.agent_service_pb2.UpdateAgentVersionRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[proto.agentlab.agent.v1.agent_pb2.AgentVersion]:
        """Low-level method to call UpdateAgentVersion, granting access to errors and metadata"""
        url = self.base_url + "/agentlab.agent.v1.AgentService/UpdateAgentVersion"
        return self._connect_client.call_unary(url, req, proto.agentlab.agent.v1.agent_pb2.AgentVersion,extra_headers, timeout_seconds)


    def update_agent_version(
        self, req: proto.agentlab.agent.v1.agent_service_pb2.UpdateAgentVersionRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> proto.agentlab.agent.v1.agent_pb2.AgentVersion:
        response = self.call_update_agent_version(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_generate_version_diff(
        self, req: proto.agentlab.agent.v1.agent_service_pb2.GenerateVersionDiffRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[proto.agentlab.agent.v1.agent_pb2.AgentVersionDiff]:
        """Low-level method to call GenerateVersionDiff, granting access to errors and metadata"""
        url = self.base_url + "/agentlab.agent.v1.AgentService/GenerateVersionDiff"
        return self._connect_client.call_unary(url, req, proto.agentlab.agent.v1.agent_pb2.AgentVersionDiff,extra_headers, timeout_seconds)


    def generate_version_diff(
        self, req: proto.agentlab.agent.v1.agent_service_pb2.GenerateVersionDiffRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> proto.agentlab.agent.v1.agent_pb2.AgentVersionDiff:
        response = self.call_generate_version_diff(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_generate_version_diff_legacy(
        self, req: proto.agentlab.agent.v1.agent_service_pb2.GenerateVersionDiffLegacyRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[proto.agentlab.agent.v1.agent_pb2.AgentVersionDiff]:
        """Low-level method to call GenerateVersionDiffLegacy, granting access to errors and metadata"""
        url = self.base_url + "/agentlab.agent.v1.AgentService/GenerateVersionDiffLegacy"
        return self._connect_client.call_unary(url, req, proto.agentlab.agent.v1.agent_pb2.AgentVersionDiff,extra_headers, timeout_seconds)


    def generate_version_diff_legacy(
        self, req: proto.agentlab.agent.v1.agent_service_pb2.GenerateVersionDiffLegacyRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> proto.agentlab.agent.v1.agent_pb2.AgentVersionDiff:
        response = self.call_generate_version_diff_legacy(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg


class AsyncAgentServiceClient:
    def __init__(
        self,
        base_url: str,
        http_client: aiohttp.ClientSession,
        protocol: ConnectProtocol = ConnectProtocol.CONNECT_PROTOBUF,
    ):
        self.base_url = base_url
        self._connect_client = AsyncConnectClient(http_client, protocol)

    async def call_create_agent(
        self, req: proto.agentlab.agent.v1.agent_service_pb2.CreateAgentRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[proto.agentlab.agent.v1.agent_pb2.Agent]:
        """Low-level method to call CreateAgent, granting access to errors and metadata"""
        url = self.base_url + "/agentlab.agent.v1.AgentService/CreateAgent"
        return await self._connect_client.call_unary(url, req, proto.agentlab.agent.v1.agent_pb2.Agent,extra_headers, timeout_seconds)

    async def create_agent(
        self, req: proto.agentlab.agent.v1.agent_service_pb2.CreateAgentRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> proto.agentlab.agent.v1.agent_pb2.Agent:
        response = await self.call_create_agent(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_get_agent(
        self, req: proto.agentlab.agent.v1.agent_service_pb2.GetAgentRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[proto.agentlab.agent.v1.agent_pb2.Agent]:
        """Low-level method to call GetAgent, granting access to errors and metadata"""
        url = self.base_url + "/agentlab.agent.v1.AgentService/GetAgent"
        return await self._connect_client.call_unary(url, req, proto.agentlab.agent.v1.agent_pb2.Agent,extra_headers, timeout_seconds)

    async def get_agent(
        self, req: proto.agentlab.agent.v1.agent_service_pb2.GetAgentRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> proto.agentlab.agent.v1.agent_pb2.Agent:
        response = await self.call_get_agent(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_list_agents(
        self, req: proto.agentlab.agent.v1.agent_service_pb2.ListAgentsRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[proto.agentlab.agent.v1.agent_service_pb2.ListAgentsResponse]:
        """Low-level method to call ListAgents, granting access to errors and metadata"""
        url = self.base_url + "/agentlab.agent.v1.AgentService/ListAgents"
        return await self._connect_client.call_unary(url, req, proto.agentlab.agent.v1.agent_service_pb2.ListAgentsResponse,extra_headers, timeout_seconds)

    async def list_agents(
        self, req: proto.agentlab.agent.v1.agent_service_pb2.ListAgentsRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> proto.agentlab.agent.v1.agent_service_pb2.ListAgentsResponse:
        response = await self.call_list_agents(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_update_agent(
        self, req: proto.agentlab.agent.v1.agent_service_pb2.UpdateAgentRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[proto.agentlab.agent.v1.agent_pb2.Agent]:
        """Low-level method to call UpdateAgent, granting access to errors and metadata"""
        url = self.base_url + "/agentlab.agent.v1.AgentService/UpdateAgent"
        return await self._connect_client.call_unary(url, req, proto.agentlab.agent.v1.agent_pb2.Agent,extra_headers, timeout_seconds)

    async def update_agent(
        self, req: proto.agentlab.agent.v1.agent_service_pb2.UpdateAgentRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> proto.agentlab.agent.v1.agent_pb2.Agent:
        response = await self.call_update_agent(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_delete_agent(
        self, req: proto.agentlab.agent.v1.agent_service_pb2.DeleteAgentRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[google.protobuf.empty_pb2.Empty]:
        """Low-level method to call DeleteAgent, granting access to errors and metadata"""
        url = self.base_url + "/agentlab.agent.v1.AgentService/DeleteAgent"
        return await self._connect_client.call_unary(url, req, google.protobuf.empty_pb2.Empty,extra_headers, timeout_seconds)

    async def delete_agent(
        self, req: proto.agentlab.agent.v1.agent_service_pb2.DeleteAgentRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> google.protobuf.empty_pb2.Empty:
        response = await self.call_delete_agent(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_get_agent_version(
        self, req: proto.agentlab.agent.v1.agent_service_pb2.GetAgentVersionRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[proto.agentlab.agent.v1.agent_pb2.AgentVersion]:
        """Low-level method to call GetAgentVersion, granting access to errors and metadata"""
        url = self.base_url + "/agentlab.agent.v1.AgentService/GetAgentVersion"
        return await self._connect_client.call_unary(url, req, proto.agentlab.agent.v1.agent_pb2.AgentVersion,extra_headers, timeout_seconds)

    async def get_agent_version(
        self, req: proto.agentlab.agent.v1.agent_service_pb2.GetAgentVersionRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> proto.agentlab.agent.v1.agent_pb2.AgentVersion:
        response = await self.call_get_agent_version(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_list_agent_versions(
        self, req: proto.agentlab.agent.v1.agent_service_pb2.ListAgentVersionsRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[proto.agentlab.agent.v1.agent_service_pb2.ListAgentVersionsResponse]:
        """Low-level method to call ListAgentVersions, granting access to errors and metadata"""
        url = self.base_url + "/agentlab.agent.v1.AgentService/ListAgentVersions"
        return await self._connect_client.call_unary(url, req, proto.agentlab.agent.v1.agent_service_pb2.ListAgentVersionsResponse,extra_headers, timeout_seconds)

    async def list_agent_versions(
        self, req: proto.agentlab.agent.v1.agent_service_pb2.ListAgentVersionsRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> proto.agentlab.agent.v1.agent_service_pb2.ListAgentVersionsResponse:
        response = await self.call_list_agent_versions(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_delete_agent_version(
        self, req: proto.agentlab.agent.v1.agent_service_pb2.DeleteAgentVersionRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[google.protobuf.empty_pb2.Empty]:
        """Low-level method to call DeleteAgentVersion, granting access to errors and metadata"""
        url = self.base_url + "/agentlab.agent.v1.AgentService/DeleteAgentVersion"
        return await self._connect_client.call_unary(url, req, google.protobuf.empty_pb2.Empty,extra_headers, timeout_seconds)

    async def delete_agent_version(
        self, req: proto.agentlab.agent.v1.agent_service_pb2.DeleteAgentVersionRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> google.protobuf.empty_pb2.Empty:
        response = await self.call_delete_agent_version(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_publish_agent_version(
        self, req: proto.agentlab.agent.v1.agent_service_pb2.PublishAgentVersionRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[proto.agentlab.agent.v1.agent_pb2.AgentVersion]:
        """Low-level method to call PublishAgentVersion, granting access to errors and metadata"""
        url = self.base_url + "/agentlab.agent.v1.AgentService/PublishAgentVersion"
        return await self._connect_client.call_unary(url, req, proto.agentlab.agent.v1.agent_pb2.AgentVersion,extra_headers, timeout_seconds)

    async def publish_agent_version(
        self, req: proto.agentlab.agent.v1.agent_service_pb2.PublishAgentVersionRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> proto.agentlab.agent.v1.agent_pb2.AgentVersion:
        response = await self.call_publish_agent_version(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_create_agent_version(
        self, req: proto.agentlab.agent.v1.agent_service_pb2.CreateAgentVersionRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[proto.agentlab.agent.v1.agent_pb2.AgentVersion]:
        """Low-level method to call CreateAgentVersion, granting access to errors and metadata"""
        url = self.base_url + "/agentlab.agent.v1.AgentService/CreateAgentVersion"
        return await self._connect_client.call_unary(url, req, proto.agentlab.agent.v1.agent_pb2.AgentVersion,extra_headers, timeout_seconds)

    async def create_agent_version(
        self, req: proto.agentlab.agent.v1.agent_service_pb2.CreateAgentVersionRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> proto.agentlab.agent.v1.agent_pb2.AgentVersion:
        response = await self.call_create_agent_version(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_update_agent_version(
        self, req: proto.agentlab.agent.v1.agent_service_pb2.UpdateAgentVersionRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[proto.agentlab.agent.v1.agent_pb2.AgentVersion]:
        """Low-level method to call UpdateAgentVersion, granting access to errors and metadata"""
        url = self.base_url + "/agentlab.agent.v1.AgentService/UpdateAgentVersion"
        return await self._connect_client.call_unary(url, req, proto.agentlab.agent.v1.agent_pb2.AgentVersion,extra_headers, timeout_seconds)

    async def update_agent_version(
        self, req: proto.agentlab.agent.v1.agent_service_pb2.UpdateAgentVersionRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> proto.agentlab.agent.v1.agent_pb2.AgentVersion:
        response = await self.call_update_agent_version(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_generate_version_diff(
        self, req: proto.agentlab.agent.v1.agent_service_pb2.GenerateVersionDiffRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[proto.agentlab.agent.v1.agent_pb2.AgentVersionDiff]:
        """Low-level method to call GenerateVersionDiff, granting access to errors and metadata"""
        url = self.base_url + "/agentlab.agent.v1.AgentService/GenerateVersionDiff"
        return await self._connect_client.call_unary(url, req, proto.agentlab.agent.v1.agent_pb2.AgentVersionDiff,extra_headers, timeout_seconds)

    async def generate_version_diff(
        self, req: proto.agentlab.agent.v1.agent_service_pb2.GenerateVersionDiffRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> proto.agentlab.agent.v1.agent_pb2.AgentVersionDiff:
        response = await self.call_generate_version_diff(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_generate_version_diff_legacy(
        self, req: proto.agentlab.agent.v1.agent_service_pb2.GenerateVersionDiffLegacyRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[proto.agentlab.agent.v1.agent_pb2.AgentVersionDiff]:
        """Low-level method to call GenerateVersionDiffLegacy, granting access to errors and metadata"""
        url = self.base_url + "/agentlab.agent.v1.AgentService/GenerateVersionDiffLegacy"
        return await self._connect_client.call_unary(url, req, proto.agentlab.agent.v1.agent_pb2.AgentVersionDiff,extra_headers, timeout_seconds)

    async def generate_version_diff_legacy(
        self, req: proto.agentlab.agent.v1.agent_service_pb2.GenerateVersionDiffLegacyRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> proto.agentlab.agent.v1.agent_pb2.AgentVersionDiff:
        response = await self.call_generate_version_diff_legacy(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg


@typing.runtime_checkable
class AgentServiceProtocol(typing.Protocol):
    def create_agent(self, req: ClientRequest[proto.agentlab.agent.v1.agent_service_pb2.CreateAgentRequest]) -> ServerResponse[proto.agentlab.agent.v1.agent_pb2.Agent]:
        ...
    def get_agent(self, req: ClientRequest[proto.agentlab.agent.v1.agent_service_pb2.GetAgentRequest]) -> ServerResponse[proto.agentlab.agent.v1.agent_pb2.Agent]:
        ...
    def list_agents(self, req: ClientRequest[proto.agentlab.agent.v1.agent_service_pb2.ListAgentsRequest]) -> ServerResponse[proto.agentlab.agent.v1.agent_service_pb2.ListAgentsResponse]:
        ...
    def update_agent(self, req: ClientRequest[proto.agentlab.agent.v1.agent_service_pb2.UpdateAgentRequest]) -> ServerResponse[proto.agentlab.agent.v1.agent_pb2.Agent]:
        ...
    def delete_agent(self, req: ClientRequest[proto.agentlab.agent.v1.agent_service_pb2.DeleteAgentRequest]) -> ServerResponse[google.protobuf.empty_pb2.Empty]:
        ...
    def get_agent_version(self, req: ClientRequest[proto.agentlab.agent.v1.agent_service_pb2.GetAgentVersionRequest]) -> ServerResponse[proto.agentlab.agent.v1.agent_pb2.AgentVersion]:
        ...
    def list_agent_versions(self, req: ClientRequest[proto.agentlab.agent.v1.agent_service_pb2.ListAgentVersionsRequest]) -> ServerResponse[proto.agentlab.agent.v1.agent_service_pb2.ListAgentVersionsResponse]:
        ...
    def delete_agent_version(self, req: ClientRequest[proto.agentlab.agent.v1.agent_service_pb2.DeleteAgentVersionRequest]) -> ServerResponse[google.protobuf.empty_pb2.Empty]:
        ...
    def publish_agent_version(self, req: ClientRequest[proto.agentlab.agent.v1.agent_service_pb2.PublishAgentVersionRequest]) -> ServerResponse[proto.agentlab.agent.v1.agent_pb2.AgentVersion]:
        ...
    def create_agent_version(self, req: ClientRequest[proto.agentlab.agent.v1.agent_service_pb2.CreateAgentVersionRequest]) -> ServerResponse[proto.agentlab.agent.v1.agent_pb2.AgentVersion]:
        ...
    def update_agent_version(self, req: ClientRequest[proto.agentlab.agent.v1.agent_service_pb2.UpdateAgentVersionRequest]) -> ServerResponse[proto.agentlab.agent.v1.agent_pb2.AgentVersion]:
        ...
    def generate_version_diff(self, req: ClientRequest[proto.agentlab.agent.v1.agent_service_pb2.GenerateVersionDiffRequest]) -> ServerResponse[proto.agentlab.agent.v1.agent_pb2.AgentVersionDiff]:
        ...
    def generate_version_diff_legacy(self, req: ClientRequest[proto.agentlab.agent.v1.agent_service_pb2.GenerateVersionDiffLegacyRequest]) -> ServerResponse[proto.agentlab.agent.v1.agent_pb2.AgentVersionDiff]:
        ...

AGENT_SERVICE_PATH_PREFIX = "/agentlab.agent.v1.AgentService"

def wsgi_agent_service(implementation: AgentServiceProtocol) -> WSGIApplication:
    app = ConnectWSGI()
    app.register_unary_rpc("/agentlab.agent.v1.AgentService/CreateAgent", implementation.create_agent, proto.agentlab.agent.v1.agent_service_pb2.CreateAgentRequest)
    app.register_unary_rpc("/agentlab.agent.v1.AgentService/GetAgent", implementation.get_agent, proto.agentlab.agent.v1.agent_service_pb2.GetAgentRequest)
    app.register_unary_rpc("/agentlab.agent.v1.AgentService/ListAgents", implementation.list_agents, proto.agentlab.agent.v1.agent_service_pb2.ListAgentsRequest)
    app.register_unary_rpc("/agentlab.agent.v1.AgentService/UpdateAgent", implementation.update_agent, proto.agentlab.agent.v1.agent_service_pb2.UpdateAgentRequest)
    app.register_unary_rpc("/agentlab.agent.v1.AgentService/DeleteAgent", implementation.delete_agent, proto.agentlab.agent.v1.agent_service_pb2.DeleteAgentRequest)
    app.register_unary_rpc("/agentlab.agent.v1.AgentService/GetAgentVersion", implementation.get_agent_version, proto.agentlab.agent.v1.agent_service_pb2.GetAgentVersionRequest)
    app.register_unary_rpc("/agentlab.agent.v1.AgentService/ListAgentVersions", implementation.list_agent_versions, proto.agentlab.agent.v1.agent_service_pb2.ListAgentVersionsRequest)
    app.register_unary_rpc("/agentlab.agent.v1.AgentService/DeleteAgentVersion", implementation.delete_agent_version, proto.agentlab.agent.v1.agent_service_pb2.DeleteAgentVersionRequest)
    app.register_unary_rpc("/agentlab.agent.v1.AgentService/PublishAgentVersion", implementation.publish_agent_version, proto.agentlab.agent.v1.agent_service_pb2.PublishAgentVersionRequest)
    app.register_unary_rpc("/agentlab.agent.v1.AgentService/CreateAgentVersion", implementation.create_agent_version, proto.agentlab.agent.v1.agent_service_pb2.CreateAgentVersionRequest)
    app.register_unary_rpc("/agentlab.agent.v1.AgentService/UpdateAgentVersion", implementation.update_agent_version, proto.agentlab.agent.v1.agent_service_pb2.UpdateAgentVersionRequest)
    app.register_unary_rpc("/agentlab.agent.v1.AgentService/GenerateVersionDiff", implementation.generate_version_diff, proto.agentlab.agent.v1.agent_service_pb2.GenerateVersionDiffRequest)
    app.register_unary_rpc("/agentlab.agent.v1.AgentService/GenerateVersionDiffLegacy", implementation.generate_version_diff_legacy, proto.agentlab.agent.v1.agent_service_pb2.GenerateVersionDiffLegacyRequest)
    return app

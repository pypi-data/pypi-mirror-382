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

import proto.agentlab.analysis.v1.analysis_service_pb2

class AgentAnalysisServiceClient:
    def __init__(
        self,
        base_url: str,
        http_client: urllib3.PoolManager | None = None,
        protocol: ConnectProtocol = ConnectProtocol.CONNECT_PROTOBUF,
    ):
        self.base_url = base_url
        self._connect_client = ConnectClient(http_client, protocol)
    def call_analyze_agent(
        self, req: proto.agentlab.analysis.v1.analysis_service_pb2.AnalyzeAgentRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[proto.agentlab.analysis.v1.analysis_service_pb2.AnalyzeAgentResponse]:
        """Low-level method to call AnalyzeAgent, granting access to errors and metadata"""
        url = self.base_url + "/agentlab.analysis.v1.AgentAnalysisService/AnalyzeAgent"
        return self._connect_client.call_unary(url, req, proto.agentlab.analysis.v1.analysis_service_pb2.AnalyzeAgentResponse,extra_headers, timeout_seconds)


    def analyze_agent(
        self, req: proto.agentlab.analysis.v1.analysis_service_pb2.AnalyzeAgentRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> proto.agentlab.analysis.v1.analysis_service_pb2.AnalyzeAgentResponse:
        response = self.call_analyze_agent(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_get_analysis_session(
        self, req: proto.agentlab.analysis.v1.analysis_service_pb2.GetAnalysisSessionRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[proto.agentlab.analysis.v1.analysis_service_pb2.AnalysisSession]:
        """Low-level method to call GetAnalysisSession, granting access to errors and metadata"""
        url = self.base_url + "/agentlab.analysis.v1.AgentAnalysisService/GetAnalysisSession"
        return self._connect_client.call_unary(url, req, proto.agentlab.analysis.v1.analysis_service_pb2.AnalysisSession,extra_headers, timeout_seconds)


    def get_analysis_session(
        self, req: proto.agentlab.analysis.v1.analysis_service_pb2.GetAnalysisSessionRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> proto.agentlab.analysis.v1.analysis_service_pb2.AnalysisSession:
        response = self.call_get_analysis_session(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_list_analysis_sessions(
        self, req: proto.agentlab.analysis.v1.analysis_service_pb2.ListAnalysisSessionsRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[proto.agentlab.analysis.v1.analysis_service_pb2.ListAnalysisSessionsResponse]:
        """Low-level method to call ListAnalysisSessions, granting access to errors and metadata"""
        url = self.base_url + "/agentlab.analysis.v1.AgentAnalysisService/ListAnalysisSessions"
        return self._connect_client.call_unary(url, req, proto.agentlab.analysis.v1.analysis_service_pb2.ListAnalysisSessionsResponse,extra_headers, timeout_seconds)


    def list_analysis_sessions(
        self, req: proto.agentlab.analysis.v1.analysis_service_pb2.ListAnalysisSessionsRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> proto.agentlab.analysis.v1.analysis_service_pb2.ListAnalysisSessionsResponse:
        response = self.call_list_analysis_sessions(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg


class AsyncAgentAnalysisServiceClient:
    def __init__(
        self,
        base_url: str,
        http_client: aiohttp.ClientSession,
        protocol: ConnectProtocol = ConnectProtocol.CONNECT_PROTOBUF,
    ):
        self.base_url = base_url
        self._connect_client = AsyncConnectClient(http_client, protocol)

    async def call_analyze_agent(
        self, req: proto.agentlab.analysis.v1.analysis_service_pb2.AnalyzeAgentRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[proto.agentlab.analysis.v1.analysis_service_pb2.AnalyzeAgentResponse]:
        """Low-level method to call AnalyzeAgent, granting access to errors and metadata"""
        url = self.base_url + "/agentlab.analysis.v1.AgentAnalysisService/AnalyzeAgent"
        return await self._connect_client.call_unary(url, req, proto.agentlab.analysis.v1.analysis_service_pb2.AnalyzeAgentResponse,extra_headers, timeout_seconds)

    async def analyze_agent(
        self, req: proto.agentlab.analysis.v1.analysis_service_pb2.AnalyzeAgentRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> proto.agentlab.analysis.v1.analysis_service_pb2.AnalyzeAgentResponse:
        response = await self.call_analyze_agent(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_get_analysis_session(
        self, req: proto.agentlab.analysis.v1.analysis_service_pb2.GetAnalysisSessionRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[proto.agentlab.analysis.v1.analysis_service_pb2.AnalysisSession]:
        """Low-level method to call GetAnalysisSession, granting access to errors and metadata"""
        url = self.base_url + "/agentlab.analysis.v1.AgentAnalysisService/GetAnalysisSession"
        return await self._connect_client.call_unary(url, req, proto.agentlab.analysis.v1.analysis_service_pb2.AnalysisSession,extra_headers, timeout_seconds)

    async def get_analysis_session(
        self, req: proto.agentlab.analysis.v1.analysis_service_pb2.GetAnalysisSessionRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> proto.agentlab.analysis.v1.analysis_service_pb2.AnalysisSession:
        response = await self.call_get_analysis_session(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_list_analysis_sessions(
        self, req: proto.agentlab.analysis.v1.analysis_service_pb2.ListAnalysisSessionsRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[proto.agentlab.analysis.v1.analysis_service_pb2.ListAnalysisSessionsResponse]:
        """Low-level method to call ListAnalysisSessions, granting access to errors and metadata"""
        url = self.base_url + "/agentlab.analysis.v1.AgentAnalysisService/ListAnalysisSessions"
        return await self._connect_client.call_unary(url, req, proto.agentlab.analysis.v1.analysis_service_pb2.ListAnalysisSessionsResponse,extra_headers, timeout_seconds)

    async def list_analysis_sessions(
        self, req: proto.agentlab.analysis.v1.analysis_service_pb2.ListAnalysisSessionsRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> proto.agentlab.analysis.v1.analysis_service_pb2.ListAnalysisSessionsResponse:
        response = await self.call_list_analysis_sessions(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg


@typing.runtime_checkable
class AgentAnalysisServiceProtocol(typing.Protocol):
    def analyze_agent(self, req: ClientRequest[proto.agentlab.analysis.v1.analysis_service_pb2.AnalyzeAgentRequest]) -> ServerResponse[proto.agentlab.analysis.v1.analysis_service_pb2.AnalyzeAgentResponse]:
        ...
    def get_analysis_session(self, req: ClientRequest[proto.agentlab.analysis.v1.analysis_service_pb2.GetAnalysisSessionRequest]) -> ServerResponse[proto.agentlab.analysis.v1.analysis_service_pb2.AnalysisSession]:
        ...
    def list_analysis_sessions(self, req: ClientRequest[proto.agentlab.analysis.v1.analysis_service_pb2.ListAnalysisSessionsRequest]) -> ServerResponse[proto.agentlab.analysis.v1.analysis_service_pb2.ListAnalysisSessionsResponse]:
        ...

AGENT_ANALYSIS_SERVICE_PATH_PREFIX = "/agentlab.analysis.v1.AgentAnalysisService"

def wsgi_agent_analysis_service(implementation: AgentAnalysisServiceProtocol) -> WSGIApplication:
    app = ConnectWSGI()
    app.register_unary_rpc("/agentlab.analysis.v1.AgentAnalysisService/AnalyzeAgent", implementation.analyze_agent, proto.agentlab.analysis.v1.analysis_service_pb2.AnalyzeAgentRequest)
    app.register_unary_rpc("/agentlab.analysis.v1.AgentAnalysisService/GetAnalysisSession", implementation.get_analysis_session, proto.agentlab.analysis.v1.analysis_service_pb2.GetAnalysisSessionRequest)
    app.register_unary_rpc("/agentlab.analysis.v1.AgentAnalysisService/ListAnalysisSessions", implementation.list_analysis_sessions, proto.agentlab.analysis.v1.analysis_service_pb2.ListAnalysisSessionsRequest)
    return app

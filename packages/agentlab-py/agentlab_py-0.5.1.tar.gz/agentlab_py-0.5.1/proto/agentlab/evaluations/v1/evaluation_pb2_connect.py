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

import proto.agentlab.evaluations.v1.evaluation_pb2

class EvaluationServiceClient:
    def __init__(
        self,
        base_url: str,
        http_client: urllib3.PoolManager | None = None,
        protocol: ConnectProtocol = ConnectProtocol.CONNECT_PROTOBUF,
    ):
        self.base_url = base_url
        self._connect_client = ConnectClient(http_client, protocol)
    def call_list_evaluators(
        self, req: proto.agentlab.evaluations.v1.evaluation_pb2.ListEvaluatorsRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[proto.agentlab.evaluations.v1.evaluation_pb2.ListEvaluatorsResponse]:
        """Low-level method to call ListEvaluators, granting access to errors and metadata"""
        url = self.base_url + "/agentlab.evaluations.v1.EvaluationService/ListEvaluators"
        return self._connect_client.call_unary(url, req, proto.agentlab.evaluations.v1.evaluation_pb2.ListEvaluatorsResponse,extra_headers, timeout_seconds)


    def list_evaluators(
        self, req: proto.agentlab.evaluations.v1.evaluation_pb2.ListEvaluatorsRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> proto.agentlab.evaluations.v1.evaluation_pb2.ListEvaluatorsResponse:
        response = self.call_list_evaluators(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_get_evaluator(
        self, req: proto.agentlab.evaluations.v1.evaluation_pb2.GetEvaluatorRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[proto.agentlab.evaluations.v1.evaluation_pb2.Evaluator]:
        """Low-level method to call GetEvaluator, granting access to errors and metadata"""
        url = self.base_url + "/agentlab.evaluations.v1.EvaluationService/GetEvaluator"
        return self._connect_client.call_unary(url, req, proto.agentlab.evaluations.v1.evaluation_pb2.Evaluator,extra_headers, timeout_seconds)


    def get_evaluator(
        self, req: proto.agentlab.evaluations.v1.evaluation_pb2.GetEvaluatorRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> proto.agentlab.evaluations.v1.evaluation_pb2.Evaluator:
        response = self.call_get_evaluator(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_run_evaluation(
        self, req: proto.agentlab.evaluations.v1.evaluation_pb2.RunEvaluationRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[proto.agentlab.evaluations.v1.evaluation_pb2.EvaluationRun]:
        """Low-level method to call RunEvaluation, granting access to errors and metadata"""
        url = self.base_url + "/agentlab.evaluations.v1.EvaluationService/RunEvaluation"
        return self._connect_client.call_unary(url, req, proto.agentlab.evaluations.v1.evaluation_pb2.EvaluationRun,extra_headers, timeout_seconds)


    def run_evaluation(
        self, req: proto.agentlab.evaluations.v1.evaluation_pb2.RunEvaluationRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> proto.agentlab.evaluations.v1.evaluation_pb2.EvaluationRun:
        response = self.call_run_evaluation(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_get_evaluation_run(
        self, req: proto.agentlab.evaluations.v1.evaluation_pb2.GetEvaluationRunRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[proto.agentlab.evaluations.v1.evaluation_pb2.EvaluationRun]:
        """Low-level method to call GetEvaluationRun, granting access to errors and metadata"""
        url = self.base_url + "/agentlab.evaluations.v1.EvaluationService/GetEvaluationRun"
        return self._connect_client.call_unary(url, req, proto.agentlab.evaluations.v1.evaluation_pb2.EvaluationRun,extra_headers, timeout_seconds)


    def get_evaluation_run(
        self, req: proto.agentlab.evaluations.v1.evaluation_pb2.GetEvaluationRunRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> proto.agentlab.evaluations.v1.evaluation_pb2.EvaluationRun:
        response = self.call_get_evaluation_run(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_list_evaluation_runs(
        self, req: proto.agentlab.evaluations.v1.evaluation_pb2.ListEvaluationRunsRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[proto.agentlab.evaluations.v1.evaluation_pb2.ListEvaluationRunsResponse]:
        """Low-level method to call ListEvaluationRuns, granting access to errors and metadata"""
        url = self.base_url + "/agentlab.evaluations.v1.EvaluationService/ListEvaluationRuns"
        return self._connect_client.call_unary(url, req, proto.agentlab.evaluations.v1.evaluation_pb2.ListEvaluationRunsResponse,extra_headers, timeout_seconds)


    def list_evaluation_runs(
        self, req: proto.agentlab.evaluations.v1.evaluation_pb2.ListEvaluationRunsRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> proto.agentlab.evaluations.v1.evaluation_pb2.ListEvaluationRunsResponse:
        response = self.call_list_evaluation_runs(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_get_evaluation_metadata(
        self, req: proto.agentlab.evaluations.v1.evaluation_pb2.GetEvaluationMetadataRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[proto.agentlab.evaluations.v1.evaluation_pb2.GetEvaluationMetadataResponse]:
        """Low-level method to call GetEvaluationMetadata, granting access to errors and metadata"""
        url = self.base_url + "/agentlab.evaluations.v1.EvaluationService/GetEvaluationMetadata"
        return self._connect_client.call_unary(url, req, proto.agentlab.evaluations.v1.evaluation_pb2.GetEvaluationMetadataResponse,extra_headers, timeout_seconds)


    def get_evaluation_metadata(
        self, req: proto.agentlab.evaluations.v1.evaluation_pb2.GetEvaluationMetadataRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> proto.agentlab.evaluations.v1.evaluation_pb2.GetEvaluationMetadataResponse:
        response = self.call_get_evaluation_metadata(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_list_evaluation_groups(
        self, req: proto.agentlab.evaluations.v1.evaluation_pb2.ListEvaluationGroupsRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[proto.agentlab.evaluations.v1.evaluation_pb2.ListEvaluationGroupsResponse]:
        """Low-level method to call ListEvaluationGroups, granting access to errors and metadata"""
        url = self.base_url + "/agentlab.evaluations.v1.EvaluationService/ListEvaluationGroups"
        return self._connect_client.call_unary(url, req, proto.agentlab.evaluations.v1.evaluation_pb2.ListEvaluationGroupsResponse,extra_headers, timeout_seconds)


    def list_evaluation_groups(
        self, req: proto.agentlab.evaluations.v1.evaluation_pb2.ListEvaluationGroupsRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> proto.agentlab.evaluations.v1.evaluation_pb2.ListEvaluationGroupsResponse:
        response = self.call_list_evaluation_groups(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_get_evaluation_group(
        self, req: proto.agentlab.evaluations.v1.evaluation_pb2.GetEvaluationGroupRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[proto.agentlab.evaluations.v1.evaluation_pb2.EvaluationGroup]:
        """Low-level method to call GetEvaluationGroup, granting access to errors and metadata"""
        url = self.base_url + "/agentlab.evaluations.v1.EvaluationService/GetEvaluationGroup"
        return self._connect_client.call_unary(url, req, proto.agentlab.evaluations.v1.evaluation_pb2.EvaluationGroup,extra_headers, timeout_seconds)


    def get_evaluation_group(
        self, req: proto.agentlab.evaluations.v1.evaluation_pb2.GetEvaluationGroupRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> proto.agentlab.evaluations.v1.evaluation_pb2.EvaluationGroup:
        response = self.call_get_evaluation_group(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_get_group_field_statistics(
        self, req: proto.agentlab.evaluations.v1.evaluation_pb2.GetGroupFieldStatisticsRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[proto.agentlab.evaluations.v1.evaluation_pb2.GetGroupFieldStatisticsResponse]:
        """Low-level method to call GetGroupFieldStatistics, granting access to errors and metadata"""
        url = self.base_url + "/agentlab.evaluations.v1.EvaluationService/GetGroupFieldStatistics"
        return self._connect_client.call_unary(url, req, proto.agentlab.evaluations.v1.evaluation_pb2.GetGroupFieldStatisticsResponse,extra_headers, timeout_seconds)


    def get_group_field_statistics(
        self, req: proto.agentlab.evaluations.v1.evaluation_pb2.GetGroupFieldStatisticsRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> proto.agentlab.evaluations.v1.evaluation_pb2.GetGroupFieldStatisticsResponse:
        response = self.call_get_group_field_statistics(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_get_weekly_evaluation_stats(
        self, req: proto.agentlab.evaluations.v1.evaluation_pb2.GetWeeklyEvaluationStatsRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[proto.agentlab.evaluations.v1.evaluation_pb2.GetWeeklyEvaluationStatsResponse]:
        """Low-level method to call GetWeeklyEvaluationStats, granting access to errors and metadata"""
        url = self.base_url + "/agentlab.evaluations.v1.EvaluationService/GetWeeklyEvaluationStats"
        return self._connect_client.call_unary(url, req, proto.agentlab.evaluations.v1.evaluation_pb2.GetWeeklyEvaluationStatsResponse,extra_headers, timeout_seconds)


    def get_weekly_evaluation_stats(
        self, req: proto.agentlab.evaluations.v1.evaluation_pb2.GetWeeklyEvaluationStatsRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> proto.agentlab.evaluations.v1.evaluation_pb2.GetWeeklyEvaluationStatsResponse:
        response = self.call_get_weekly_evaluation_stats(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_get_evaluation_analytics(
        self, req: proto.agentlab.evaluations.v1.evaluation_pb2.GetEvaluationAnalyticsRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[proto.agentlab.evaluations.v1.evaluation_pb2.GetEvaluationAnalyticsResponse]:
        """Low-level method to call GetEvaluationAnalytics, granting access to errors and metadata"""
        url = self.base_url + "/agentlab.evaluations.v1.EvaluationService/GetEvaluationAnalytics"
        return self._connect_client.call_unary(url, req, proto.agentlab.evaluations.v1.evaluation_pb2.GetEvaluationAnalyticsResponse,extra_headers, timeout_seconds)


    def get_evaluation_analytics(
        self, req: proto.agentlab.evaluations.v1.evaluation_pb2.GetEvaluationAnalyticsRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> proto.agentlab.evaluations.v1.evaluation_pb2.GetEvaluationAnalyticsResponse:
        response = self.call_get_evaluation_analytics(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg


class AsyncEvaluationServiceClient:
    def __init__(
        self,
        base_url: str,
        http_client: aiohttp.ClientSession,
        protocol: ConnectProtocol = ConnectProtocol.CONNECT_PROTOBUF,
    ):
        self.base_url = base_url
        self._connect_client = AsyncConnectClient(http_client, protocol)

    async def call_list_evaluators(
        self, req: proto.agentlab.evaluations.v1.evaluation_pb2.ListEvaluatorsRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[proto.agentlab.evaluations.v1.evaluation_pb2.ListEvaluatorsResponse]:
        """Low-level method to call ListEvaluators, granting access to errors and metadata"""
        url = self.base_url + "/agentlab.evaluations.v1.EvaluationService/ListEvaluators"
        return await self._connect_client.call_unary(url, req, proto.agentlab.evaluations.v1.evaluation_pb2.ListEvaluatorsResponse,extra_headers, timeout_seconds)

    async def list_evaluators(
        self, req: proto.agentlab.evaluations.v1.evaluation_pb2.ListEvaluatorsRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> proto.agentlab.evaluations.v1.evaluation_pb2.ListEvaluatorsResponse:
        response = await self.call_list_evaluators(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_get_evaluator(
        self, req: proto.agentlab.evaluations.v1.evaluation_pb2.GetEvaluatorRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[proto.agentlab.evaluations.v1.evaluation_pb2.Evaluator]:
        """Low-level method to call GetEvaluator, granting access to errors and metadata"""
        url = self.base_url + "/agentlab.evaluations.v1.EvaluationService/GetEvaluator"
        return await self._connect_client.call_unary(url, req, proto.agentlab.evaluations.v1.evaluation_pb2.Evaluator,extra_headers, timeout_seconds)

    async def get_evaluator(
        self, req: proto.agentlab.evaluations.v1.evaluation_pb2.GetEvaluatorRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> proto.agentlab.evaluations.v1.evaluation_pb2.Evaluator:
        response = await self.call_get_evaluator(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_run_evaluation(
        self, req: proto.agentlab.evaluations.v1.evaluation_pb2.RunEvaluationRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[proto.agentlab.evaluations.v1.evaluation_pb2.EvaluationRun]:
        """Low-level method to call RunEvaluation, granting access to errors and metadata"""
        url = self.base_url + "/agentlab.evaluations.v1.EvaluationService/RunEvaluation"
        return await self._connect_client.call_unary(url, req, proto.agentlab.evaluations.v1.evaluation_pb2.EvaluationRun,extra_headers, timeout_seconds)

    async def run_evaluation(
        self, req: proto.agentlab.evaluations.v1.evaluation_pb2.RunEvaluationRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> proto.agentlab.evaluations.v1.evaluation_pb2.EvaluationRun:
        response = await self.call_run_evaluation(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_get_evaluation_run(
        self, req: proto.agentlab.evaluations.v1.evaluation_pb2.GetEvaluationRunRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[proto.agentlab.evaluations.v1.evaluation_pb2.EvaluationRun]:
        """Low-level method to call GetEvaluationRun, granting access to errors and metadata"""
        url = self.base_url + "/agentlab.evaluations.v1.EvaluationService/GetEvaluationRun"
        return await self._connect_client.call_unary(url, req, proto.agentlab.evaluations.v1.evaluation_pb2.EvaluationRun,extra_headers, timeout_seconds)

    async def get_evaluation_run(
        self, req: proto.agentlab.evaluations.v1.evaluation_pb2.GetEvaluationRunRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> proto.agentlab.evaluations.v1.evaluation_pb2.EvaluationRun:
        response = await self.call_get_evaluation_run(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_list_evaluation_runs(
        self, req: proto.agentlab.evaluations.v1.evaluation_pb2.ListEvaluationRunsRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[proto.agentlab.evaluations.v1.evaluation_pb2.ListEvaluationRunsResponse]:
        """Low-level method to call ListEvaluationRuns, granting access to errors and metadata"""
        url = self.base_url + "/agentlab.evaluations.v1.EvaluationService/ListEvaluationRuns"
        return await self._connect_client.call_unary(url, req, proto.agentlab.evaluations.v1.evaluation_pb2.ListEvaluationRunsResponse,extra_headers, timeout_seconds)

    async def list_evaluation_runs(
        self, req: proto.agentlab.evaluations.v1.evaluation_pb2.ListEvaluationRunsRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> proto.agentlab.evaluations.v1.evaluation_pb2.ListEvaluationRunsResponse:
        response = await self.call_list_evaluation_runs(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_get_evaluation_metadata(
        self, req: proto.agentlab.evaluations.v1.evaluation_pb2.GetEvaluationMetadataRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[proto.agentlab.evaluations.v1.evaluation_pb2.GetEvaluationMetadataResponse]:
        """Low-level method to call GetEvaluationMetadata, granting access to errors and metadata"""
        url = self.base_url + "/agentlab.evaluations.v1.EvaluationService/GetEvaluationMetadata"
        return await self._connect_client.call_unary(url, req, proto.agentlab.evaluations.v1.evaluation_pb2.GetEvaluationMetadataResponse,extra_headers, timeout_seconds)

    async def get_evaluation_metadata(
        self, req: proto.agentlab.evaluations.v1.evaluation_pb2.GetEvaluationMetadataRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> proto.agentlab.evaluations.v1.evaluation_pb2.GetEvaluationMetadataResponse:
        response = await self.call_get_evaluation_metadata(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_list_evaluation_groups(
        self, req: proto.agentlab.evaluations.v1.evaluation_pb2.ListEvaluationGroupsRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[proto.agentlab.evaluations.v1.evaluation_pb2.ListEvaluationGroupsResponse]:
        """Low-level method to call ListEvaluationGroups, granting access to errors and metadata"""
        url = self.base_url + "/agentlab.evaluations.v1.EvaluationService/ListEvaluationGroups"
        return await self._connect_client.call_unary(url, req, proto.agentlab.evaluations.v1.evaluation_pb2.ListEvaluationGroupsResponse,extra_headers, timeout_seconds)

    async def list_evaluation_groups(
        self, req: proto.agentlab.evaluations.v1.evaluation_pb2.ListEvaluationGroupsRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> proto.agentlab.evaluations.v1.evaluation_pb2.ListEvaluationGroupsResponse:
        response = await self.call_list_evaluation_groups(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_get_evaluation_group(
        self, req: proto.agentlab.evaluations.v1.evaluation_pb2.GetEvaluationGroupRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[proto.agentlab.evaluations.v1.evaluation_pb2.EvaluationGroup]:
        """Low-level method to call GetEvaluationGroup, granting access to errors and metadata"""
        url = self.base_url + "/agentlab.evaluations.v1.EvaluationService/GetEvaluationGroup"
        return await self._connect_client.call_unary(url, req, proto.agentlab.evaluations.v1.evaluation_pb2.EvaluationGroup,extra_headers, timeout_seconds)

    async def get_evaluation_group(
        self, req: proto.agentlab.evaluations.v1.evaluation_pb2.GetEvaluationGroupRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> proto.agentlab.evaluations.v1.evaluation_pb2.EvaluationGroup:
        response = await self.call_get_evaluation_group(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_get_group_field_statistics(
        self, req: proto.agentlab.evaluations.v1.evaluation_pb2.GetGroupFieldStatisticsRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[proto.agentlab.evaluations.v1.evaluation_pb2.GetGroupFieldStatisticsResponse]:
        """Low-level method to call GetGroupFieldStatistics, granting access to errors and metadata"""
        url = self.base_url + "/agentlab.evaluations.v1.EvaluationService/GetGroupFieldStatistics"
        return await self._connect_client.call_unary(url, req, proto.agentlab.evaluations.v1.evaluation_pb2.GetGroupFieldStatisticsResponse,extra_headers, timeout_seconds)

    async def get_group_field_statistics(
        self, req: proto.agentlab.evaluations.v1.evaluation_pb2.GetGroupFieldStatisticsRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> proto.agentlab.evaluations.v1.evaluation_pb2.GetGroupFieldStatisticsResponse:
        response = await self.call_get_group_field_statistics(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_get_weekly_evaluation_stats(
        self, req: proto.agentlab.evaluations.v1.evaluation_pb2.GetWeeklyEvaluationStatsRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[proto.agentlab.evaluations.v1.evaluation_pb2.GetWeeklyEvaluationStatsResponse]:
        """Low-level method to call GetWeeklyEvaluationStats, granting access to errors and metadata"""
        url = self.base_url + "/agentlab.evaluations.v1.EvaluationService/GetWeeklyEvaluationStats"
        return await self._connect_client.call_unary(url, req, proto.agentlab.evaluations.v1.evaluation_pb2.GetWeeklyEvaluationStatsResponse,extra_headers, timeout_seconds)

    async def get_weekly_evaluation_stats(
        self, req: proto.agentlab.evaluations.v1.evaluation_pb2.GetWeeklyEvaluationStatsRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> proto.agentlab.evaluations.v1.evaluation_pb2.GetWeeklyEvaluationStatsResponse:
        response = await self.call_get_weekly_evaluation_stats(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_get_evaluation_analytics(
        self, req: proto.agentlab.evaluations.v1.evaluation_pb2.GetEvaluationAnalyticsRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[proto.agentlab.evaluations.v1.evaluation_pb2.GetEvaluationAnalyticsResponse]:
        """Low-level method to call GetEvaluationAnalytics, granting access to errors and metadata"""
        url = self.base_url + "/agentlab.evaluations.v1.EvaluationService/GetEvaluationAnalytics"
        return await self._connect_client.call_unary(url, req, proto.agentlab.evaluations.v1.evaluation_pb2.GetEvaluationAnalyticsResponse,extra_headers, timeout_seconds)

    async def get_evaluation_analytics(
        self, req: proto.agentlab.evaluations.v1.evaluation_pb2.GetEvaluationAnalyticsRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> proto.agentlab.evaluations.v1.evaluation_pb2.GetEvaluationAnalyticsResponse:
        response = await self.call_get_evaluation_analytics(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg


@typing.runtime_checkable
class EvaluationServiceProtocol(typing.Protocol):
    def list_evaluators(self, req: ClientRequest[proto.agentlab.evaluations.v1.evaluation_pb2.ListEvaluatorsRequest]) -> ServerResponse[proto.agentlab.evaluations.v1.evaluation_pb2.ListEvaluatorsResponse]:
        ...
    def get_evaluator(self, req: ClientRequest[proto.agentlab.evaluations.v1.evaluation_pb2.GetEvaluatorRequest]) -> ServerResponse[proto.agentlab.evaluations.v1.evaluation_pb2.Evaluator]:
        ...
    def run_evaluation(self, req: ClientRequest[proto.agentlab.evaluations.v1.evaluation_pb2.RunEvaluationRequest]) -> ServerResponse[proto.agentlab.evaluations.v1.evaluation_pb2.EvaluationRun]:
        ...
    def get_evaluation_run(self, req: ClientRequest[proto.agentlab.evaluations.v1.evaluation_pb2.GetEvaluationRunRequest]) -> ServerResponse[proto.agentlab.evaluations.v1.evaluation_pb2.EvaluationRun]:
        ...
    def list_evaluation_runs(self, req: ClientRequest[proto.agentlab.evaluations.v1.evaluation_pb2.ListEvaluationRunsRequest]) -> ServerResponse[proto.agentlab.evaluations.v1.evaluation_pb2.ListEvaluationRunsResponse]:
        ...
    def get_evaluation_metadata(self, req: ClientRequest[proto.agentlab.evaluations.v1.evaluation_pb2.GetEvaluationMetadataRequest]) -> ServerResponse[proto.agentlab.evaluations.v1.evaluation_pb2.GetEvaluationMetadataResponse]:
        ...
    def list_evaluation_groups(self, req: ClientRequest[proto.agentlab.evaluations.v1.evaluation_pb2.ListEvaluationGroupsRequest]) -> ServerResponse[proto.agentlab.evaluations.v1.evaluation_pb2.ListEvaluationGroupsResponse]:
        ...
    def get_evaluation_group(self, req: ClientRequest[proto.agentlab.evaluations.v1.evaluation_pb2.GetEvaluationGroupRequest]) -> ServerResponse[proto.agentlab.evaluations.v1.evaluation_pb2.EvaluationGroup]:
        ...
    def get_group_field_statistics(self, req: ClientRequest[proto.agentlab.evaluations.v1.evaluation_pb2.GetGroupFieldStatisticsRequest]) -> ServerResponse[proto.agentlab.evaluations.v1.evaluation_pb2.GetGroupFieldStatisticsResponse]:
        ...
    def get_weekly_evaluation_stats(self, req: ClientRequest[proto.agentlab.evaluations.v1.evaluation_pb2.GetWeeklyEvaluationStatsRequest]) -> ServerResponse[proto.agentlab.evaluations.v1.evaluation_pb2.GetWeeklyEvaluationStatsResponse]:
        ...
    def get_evaluation_analytics(self, req: ClientRequest[proto.agentlab.evaluations.v1.evaluation_pb2.GetEvaluationAnalyticsRequest]) -> ServerResponse[proto.agentlab.evaluations.v1.evaluation_pb2.GetEvaluationAnalyticsResponse]:
        ...

EVALUATION_SERVICE_PATH_PREFIX = "/agentlab.evaluations.v1.EvaluationService"

def wsgi_evaluation_service(implementation: EvaluationServiceProtocol) -> WSGIApplication:
    app = ConnectWSGI()
    app.register_unary_rpc("/agentlab.evaluations.v1.EvaluationService/ListEvaluators", implementation.list_evaluators, proto.agentlab.evaluations.v1.evaluation_pb2.ListEvaluatorsRequest)
    app.register_unary_rpc("/agentlab.evaluations.v1.EvaluationService/GetEvaluator", implementation.get_evaluator, proto.agentlab.evaluations.v1.evaluation_pb2.GetEvaluatorRequest)
    app.register_unary_rpc("/agentlab.evaluations.v1.EvaluationService/RunEvaluation", implementation.run_evaluation, proto.agentlab.evaluations.v1.evaluation_pb2.RunEvaluationRequest)
    app.register_unary_rpc("/agentlab.evaluations.v1.EvaluationService/GetEvaluationRun", implementation.get_evaluation_run, proto.agentlab.evaluations.v1.evaluation_pb2.GetEvaluationRunRequest)
    app.register_unary_rpc("/agentlab.evaluations.v1.EvaluationService/ListEvaluationRuns", implementation.list_evaluation_runs, proto.agentlab.evaluations.v1.evaluation_pb2.ListEvaluationRunsRequest)
    app.register_unary_rpc("/agentlab.evaluations.v1.EvaluationService/GetEvaluationMetadata", implementation.get_evaluation_metadata, proto.agentlab.evaluations.v1.evaluation_pb2.GetEvaluationMetadataRequest)
    app.register_unary_rpc("/agentlab.evaluations.v1.EvaluationService/ListEvaluationGroups", implementation.list_evaluation_groups, proto.agentlab.evaluations.v1.evaluation_pb2.ListEvaluationGroupsRequest)
    app.register_unary_rpc("/agentlab.evaluations.v1.EvaluationService/GetEvaluationGroup", implementation.get_evaluation_group, proto.agentlab.evaluations.v1.evaluation_pb2.GetEvaluationGroupRequest)
    app.register_unary_rpc("/agentlab.evaluations.v1.EvaluationService/GetGroupFieldStatistics", implementation.get_group_field_statistics, proto.agentlab.evaluations.v1.evaluation_pb2.GetGroupFieldStatisticsRequest)
    app.register_unary_rpc("/agentlab.evaluations.v1.EvaluationService/GetWeeklyEvaluationStats", implementation.get_weekly_evaluation_stats, proto.agentlab.evaluations.v1.evaluation_pb2.GetWeeklyEvaluationStatsRequest)
    app.register_unary_rpc("/agentlab.evaluations.v1.EvaluationService/GetEvaluationAnalytics", implementation.get_evaluation_analytics, proto.agentlab.evaluations.v1.evaluation_pb2.GetEvaluationAnalyticsRequest)
    return app

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
import proto.agentlab.iam.v1.iam_service_pb2
import proto.agentlab.iam.v1.membership_pb2

class IAMServiceClient:
    def __init__(
        self,
        base_url: str,
        http_client: urllib3.PoolManager | None = None,
        protocol: ConnectProtocol = ConnectProtocol.CONNECT_PROTOBUF,
    ):
        self.base_url = base_url
        self._connect_client = ConnectClient(http_client, protocol)
    def call_validate_token(
        self, req: proto.agentlab.iam.v1.iam_service_pb2.ValidateTokenRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[proto.agentlab.iam.v1.iam_service_pb2.ValidateTokenResponse]:
        """Low-level method to call ValidateToken, granting access to errors and metadata"""
        url = self.base_url + "/agentlab.iam.v1.IAMService/ValidateToken"
        return self._connect_client.call_unary(url, req, proto.agentlab.iam.v1.iam_service_pb2.ValidateTokenResponse,extra_headers, timeout_seconds)


    def validate_token(
        self, req: proto.agentlab.iam.v1.iam_service_pb2.ValidateTokenRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> proto.agentlab.iam.v1.iam_service_pb2.ValidateTokenResponse:
        response = self.call_validate_token(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_get_auth_context(
        self, req: proto.agentlab.iam.v1.iam_service_pb2.GetAuthContextRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[proto.agentlab.iam.v1.iam_service_pb2.GetAuthContextResponse]:
        """Low-level method to call GetAuthContext, granting access to errors and metadata"""
        url = self.base_url + "/agentlab.iam.v1.IAMService/GetAuthContext"
        return self._connect_client.call_unary(url, req, proto.agentlab.iam.v1.iam_service_pb2.GetAuthContextResponse,extra_headers, timeout_seconds)


    def get_auth_context(
        self, req: proto.agentlab.iam.v1.iam_service_pb2.GetAuthContextRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> proto.agentlab.iam.v1.iam_service_pb2.GetAuthContextResponse:
        response = self.call_get_auth_context(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_invite_user(
        self, req: proto.agentlab.iam.v1.iam_service_pb2.InviteUserRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[proto.agentlab.iam.v1.membership_pb2.Invitation]:
        """Low-level method to call InviteUser, granting access to errors and metadata"""
        url = self.base_url + "/agentlab.iam.v1.IAMService/InviteUser"
        return self._connect_client.call_unary(url, req, proto.agentlab.iam.v1.membership_pb2.Invitation,extra_headers, timeout_seconds)


    def invite_user(
        self, req: proto.agentlab.iam.v1.iam_service_pb2.InviteUserRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> proto.agentlab.iam.v1.membership_pb2.Invitation:
        response = self.call_invite_user(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_accept_invitation(
        self, req: proto.agentlab.iam.v1.iam_service_pb2.AcceptInvitationRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[proto.agentlab.iam.v1.membership_pb2.Membership]:
        """Low-level method to call AcceptInvitation, granting access to errors and metadata"""
        url = self.base_url + "/agentlab.iam.v1.IAMService/AcceptInvitation"
        return self._connect_client.call_unary(url, req, proto.agentlab.iam.v1.membership_pb2.Membership,extra_headers, timeout_seconds)


    def accept_invitation(
        self, req: proto.agentlab.iam.v1.iam_service_pb2.AcceptInvitationRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> proto.agentlab.iam.v1.membership_pb2.Membership:
        response = self.call_accept_invitation(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_list_members(
        self, req: proto.agentlab.iam.v1.iam_service_pb2.ListMembersRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[proto.agentlab.iam.v1.iam_service_pb2.ListMembersResponse]:
        """Low-level method to call ListMembers, granting access to errors and metadata"""
        url = self.base_url + "/agentlab.iam.v1.IAMService/ListMembers"
        return self._connect_client.call_unary(url, req, proto.agentlab.iam.v1.iam_service_pb2.ListMembersResponse,extra_headers, timeout_seconds)


    def list_members(
        self, req: proto.agentlab.iam.v1.iam_service_pb2.ListMembersRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> proto.agentlab.iam.v1.iam_service_pb2.ListMembersResponse:
        response = self.call_list_members(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_update_membership(
        self, req: proto.agentlab.iam.v1.iam_service_pb2.UpdateMembershipRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[proto.agentlab.iam.v1.membership_pb2.Membership]:
        """Low-level method to call UpdateMembership, granting access to errors and metadata"""
        url = self.base_url + "/agentlab.iam.v1.IAMService/UpdateMembership"
        return self._connect_client.call_unary(url, req, proto.agentlab.iam.v1.membership_pb2.Membership,extra_headers, timeout_seconds)


    def update_membership(
        self, req: proto.agentlab.iam.v1.iam_service_pb2.UpdateMembershipRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> proto.agentlab.iam.v1.membership_pb2.Membership:
        response = self.call_update_membership(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_remove_member(
        self, req: proto.agentlab.iam.v1.iam_service_pb2.RemoveMemberRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[google.protobuf.empty_pb2.Empty]:
        """Low-level method to call RemoveMember, granting access to errors and metadata"""
        url = self.base_url + "/agentlab.iam.v1.IAMService/RemoveMember"
        return self._connect_client.call_unary(url, req, google.protobuf.empty_pb2.Empty,extra_headers, timeout_seconds)


    def remove_member(
        self, req: proto.agentlab.iam.v1.iam_service_pb2.RemoveMemberRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> google.protobuf.empty_pb2.Empty:
        response = self.call_remove_member(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_list_invitations(
        self, req: proto.agentlab.iam.v1.iam_service_pb2.ListInvitationsRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[proto.agentlab.iam.v1.iam_service_pb2.ListInvitationsResponse]:
        """Low-level method to call ListInvitations, granting access to errors and metadata"""
        url = self.base_url + "/agentlab.iam.v1.IAMService/ListInvitations"
        return self._connect_client.call_unary(url, req, proto.agentlab.iam.v1.iam_service_pb2.ListInvitationsResponse,extra_headers, timeout_seconds)


    def list_invitations(
        self, req: proto.agentlab.iam.v1.iam_service_pb2.ListInvitationsRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> proto.agentlab.iam.v1.iam_service_pb2.ListInvitationsResponse:
        response = self.call_list_invitations(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_cancel_invitation(
        self, req: proto.agentlab.iam.v1.iam_service_pb2.CancelInvitationRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[google.protobuf.empty_pb2.Empty]:
        """Low-level method to call CancelInvitation, granting access to errors and metadata"""
        url = self.base_url + "/agentlab.iam.v1.IAMService/CancelInvitation"
        return self._connect_client.call_unary(url, req, google.protobuf.empty_pb2.Empty,extra_headers, timeout_seconds)


    def cancel_invitation(
        self, req: proto.agentlab.iam.v1.iam_service_pb2.CancelInvitationRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> google.protobuf.empty_pb2.Empty:
        response = self.call_cancel_invitation(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_create_api_token(
        self, req: proto.agentlab.iam.v1.iam_service_pb2.CreateAPITokenRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[proto.agentlab.iam.v1.iam_service_pb2.CreateAPITokenResponse]:
        """Low-level method to call CreateAPIToken, granting access to errors and metadata"""
        url = self.base_url + "/agentlab.iam.v1.IAMService/CreateAPIToken"
        return self._connect_client.call_unary(url, req, proto.agentlab.iam.v1.iam_service_pb2.CreateAPITokenResponse,extra_headers, timeout_seconds)


    def create_api_token(
        self, req: proto.agentlab.iam.v1.iam_service_pb2.CreateAPITokenRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> proto.agentlab.iam.v1.iam_service_pb2.CreateAPITokenResponse:
        response = self.call_create_api_token(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_list_api_tokens(
        self, req: proto.agentlab.iam.v1.iam_service_pb2.ListAPITokensRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[proto.agentlab.iam.v1.iam_service_pb2.ListAPITokensResponse]:
        """Low-level method to call ListAPITokens, granting access to errors and metadata"""
        url = self.base_url + "/agentlab.iam.v1.IAMService/ListAPITokens"
        return self._connect_client.call_unary(url, req, proto.agentlab.iam.v1.iam_service_pb2.ListAPITokensResponse,extra_headers, timeout_seconds)


    def list_api_tokens(
        self, req: proto.agentlab.iam.v1.iam_service_pb2.ListAPITokensRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> proto.agentlab.iam.v1.iam_service_pb2.ListAPITokensResponse:
        response = self.call_list_api_tokens(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_revoke_api_token(
        self, req: proto.agentlab.iam.v1.iam_service_pb2.RevokeAPITokenRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[google.protobuf.empty_pb2.Empty]:
        """Low-level method to call RevokeAPIToken, granting access to errors and metadata"""
        url = self.base_url + "/agentlab.iam.v1.IAMService/RevokeAPIToken"
        return self._connect_client.call_unary(url, req, google.protobuf.empty_pb2.Empty,extra_headers, timeout_seconds)


    def revoke_api_token(
        self, req: proto.agentlab.iam.v1.iam_service_pb2.RevokeAPITokenRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> google.protobuf.empty_pb2.Empty:
        response = self.call_revoke_api_token(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg


class AsyncIAMServiceClient:
    def __init__(
        self,
        base_url: str,
        http_client: aiohttp.ClientSession,
        protocol: ConnectProtocol = ConnectProtocol.CONNECT_PROTOBUF,
    ):
        self.base_url = base_url
        self._connect_client = AsyncConnectClient(http_client, protocol)

    async def call_validate_token(
        self, req: proto.agentlab.iam.v1.iam_service_pb2.ValidateTokenRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[proto.agentlab.iam.v1.iam_service_pb2.ValidateTokenResponse]:
        """Low-level method to call ValidateToken, granting access to errors and metadata"""
        url = self.base_url + "/agentlab.iam.v1.IAMService/ValidateToken"
        return await self._connect_client.call_unary(url, req, proto.agentlab.iam.v1.iam_service_pb2.ValidateTokenResponse,extra_headers, timeout_seconds)

    async def validate_token(
        self, req: proto.agentlab.iam.v1.iam_service_pb2.ValidateTokenRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> proto.agentlab.iam.v1.iam_service_pb2.ValidateTokenResponse:
        response = await self.call_validate_token(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_get_auth_context(
        self, req: proto.agentlab.iam.v1.iam_service_pb2.GetAuthContextRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[proto.agentlab.iam.v1.iam_service_pb2.GetAuthContextResponse]:
        """Low-level method to call GetAuthContext, granting access to errors and metadata"""
        url = self.base_url + "/agentlab.iam.v1.IAMService/GetAuthContext"
        return await self._connect_client.call_unary(url, req, proto.agentlab.iam.v1.iam_service_pb2.GetAuthContextResponse,extra_headers, timeout_seconds)

    async def get_auth_context(
        self, req: proto.agentlab.iam.v1.iam_service_pb2.GetAuthContextRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> proto.agentlab.iam.v1.iam_service_pb2.GetAuthContextResponse:
        response = await self.call_get_auth_context(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_invite_user(
        self, req: proto.agentlab.iam.v1.iam_service_pb2.InviteUserRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[proto.agentlab.iam.v1.membership_pb2.Invitation]:
        """Low-level method to call InviteUser, granting access to errors and metadata"""
        url = self.base_url + "/agentlab.iam.v1.IAMService/InviteUser"
        return await self._connect_client.call_unary(url, req, proto.agentlab.iam.v1.membership_pb2.Invitation,extra_headers, timeout_seconds)

    async def invite_user(
        self, req: proto.agentlab.iam.v1.iam_service_pb2.InviteUserRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> proto.agentlab.iam.v1.membership_pb2.Invitation:
        response = await self.call_invite_user(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_accept_invitation(
        self, req: proto.agentlab.iam.v1.iam_service_pb2.AcceptInvitationRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[proto.agentlab.iam.v1.membership_pb2.Membership]:
        """Low-level method to call AcceptInvitation, granting access to errors and metadata"""
        url = self.base_url + "/agentlab.iam.v1.IAMService/AcceptInvitation"
        return await self._connect_client.call_unary(url, req, proto.agentlab.iam.v1.membership_pb2.Membership,extra_headers, timeout_seconds)

    async def accept_invitation(
        self, req: proto.agentlab.iam.v1.iam_service_pb2.AcceptInvitationRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> proto.agentlab.iam.v1.membership_pb2.Membership:
        response = await self.call_accept_invitation(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_list_members(
        self, req: proto.agentlab.iam.v1.iam_service_pb2.ListMembersRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[proto.agentlab.iam.v1.iam_service_pb2.ListMembersResponse]:
        """Low-level method to call ListMembers, granting access to errors and metadata"""
        url = self.base_url + "/agentlab.iam.v1.IAMService/ListMembers"
        return await self._connect_client.call_unary(url, req, proto.agentlab.iam.v1.iam_service_pb2.ListMembersResponse,extra_headers, timeout_seconds)

    async def list_members(
        self, req: proto.agentlab.iam.v1.iam_service_pb2.ListMembersRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> proto.agentlab.iam.v1.iam_service_pb2.ListMembersResponse:
        response = await self.call_list_members(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_update_membership(
        self, req: proto.agentlab.iam.v1.iam_service_pb2.UpdateMembershipRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[proto.agentlab.iam.v1.membership_pb2.Membership]:
        """Low-level method to call UpdateMembership, granting access to errors and metadata"""
        url = self.base_url + "/agentlab.iam.v1.IAMService/UpdateMembership"
        return await self._connect_client.call_unary(url, req, proto.agentlab.iam.v1.membership_pb2.Membership,extra_headers, timeout_seconds)

    async def update_membership(
        self, req: proto.agentlab.iam.v1.iam_service_pb2.UpdateMembershipRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> proto.agentlab.iam.v1.membership_pb2.Membership:
        response = await self.call_update_membership(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_remove_member(
        self, req: proto.agentlab.iam.v1.iam_service_pb2.RemoveMemberRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[google.protobuf.empty_pb2.Empty]:
        """Low-level method to call RemoveMember, granting access to errors and metadata"""
        url = self.base_url + "/agentlab.iam.v1.IAMService/RemoveMember"
        return await self._connect_client.call_unary(url, req, google.protobuf.empty_pb2.Empty,extra_headers, timeout_seconds)

    async def remove_member(
        self, req: proto.agentlab.iam.v1.iam_service_pb2.RemoveMemberRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> google.protobuf.empty_pb2.Empty:
        response = await self.call_remove_member(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_list_invitations(
        self, req: proto.agentlab.iam.v1.iam_service_pb2.ListInvitationsRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[proto.agentlab.iam.v1.iam_service_pb2.ListInvitationsResponse]:
        """Low-level method to call ListInvitations, granting access to errors and metadata"""
        url = self.base_url + "/agentlab.iam.v1.IAMService/ListInvitations"
        return await self._connect_client.call_unary(url, req, proto.agentlab.iam.v1.iam_service_pb2.ListInvitationsResponse,extra_headers, timeout_seconds)

    async def list_invitations(
        self, req: proto.agentlab.iam.v1.iam_service_pb2.ListInvitationsRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> proto.agentlab.iam.v1.iam_service_pb2.ListInvitationsResponse:
        response = await self.call_list_invitations(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_cancel_invitation(
        self, req: proto.agentlab.iam.v1.iam_service_pb2.CancelInvitationRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[google.protobuf.empty_pb2.Empty]:
        """Low-level method to call CancelInvitation, granting access to errors and metadata"""
        url = self.base_url + "/agentlab.iam.v1.IAMService/CancelInvitation"
        return await self._connect_client.call_unary(url, req, google.protobuf.empty_pb2.Empty,extra_headers, timeout_seconds)

    async def cancel_invitation(
        self, req: proto.agentlab.iam.v1.iam_service_pb2.CancelInvitationRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> google.protobuf.empty_pb2.Empty:
        response = await self.call_cancel_invitation(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_create_api_token(
        self, req: proto.agentlab.iam.v1.iam_service_pb2.CreateAPITokenRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[proto.agentlab.iam.v1.iam_service_pb2.CreateAPITokenResponse]:
        """Low-level method to call CreateAPIToken, granting access to errors and metadata"""
        url = self.base_url + "/agentlab.iam.v1.IAMService/CreateAPIToken"
        return await self._connect_client.call_unary(url, req, proto.agentlab.iam.v1.iam_service_pb2.CreateAPITokenResponse,extra_headers, timeout_seconds)

    async def create_api_token(
        self, req: proto.agentlab.iam.v1.iam_service_pb2.CreateAPITokenRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> proto.agentlab.iam.v1.iam_service_pb2.CreateAPITokenResponse:
        response = await self.call_create_api_token(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_list_api_tokens(
        self, req: proto.agentlab.iam.v1.iam_service_pb2.ListAPITokensRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[proto.agentlab.iam.v1.iam_service_pb2.ListAPITokensResponse]:
        """Low-level method to call ListAPITokens, granting access to errors and metadata"""
        url = self.base_url + "/agentlab.iam.v1.IAMService/ListAPITokens"
        return await self._connect_client.call_unary(url, req, proto.agentlab.iam.v1.iam_service_pb2.ListAPITokensResponse,extra_headers, timeout_seconds)

    async def list_api_tokens(
        self, req: proto.agentlab.iam.v1.iam_service_pb2.ListAPITokensRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> proto.agentlab.iam.v1.iam_service_pb2.ListAPITokensResponse:
        response = await self.call_list_api_tokens(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_revoke_api_token(
        self, req: proto.agentlab.iam.v1.iam_service_pb2.RevokeAPITokenRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[google.protobuf.empty_pb2.Empty]:
        """Low-level method to call RevokeAPIToken, granting access to errors and metadata"""
        url = self.base_url + "/agentlab.iam.v1.IAMService/RevokeAPIToken"
        return await self._connect_client.call_unary(url, req, google.protobuf.empty_pb2.Empty,extra_headers, timeout_seconds)

    async def revoke_api_token(
        self, req: proto.agentlab.iam.v1.iam_service_pb2.RevokeAPITokenRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> google.protobuf.empty_pb2.Empty:
        response = await self.call_revoke_api_token(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg


@typing.runtime_checkable
class IAMServiceProtocol(typing.Protocol):
    def validate_token(self, req: ClientRequest[proto.agentlab.iam.v1.iam_service_pb2.ValidateTokenRequest]) -> ServerResponse[proto.agentlab.iam.v1.iam_service_pb2.ValidateTokenResponse]:
        ...
    def get_auth_context(self, req: ClientRequest[proto.agentlab.iam.v1.iam_service_pb2.GetAuthContextRequest]) -> ServerResponse[proto.agentlab.iam.v1.iam_service_pb2.GetAuthContextResponse]:
        ...
    def invite_user(self, req: ClientRequest[proto.agentlab.iam.v1.iam_service_pb2.InviteUserRequest]) -> ServerResponse[proto.agentlab.iam.v1.membership_pb2.Invitation]:
        ...
    def accept_invitation(self, req: ClientRequest[proto.agentlab.iam.v1.iam_service_pb2.AcceptInvitationRequest]) -> ServerResponse[proto.agentlab.iam.v1.membership_pb2.Membership]:
        ...
    def list_members(self, req: ClientRequest[proto.agentlab.iam.v1.iam_service_pb2.ListMembersRequest]) -> ServerResponse[proto.agentlab.iam.v1.iam_service_pb2.ListMembersResponse]:
        ...
    def update_membership(self, req: ClientRequest[proto.agentlab.iam.v1.iam_service_pb2.UpdateMembershipRequest]) -> ServerResponse[proto.agentlab.iam.v1.membership_pb2.Membership]:
        ...
    def remove_member(self, req: ClientRequest[proto.agentlab.iam.v1.iam_service_pb2.RemoveMemberRequest]) -> ServerResponse[google.protobuf.empty_pb2.Empty]:
        ...
    def list_invitations(self, req: ClientRequest[proto.agentlab.iam.v1.iam_service_pb2.ListInvitationsRequest]) -> ServerResponse[proto.agentlab.iam.v1.iam_service_pb2.ListInvitationsResponse]:
        ...
    def cancel_invitation(self, req: ClientRequest[proto.agentlab.iam.v1.iam_service_pb2.CancelInvitationRequest]) -> ServerResponse[google.protobuf.empty_pb2.Empty]:
        ...
    def create_api_token(self, req: ClientRequest[proto.agentlab.iam.v1.iam_service_pb2.CreateAPITokenRequest]) -> ServerResponse[proto.agentlab.iam.v1.iam_service_pb2.CreateAPITokenResponse]:
        ...
    def list_api_tokens(self, req: ClientRequest[proto.agentlab.iam.v1.iam_service_pb2.ListAPITokensRequest]) -> ServerResponse[proto.agentlab.iam.v1.iam_service_pb2.ListAPITokensResponse]:
        ...
    def revoke_api_token(self, req: ClientRequest[proto.agentlab.iam.v1.iam_service_pb2.RevokeAPITokenRequest]) -> ServerResponse[google.protobuf.empty_pb2.Empty]:
        ...

IAM_SERVICE_PATH_PREFIX = "/agentlab.iam.v1.IAMService"

def wsgi_iam_service(implementation: IAMServiceProtocol) -> WSGIApplication:
    app = ConnectWSGI()
    app.register_unary_rpc("/agentlab.iam.v1.IAMService/ValidateToken", implementation.validate_token, proto.agentlab.iam.v1.iam_service_pb2.ValidateTokenRequest)
    app.register_unary_rpc("/agentlab.iam.v1.IAMService/GetAuthContext", implementation.get_auth_context, proto.agentlab.iam.v1.iam_service_pb2.GetAuthContextRequest)
    app.register_unary_rpc("/agentlab.iam.v1.IAMService/InviteUser", implementation.invite_user, proto.agentlab.iam.v1.iam_service_pb2.InviteUserRequest)
    app.register_unary_rpc("/agentlab.iam.v1.IAMService/AcceptInvitation", implementation.accept_invitation, proto.agentlab.iam.v1.iam_service_pb2.AcceptInvitationRequest)
    app.register_unary_rpc("/agentlab.iam.v1.IAMService/ListMembers", implementation.list_members, proto.agentlab.iam.v1.iam_service_pb2.ListMembersRequest)
    app.register_unary_rpc("/agentlab.iam.v1.IAMService/UpdateMembership", implementation.update_membership, proto.agentlab.iam.v1.iam_service_pb2.UpdateMembershipRequest)
    app.register_unary_rpc("/agentlab.iam.v1.IAMService/RemoveMember", implementation.remove_member, proto.agentlab.iam.v1.iam_service_pb2.RemoveMemberRequest)
    app.register_unary_rpc("/agentlab.iam.v1.IAMService/ListInvitations", implementation.list_invitations, proto.agentlab.iam.v1.iam_service_pb2.ListInvitationsRequest)
    app.register_unary_rpc("/agentlab.iam.v1.IAMService/CancelInvitation", implementation.cancel_invitation, proto.agentlab.iam.v1.iam_service_pb2.CancelInvitationRequest)
    app.register_unary_rpc("/agentlab.iam.v1.IAMService/CreateAPIToken", implementation.create_api_token, proto.agentlab.iam.v1.iam_service_pb2.CreateAPITokenRequest)
    app.register_unary_rpc("/agentlab.iam.v1.IAMService/ListAPITokens", implementation.list_api_tokens, proto.agentlab.iam.v1.iam_service_pb2.ListAPITokensRequest)
    app.register_unary_rpc("/agentlab.iam.v1.IAMService/RevokeAPIToken", implementation.revoke_api_token, proto.agentlab.iam.v1.iam_service_pb2.RevokeAPITokenRequest)
    return app

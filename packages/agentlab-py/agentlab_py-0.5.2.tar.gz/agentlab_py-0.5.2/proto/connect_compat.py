"""
Compatibility layer for connect-python 0.5.0.

This module provides compatibility wrappers that allow generated protobuf 
Connect service files (generated for 0.4.x) to work with connect-python 0.5.0.
"""

from typing import Optional, TypeVar, Generic, Any
import urllib3
import httpx
from connectrpc.client import ConnectClient as ConnectClient050, ConnectClientSync as ConnectClientSync050
from connectrpc.errors import ConnectError
from connectrpc.code import Code
from connectrpc.request import Headers
from connectrpc.method import MethodInfo, IdempotencyLevel

# Type variables for generic response types
REQ = TypeVar('REQ')
RES = TypeVar('RES')


class ConnectProtocol:
    """Compatibility enum for protocol selection"""
    CONNECT_PROTOBUF = "proto"
    CONNECT_JSON = "json"
    GRPC = "grpc"
    GRPCWEB = "grpcweb"


class ConnectProtocolError(ConnectError):
    """Compatibility exception that maps to ConnectError"""
    pass


class UnaryOutput(Generic[RES]):
    """Wrapper for unary call responses that matches 0.4.x API"""
    def __init__(self, message: Optional[RES], error: Optional[ConnectError]):
        self._message = message
        self._error = error
    
    def message(self) -> Optional[RES]:
        return self._message
    
    def error(self) -> Optional[ConnectError]:
        return self._error


class ClientStreamingOutput(Generic[RES]):
    """Wrapper for client streaming responses"""
    def __init__(self, message: Optional[RES], error: Optional[ConnectError]):
        self._message = message
        self._error = error
    
    def message(self) -> Optional[RES]:
        return self._message
    
    def error(self) -> Optional[ConnectError]:
        return self._error


# Type aliases for compatibility
HeaderInput = Optional[dict[str, str | list[str]]]
StreamInput = Any
AsyncStreamOutput = Any
StreamOutput = Any


class ConnectClient:
    """
    Compatibility wrapper for synchronous Connect client (0.4.x style).
    Wraps the new 0.5.0 ConnectClientSync.
    """
    def __init__(
        self,
        http_client: Optional[urllib3.PoolManager] = None,
        protocol: str = ConnectProtocol.CONNECT_PROTOBUF,
    ):
        self.protocol = protocol
        self.http_client = http_client
        self._base_url: Optional[str] = None
        self._client: Optional[ConnectClientSync050] = None
    
    def _ensure_client(self, url: str) -> ConnectClientSync050:
        """Lazy initialization of the 0.5.0 client"""
        # Extract base URL from the full URL
        if "://" in url:
            # Full URL like https://api.example.com/service/Method
            parts = url.split("/")
            base_url = f"{parts[0]}//{parts[2]}"
        else:
            # Relative URL - shouldn't happen but handle it
            base_url = url.split("/")[0]
        
        if self._client is None or self._base_url != base_url:
            self._base_url = base_url
            proto_json = (self.protocol == ConnectProtocol.CONNECT_JSON)
            
            # Convert urllib3 client to httpx client if provided
            httpx_client = None
            if self.http_client is not None:
                # Create a basic httpx client - connection pooling is handled internally
                httpx_client = httpx.Client()
            
            self._client = ConnectClientSync050(
                address=base_url,
                proto_json=proto_json,
                session=httpx_client,
            )
        
        return self._client
    
    def call_unary(
        self,
        url: str,
        request: REQ,
        response_type: type[RES],
        extra_headers: HeaderInput = None,
        timeout_seconds: Optional[float] = None,
    ) -> UnaryOutput[RES]:
        """Make a unary (request-response) RPC call"""
        try:
            client = self._ensure_client(url)
            
            # Extract the method path and service name from the URL
            # Format: /service.name.Space/MethodName
            if "://" in url:
                # Full URL like https://api.example.com/service/Method
                method_path = "/" + "/".join(url.split("/")[3:])
            else:
                method_path = url
            
            # Parse service and method from path like "/agentlab.evaluations.v1.EvaluationService/RunEvaluation"
            parts = method_path.strip("/").split("/")
            if len(parts) >= 2:
                service_name = parts[0]
                method_name = parts[1]
            else:
                service_name = "unknown"
                method_name = parts[0] if parts else "unknown"
            
            # Prepare headers
            headers = {}
            if extra_headers:
                if isinstance(extra_headers, dict):
                    headers = extra_headers
            
            # Convert timeout to milliseconds
            timeout_ms = None
            if timeout_seconds is not None:
                timeout_ms = int(timeout_seconds * 1000)
            
            # Create MethodInfo for 0.5.0 API
            method_info = MethodInfo(
                name=method_name,
                service_name=service_name,
                input=type(request),
                output=response_type,
                idempotency_level=IdempotencyLevel.UNKNOWN,
            )
            
            # Make the call using the 0.5.0 API
            response = client.execute_unary(
                request=request,
                method=method_info,
                headers=headers,
                timeout_ms=timeout_ms,
            )
            
            return UnaryOutput(response, None)
            
        except ConnectError as e:
            return UnaryOutput(None, e)
        except Exception as e:
            # Wrap other exceptions as ConnectError
            error = ConnectProtocolError(str(e))
            return UnaryOutput(None, error)


class AsyncConnectClient:
    """
    Compatibility wrapper for async Connect client (0.4.x style).
    Wraps the new 0.5.0 ConnectClient (async).
    """
    def __init__(
        self,
        http_client: Optional[Any] = None,  # aiohttp client in 0.4.x
        protocol: str = ConnectProtocol.CONNECT_PROTOBUF,
    ):
        self.protocol = protocol
        self.http_client = http_client
        self._base_url: Optional[str] = None
        self._client: Optional[ConnectClient050] = None
    
    def _ensure_client(self, url: str) -> ConnectClient050:
        """Lazy initialization of the 0.5.0 async client"""
        if "://" in url:
            parts = url.split("/")
            base_url = f"{parts[0]}//{parts[2]}"
        else:
            base_url = url.split("/")[0]
        
        if self._client is None or self._base_url != base_url:
            self._base_url = base_url
            proto_json = (self.protocol == ConnectProtocol.CONNECT_JSON)
            
            # For async, we'll create an httpx.AsyncClient
            httpx_client = None
            if self.http_client is not None:
                httpx_client = httpx.AsyncClient()
            
            self._client = ConnectClient050(
                address=base_url,
                proto_json=proto_json,
                session=httpx_client,
            )
        
        return self._client
    
    async def call_unary(
        self,
        url: str,
        request: REQ,
        response_type: type[RES],
        extra_headers: HeaderInput = None,
        timeout_seconds: Optional[float] = None,
    ) -> UnaryOutput[RES]:
        """Make an async unary (request-response) RPC call"""
        try:
            client = self._ensure_client(url)
            
            if "://" in url:
                method_path = "/" + "/".join(url.split("/")[3:])
            else:
                method_path = url
            
            # Parse service and method from path
            parts = method_path.strip("/").split("/")
            if len(parts) >= 2:
                service_name = parts[0]
                method_name = parts[1]
            else:
                service_name = "unknown"
                method_name = parts[0] if parts else "unknown"
            
            headers = {}
            if extra_headers:
                if isinstance(extra_headers, dict):
                    headers = extra_headers
            
            timeout_ms = None
            if timeout_seconds is not None:
                timeout_ms = int(timeout_seconds * 1000)
            
            # Create MethodInfo for 0.5.0 API
            method_info = MethodInfo(
                name=method_name,
                service_name=service_name,
                input=type(request),
                output=response_type,
                idempotency_level=IdempotencyLevel.UNKNOWN,
            )
            
            # Make the async call using 0.5.0 API
            response = await client.execute_unary(
                request=request,
                method=method_info,
                headers=headers,
                timeout_ms=timeout_ms,
            )
            
            return UnaryOutput(response, None)
            
        except ConnectError as e:
            return UnaryOutput(None, e)
        except Exception as e:
            error = ConnectProtocolError(str(e))
            return UnaryOutput(None, error)


# Server-side classes (stub implementations for generated code compatibility)
class ClientRequest:
    """Stub for server-side request"""
    pass


class ClientStream:
    """Stub for client streaming"""
    pass


class ServerResponse:
    """Stub for server response"""
    pass


class ServerStream:
    """Stub for server streaming"""
    pass


class ConnectWSGI:
    """Stub for WSGI server"""
    pass


"""AgentLab Python Client for evaluation platform using Connect RPC."""

import urllib3
import os
from typing import Optional, Dict, List, Union, Callable, Awaitable
import json

from .exceptions import AgentLabError, AuthenticationError, APIError
from .converters import (
    convert_evaluation_run, convert_evaluator, convert_list_evaluators_response, 
    convert_list_evaluation_runs_response, convert_agent_version, convert_list_agent_versions_response,
    convert_analysis_session, convert_list_analysis_sessions_response
)
from agentlab.proto.agentlab.evaluations.v1.evaluation_connect import EvaluationServiceClientSync
from agentlab.proto.agentlab.evaluations.v1 import evaluation_pb2
from agentlab.proto.agentlab.iam.v1.iam_service_connect import IAMServiceClientSync
from agentlab.proto.agentlab.iam.v1 import iam_service_pb2
from agentlab.proto.agentlab.agent.v1.agent_service_connect import AgentServiceClientSync
from agentlab.proto.agentlab.agent.v1 import agent_service_pb2
from agentlab.proto.agentlab.analysis.v1.analysis_service_connect import AgentAnalysisServiceClientSync
from agentlab.proto.agentlab.analysis.v1 import analysis_service_pb2

# Type aliases
TokenGetter = Callable[[], Awaitable[Optional[str]]]


class CreateEvaluationOptions:
    """Options for creating an evaluation."""
    
    def __init__(
        self,
        agent_name: str,
        agent_version: str,
        evaluator_names: List[str],
        user_question: str,
        agent_answer: str,
        project_id: Optional[str] = None,
        ground_truth: Optional[str] = None,
        instructions: Optional[str] = None,
        metadata: Optional[Dict[str, Union[str, int, bool, float]]] = None
    ):
        self.agent_name = agent_name
        self.agent_version = agent_version
        self.evaluator_names = evaluator_names
        self.user_question = user_question
        self.agent_answer = agent_answer
        self.project_id = project_id
        self.ground_truth = ground_truth
        self.instructions = instructions
        self.metadata = metadata or {}


class CreateAgentVersionOptions:
    """Options for creating an agent version."""
    
    def __init__(
        self,
        agent_name: str,
        version: str,
        prompts: Dict[str, str],
        project_id: Optional[str] = None,
        metadata: Optional[Dict[str, Union[str, int, bool, float]]] = None,
        description: Optional[str] = None
    ):
        self.agent_name = agent_name
        self.version = version
        self.prompts = prompts
        self.project_id = project_id
        self.metadata = metadata or {}
        self.description = description


class AnalysisParameters:
    """Parameters for creating an analysis session."""
    
    def __init__(
        self,
        min_evaluation_runs: int = 1,
        time_range_days: Optional[int] = None,
        period_start: Optional[str] = None,
        period_end: Optional[str] = None,
        evaluator_types: Optional[List[str]] = None,
        evaluation_hash: Optional[str] = None
    ):
        self.min_evaluation_runs = min_evaluation_runs
        self.time_range_days = time_range_days
        self.period_start = period_start
        self.period_end = period_end
        self.evaluator_types = evaluator_types or []
        self.evaluation_hash = evaluation_hash


class AgentLabClientOptions:
    """Configuration options for the AgentLab client."""
    
    def __init__(
        self,
        api_token: Optional[str] = None,
        token_getter: Optional[TokenGetter] = None,
        base_url: Optional[str] = None
    ):
        # If api_token is not provided, try to get it from environment variable
        if api_token is None:
            api_token = os.getenv('AGENTLAB_API_TOKEN')
        
        self.api_token = api_token
        self.token_getter = token_getter
        self.base_url = base_url or "https://api.agentlab.vectorlabs.cz"


class AgentLabClient:
    """Main client for interacting with the AgentLab evaluation platform."""
    
    def __init__(self, options: Optional[AgentLabClientOptions] = None):
        """Initialize the AgentLab client.
        
        Args:
            options: Configuration options for the client. If None, uses default options.
        """
        if options is None:
            options = AgentLabClientOptions()
        self._base_url = options.base_url
        self._get_token = None
        self._auth_context = None
        
        # Set up token getter
        if options.token_getter:
            self._get_token = options.token_getter
        elif options.api_token:
            self._get_token = self._create_static_token_getter(options.api_token)
        
        # Create service clients (0.5.0 API uses address instead of base_url/http_client)
        # The new clients extend ConnectClientSync which handles HTTP internally with httpx
        self.evaluations = EvaluationServiceClientSync(address=self._base_url)
        self.iam = IAMServiceClientSync(address=self._base_url)
        self.agents = AgentServiceClientSync(address=self._base_url)
        self.analysis = AgentAnalysisServiceClientSync(address=self._base_url)
    
    def _create_static_token_getter(self, token: str) -> Callable[[], str]:
        """Create a token getter that returns a static token."""
        def get_token():
            return token
        return get_token
    
    def _get_auth_headers(self) -> Dict[str, str]:
        """Get authentication headers for requests."""
        headers = {}
        if self._get_token:
            try:
                token = self._get_token()
                if token:
                    headers["Authorization"] = f"Bearer {token}"
                else:
                    print("⚠️  No token available for authenticated request")
            except Exception as error:
                print(f"❌ Failed to get authentication token: {error}")
        else:
            print("⚠️  No token getter provided for request")
        return headers
    
    def _get_auth_context(self):
        """Initialize auth context on client creation (called automatically)."""
        if self._auth_context:
            return self._auth_context
        
        request = iam_service_pb2.GetAuthContextRequest()
        
        try:
            self._auth_context = self.iam.get_auth_context(
                request, 
                headers=self._get_auth_headers()
            )
            return self._auth_context
        except Exception as e:
            raise AuthenticationError(f"Failed to get auth context: {e}")
    
    def _get_project_id(self, project_id: Optional[str] = None) -> str:
        """Get project ID, either from parameter or auto-filled from auth context."""
        if project_id:
            return project_id
        
        # Auto-fill projectId from auth context
        try:
            auth_context = self._get_auth_context()
            auto_project_id = getattr(auth_context, 'project_id', None)
            if auto_project_id:
                return auto_project_id
        except Exception:
            pass  # Fall through to error
        
        raise AgentLabError(
            "project_id is required. Please provide it explicitly or ensure you have access to at least one project."
        )
    
    def run_evaluation(self, options: CreateEvaluationOptions):
        """Create a new evaluation run using multiple evaluators.
        
        Args:
            options: Configuration for the evaluation run
            
        Returns:
            EvaluationRun: The created evaluation run (pythonic model)
            
        Raises:
            AgentLabError: If projectId is not provided and can't be auto-filled
        """
        # Get project ID
        project_id = self._get_project_id(options.project_id)
        
        # Convert metadata to ScoreValue objects
        metadata_entries = {}
        for key, value in options.metadata.items():
            score_value = evaluation_pb2.ScoreValue()
            if isinstance(value, str):
                score_value.string_value = value
            elif isinstance(value, bool):
                score_value.bool_value = value 
            elif isinstance(value, int):
                score_value.int_value = value
            elif isinstance(value, float):
                score_value.float_value = value
            else:
                score_value.string_value = str(value)
            metadata_entries[key] = score_value
        
        # Format evaluator names with full resource paths
        evaluator_names = []
        for name in options.evaluator_names:
            if name.startswith("projects/"):
                evaluator_names.append(name)
            else:
                evaluator_names.append(f"projects/{project_id}/evaluators/{name}")
        
        # Create the request
        request = evaluation_pb2.RunEvaluationRequest(
            parent=f"projects/{project_id}",
            evaluator_names=evaluator_names,
            user_question=options.user_question,
            agent_answer=options.agent_answer,
            ground_truth=options.ground_truth or "",
            instructions=options.instructions or "",
            agent_name=options.agent_name,
            agent_version=options.agent_version,
            metadata=metadata_entries
        )
        
        try:
            response = self.evaluations.run_evaluation(
                request,
                headers=self._get_auth_headers()
            )
            
            # Always convert to pythonic model
            return convert_evaluation_run(response)
        except Exception as e:
            raise APIError(f"Failed to run evaluation: {e}")
    
    def get_evaluation_run(self, name: str):
        """Get an evaluation run by its name.
        
        Args:
            name: The name/ID of the evaluation run
            
        Returns:
            EvaluationRun: The evaluation run (pythonic model)
        """
        request = evaluation_pb2.GetEvaluationRunRequest(name=name)
        
        try:
            response = self.evaluations.get_evaluation_run(
                request,
                headers=self._get_auth_headers()
            )
            
            # Always convert to pythonic model
            return convert_evaluation_run(response)
        except Exception as e:
            raise APIError(f"Failed to get evaluation run: {e}")
    
    def list_evaluators(self, project_id: Optional[str] = None):
        """List available evaluators for a project.
        
        Args:
            project_id: The project ID (will be auto-filled if not provided)
            
        Returns:
            ListEvaluatorsResponse: The list of evaluators (pythonic model)
        """
        resolved_project_id = self._get_project_id(project_id)
        request = evaluation_pb2.ListEvaluatorsRequest(
            parent=f"projects/{resolved_project_id}",
            page_size=50,
            page_token=""
        )
        
        try:
            response = self.evaluations.list_evaluators(
                request,
                headers=self._get_auth_headers()
            )
            
            # Always convert to pythonic model
            return convert_list_evaluators_response(response)
        except Exception as e:
            raise APIError(f"Failed to list evaluators: {e}")
    
    def get_evaluator(self, name: str):
        """Get a specific evaluator.
        
        Args:
            name: The name/ID of the evaluator
            
        Returns:
            Evaluator: The evaluator (pythonic model)
        """
        request = evaluation_pb2.GetEvaluatorRequest(name=name)
        
        try:
            response = self.evaluations.get_evaluator(
                request,
                headers=self._get_auth_headers()
            )
            
            # Always convert to pythonic model
            return convert_evaluator(response)
        except Exception as e:
            raise APIError(f"Failed to get evaluator: {e}")
    
    def list_evaluation_runs(self, project_id: Optional[str] = None):
        """List evaluation runs for a project.
        
        Args:
            project_id: The project ID (will be auto-filled if not provided)
            
        Returns:
            ListEvaluationRunsResponse: The list of evaluation runs (pythonic model)
        """
        resolved_project_id = self._get_project_id(project_id)
        request = evaluation_pb2.ListEvaluationRunsRequest(
            parent=f"projects/{resolved_project_id}",
            page_size=50,
            page_token="",
            filter=""
        )
        
        try:
            response = self.evaluations.list_evaluation_runs(
                request,
                headers=self._get_auth_headers()
            )
            
            # Always convert to pythonic model
            return convert_list_evaluation_runs_response(response)
        except Exception as e:
            raise APIError(f"Failed to list evaluation runs: {e}")
    
    def get_evaluation_result(self, name: str):
        """Get evaluation result with structured evaluator results.
        
        Args:
            name: The name/ID of the evaluation run
            
        Returns:
            dict: Dictionary containing 'run' and 'results' keys
        """
        run = self.get_evaluation_run(name)
        
        # Parse JSON outputs from evaluator results
        results = {}
        evaluator_results = getattr(run, 'evaluator_results', {})
        
        for evaluator_name, result in evaluator_results.items():
            try:
                output = getattr(result, 'output', '')
                results[evaluator_name] = json.loads(output)
            except (json.JSONDecodeError, AttributeError) as error:
                print(f"Failed to parse output for evaluator {evaluator_name}: {error}")
                results[evaluator_name] = {"raw": getattr(result, 'output', '')}
        
        return {
            "run": run,
            "results": results
        }
    
    def get_agent_version(self, agent_name: str, version: str, project_id: Optional[str] = None):
        """Get an agent version by agent name and version.
        
        Args:
            agent_name: The name of the agent
            version: The version of the agent
            project_id: The project ID (will be auto-filled if not provided)
            
        Returns:
            AgentVersion: The agent version (pythonic model)
        """
        resolved_project_id = self._get_project_id(project_id)
        name = f"projects/{resolved_project_id}/agents/{agent_name}/versions/{version}"
        
        request = agent_service_pb2.GetAgentVersionRequest(name=name)
        
        try:
            response = self.agents.get_agent_version(
                request,
                headers=self._get_auth_headers()
            )
            
            # Convert to pythonic model
            return convert_agent_version(response)
        except Exception as e:
            # Check if it's a 404 or NOT_FOUND error and re-raise with more context
            if "404" in str(e) or "NOT_FOUND" in str(e):
                from .exceptions import APIError
                raise APIError(f"Agent version '{agent_name}' version '{version}' not found (404): {e}")
            raise APIError(f"Failed to get agent version: {e}")
    
    def create_agent_version(self, options: CreateAgentVersionOptions):
        """Create a new agent version.
        
        Args:
            options: Configuration for creating the agent version
            
        Returns:
            AgentVersion: The created agent version (pythonic model)
        """
        resolved_project_id = self._get_project_id(options.project_id)
        
        # Convert metadata to google.protobuf.Struct
        from google.protobuf import struct_pb2
        metadata_struct = None
        if options.metadata:
            metadata_struct = struct_pb2.Struct()
            for key, value in options.metadata.items():
                if isinstance(value, str):
                    metadata_struct.fields[key].string_value = value
                elif isinstance(value, bool):
                    metadata_struct.fields[key].bool_value = value
                elif isinstance(value, int):
                    metadata_struct.fields[key].number_value = float(value)
                elif isinstance(value, float):
                    metadata_struct.fields[key].number_value = value
                else:
                    metadata_struct.fields[key].string_value = str(value)
        
        request = agent_service_pb2.CreateAgentVersionRequest(
            parent=f"projects/{resolved_project_id}",
            agent_name=options.agent_name,
            version=options.version,
            prompts=options.prompts,
            metadata=metadata_struct,
            description=options.description or ""
        )
        
        try:
            response = self.agents.create_agent_version(
                request,
                headers=self._get_auth_headers()
            )
            
            # Convert to pythonic model
            return convert_agent_version(response)
        except Exception as e:
            raise APIError(f"Failed to create agent version: {e}")
    
    def publish_agent_version(self, options: CreateAgentVersionOptions):
        """Publish (create or update) an agent version. This is idempotent and allows adding fields.
        
        This method is preferred over create_agent_version as it:
        - Is idempotent (can be called multiple times)
        - Allows adding new fields to existing versions (e.g., prompts, metadata keys)
        - Creates the agent if it doesn't exist
        
        Args:
            options: Configuration for publishing the agent version
            
        Returns:
            AgentVersion: The published agent version (pythonic model)
        """
        resolved_project_id = self._get_project_id(options.project_id)
        parent = f"projects/{resolved_project_id}/agents/{options.agent_name}"
        
        # Convert metadata to string map (PublishAgentVersionRequest uses map<string, string>)
        metadata_map = {}
        if options.metadata:
            for key, value in options.metadata.items():
                metadata_map[key] = str(value)
        
        request = agent_service_pb2.PublishAgentVersionRequest(
            parent=parent,
            version=options.version,
            prompts=options.prompts,
            metadata=metadata_map,
            create_agent_if_missing=True
        )
        
        try:
            response = self.agents.publish_agent_version(
                request,
                headers=self._get_auth_headers()
            )
            
            # Convert to pythonic model
            return convert_agent_version(response)
        except Exception as e:
            raise APIError(f"Failed to publish agent version: {e}")
    
    def list_agent_versions(self, agent_name: str, project_id: Optional[str] = None):
        """List all versions for an agent.
        
        Args:
            agent_name: The name of the agent
            project_id: The project ID (will be auto-filled if not provided)
            
        Returns:
            ListAgentVersionsResponse: The list of agent versions (pythonic model)
        """
        resolved_project_id = self._get_project_id(project_id)
        parent = f"projects/{resolved_project_id}/agents/{agent_name}"
        
        request = agent_service_pb2.ListAgentVersionsRequest(
            parent=parent,
            page_size=50,
            page_token=""
        )
        
        try:
            response = self.agents.list_agent_versions(
                request,
                headers=self._get_auth_headers()
            )
            
            # Convert to pythonic model
            return convert_list_agent_versions_response(response)
        except Exception as e:
            raise APIError(f"Failed to list agent versions: {e}")
    
    def analyze_agent(self, agent_name: str, version: str, analysis_parameters: AnalysisParameters, project_id: Optional[str] = None):
        """Create a new analysis session for an agent version.
        
        Args:
            agent_name: The name of the agent
            version: The version of the agent to analyze
            analysis_parameters: Parameters for the analysis
            project_id: The project ID (will be auto-filled if not provided)
            
        Returns:
            AnalysisSession: The created analysis session (pythonic model)
        """
        resolved_project_id = self._get_project_id(project_id)
        agent_version_name = f"projects/{resolved_project_id}/agents/{agent_name}/versions/{version}"
        
        # Create the analysis parameters protobuf object
        from google.protobuf import timestamp_pb2
        from datetime import datetime
        
        analysis_params_pb = analysis_service_pb2.AnalysisParameters(
            min_evaluation_runs=analysis_parameters.min_evaluation_runs,
            evaluator_types=analysis_parameters.evaluator_types,
            evaluation_hash=analysis_parameters.evaluation_hash or ""
        )
        
        # Handle time range
        if analysis_parameters.time_range_days:
            analysis_params_pb.time_range_days = analysis_parameters.time_range_days
        
        # Handle period start/end (ISO format strings to timestamp)
        if analysis_parameters.period_start:
            try:
                start_dt = datetime.fromisoformat(analysis_parameters.period_start.replace('Z', '+00:00'))
                timestamp = timestamp_pb2.Timestamp()
                timestamp.FromDatetime(start_dt)
                analysis_params_pb.period_start.CopyFrom(timestamp)
            except ValueError as e:
                raise APIError(f"Invalid period_start format: {e}")
        
        if analysis_parameters.period_end:
            try:
                end_dt = datetime.fromisoformat(analysis_parameters.period_end.replace('Z', '+00:00'))
                timestamp = timestamp_pb2.Timestamp()
                timestamp.FromDatetime(end_dt)
                analysis_params_pb.period_end.CopyFrom(timestamp)
            except ValueError as e:
                raise APIError(f"Invalid period_end format: {e}")
        
        # Create the request
        request = analysis_service_pb2.AnalyzeAgentRequest(
            name=agent_version_name,
            analysis_parameters=analysis_params_pb
        )
        
        try:
            response = self.analysis.analyze_agent(
                request,
                headers=self._get_auth_headers()
            )
            
            # Convert to pythonic model
            return convert_analysis_session(response.session)
        except Exception as e:
            raise APIError(f"Failed to analyze agent: {e}")
    
    def get_analysis_session(self, session_id: str, project_id: Optional[str] = None):
        """Get an analysis session by its ID.
        
        Args:
            session_id: The ID of the analysis session
            project_id: The project ID (will be auto-filled if not provided)
            
        Returns:
            AnalysisSession: The analysis session (pythonic model)
        """
        resolved_project_id = self._get_project_id(project_id)
        session_name = f"projects/{resolved_project_id}/analysis-sessions/{session_id}"
        
        request = analysis_service_pb2.GetAnalysisSessionRequest(name=session_name)
        
        try:
            response = self.analysis.get_analysis_session(
                request,
                headers=self._get_auth_headers()
            )
            
            # Convert to pythonic model
            return convert_analysis_session(response)
        except Exception as e:
            raise APIError(f"Failed to get analysis session: {e}")
    
    def list_analysis_sessions(self, project_id: Optional[str] = None, page_size: int = 50, page_token: str = ""):
        """List analysis sessions for a project.
        
        Args:
            project_id: The project ID (will be auto-filled if not provided)
            page_size: Number of sessions to return per page
            page_token: Token for pagination
            
        Returns:
            ListAnalysisSessionsResponse: The list of analysis sessions (pythonic model)
        """
        resolved_project_id = self._get_project_id(project_id)
        parent = f"projects/{resolved_project_id}"
        
        request = analysis_service_pb2.ListAnalysisSessionsRequest(
            parent=parent,
            page_size=page_size,
            page_token=page_token
        )
        
        try:
            response = self.analysis.list_analysis_sessions(
                request,
                headers=self._get_auth_headers()
            )
            
            # Convert to pythonic model
            return convert_list_analysis_sessions_response(response)
        except Exception as e:
            raise APIError(f"Failed to list analysis sessions: {e}")

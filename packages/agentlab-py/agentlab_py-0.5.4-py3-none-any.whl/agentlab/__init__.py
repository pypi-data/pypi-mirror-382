"""AgentLab Python Client Library

A Python client library for the AgentLab evaluation platform using Connect RPC.
"""

from .client import AgentLabClient, AgentLabClientOptions, CreateEvaluationOptions, CreateAgentVersionOptions, AnalysisParameters
from .exceptions import AgentLabError, AuthenticationError, APIError
from .models import (
    EvaluationRun, EvaluatorResult, Evaluator,
    ListEvaluatorsResponse, ListEvaluationRunsResponse,
    EvaluationState, EvaluatorResultState,
    Agent, AgentVersion, ListAgentVersionsResponse,
    # Analysis models
    AnalysisStatus, OptimizationType, Priority, TrendDirection, DefectCategoryType,
    OptimizationOpportunity, FailurePattern, EvaluatorStats, StatisticalSummary,
    DefectExample, DefectCategory, DefectTrend, DefectFrequencyAnalysis,
    AnalysisData, AnalysisSession, ListAnalysisSessionsResponse
)
from .converters import convert_protobuf_object

__version__ = "0.1.0"
__all__ = [
    "AgentLabClient", "AgentLabClientOptions", "CreateEvaluationOptions", "CreateAgentVersionOptions", "AnalysisParameters",
    "AgentLabError", "AuthenticationError", "APIError",
    "EvaluationRun", "EvaluatorResult", "Evaluator",
    "ListEvaluatorsResponse", "ListEvaluationRunsResponse",
    "EvaluationState", "EvaluatorResultState",
    "Agent", "AgentVersion", "ListAgentVersionsResponse",
    # Analysis exports
    "AnalysisStatus", "OptimizationType", "Priority", "TrendDirection", "DefectCategoryType",
    "OptimizationOpportunity", "FailurePattern", "EvaluatorStats", "StatisticalSummary",
    "DefectExample", "DefectCategory", "DefectTrend", "DefectFrequencyAnalysis",
    "AnalysisData", "AnalysisSession", "ListAnalysisSessionsResponse",
    "convert_protobuf_object"
]

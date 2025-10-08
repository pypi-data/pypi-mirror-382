"""Converters for transforming protobuf objects to pythonic models.

This module provides functions to convert protobuf-generated objects into
more pythonic wrapper classes that are easier to work with.
"""

from datetime import datetime
from typing import Dict, List, Union, Any

from .models import (
    EvaluationRun, EvaluatorResult, Evaluator, 
    ListEvaluatorsResponse, ListEvaluationRunsResponse,
    EvaluationState, EvaluatorResultState,
    Agent, AgentVersion, ListAgentVersionsResponse,
    AnalysisStatus, OptimizationType, Priority, TrendDirection, DefectCategoryType,
    OptimizationOpportunity, FailurePattern, EvaluatorStats, StatisticalSummary,
    DefectExample, DefectCategory, DefectTrend, DefectFrequencyAnalysis,
    AnalysisData, AnalysisSession, ListAnalysisSessionsResponse
)


def _parse_timestamp(timestamp_pb) -> datetime:
    """Convert protobuf timestamp to datetime."""
    if timestamp_pb is None:
        return None
    
    try:
        # Protobuf timestamps have seconds and nanos fields
        seconds = getattr(timestamp_pb, 'seconds', 0)
        nanos = getattr(timestamp_pb, 'nanos', 0)
        return datetime.fromtimestamp(seconds + nanos / 1_000_000_000)
    except (AttributeError, TypeError, ValueError):
        return None


def _parse_score_value(score_value_pb) -> Union[str, int, bool, float]:
    """Convert protobuf ScoreValue to Python type."""
    if score_value_pb is None:
        return None
    
    # ScoreValue is a oneof field - check which type it contains
    if hasattr(score_value_pb, 'string_value') and score_value_pb.HasField('string_value'):
        return score_value_pb.string_value
    elif hasattr(score_value_pb, 'int_value') and score_value_pb.HasField('int_value'):
        return score_value_pb.int_value
    elif hasattr(score_value_pb, 'bool_value') and score_value_pb.HasField('bool_value'):
        return score_value_pb.bool_value
    elif hasattr(score_value_pb, 'float_value') and score_value_pb.HasField('float_value'):
        return score_value_pb.float_value
    
    return None


def _parse_enum_state(state_value, enum_class) -> Any:
    """Convert protobuf enum value to our enum."""
    if isinstance(state_value, int):
        # Convert int enum value to string first
        state_names = {
            0: "STATE_UNSPECIFIED",
            1: "PENDING", 
            2: "RUNNING",
            3: "SUCCEEDED",
            4: "FAILED"
        }
        state_str = state_names.get(state_value, "STATE_UNSPECIFIED")
    else:
        state_str = str(state_value)
    
    # Try to find matching enum value
    for enum_val in enum_class:
        if enum_val.value == state_str:
            return enum_val
    
    return enum_class.UNSPECIFIED


def _parse_analysis_enum(enum_value, enum_class) -> Any:
    """Convert protobuf enum value to analysis enum."""
    if isinstance(enum_value, int):
        # Handle different enum types by checking the enum class
        if enum_class == AnalysisStatus:
            enum_names = {
                0: "ANALYSIS_STATUS_UNSPECIFIED",
                1: "ANALYSIS_STATUS_PENDING",
                2: "ANALYSIS_STATUS_PROCESSING", 
                3: "ANALYSIS_STATUS_COMPLETED",
                4: "ANALYSIS_STATUS_FAILED"
            }
        elif enum_class == OptimizationType:
            enum_names = {
                0: "OPTIMIZATION_TYPE_UNSPECIFIED",
                1: "OPTIMIZATION_TYPE_PROMPT_REFINEMENT",
                2: "OPTIMIZATION_TYPE_PARAMETER_ADJUSTMENT",
                3: "OPTIMIZATION_TYPE_EVALUATION_FOCUS"
            }
        elif enum_class == Priority:
            enum_names = {
                0: "PRIORITY_UNSPECIFIED",
                1: "PRIORITY_LOW",
                2: "PRIORITY_MEDIUM",
                3: "PRIORITY_HIGH"
            }
        elif enum_class == TrendDirection:
            enum_names = {
                0: "TREND_DIRECTION_UNSPECIFIED",
                1: "TREND_DIRECTION_IMPROVING",
                2: "TREND_DIRECTION_DECLINING",
                3: "TREND_DIRECTION_STABLE"
            }
        elif enum_class == DefectCategoryType:
            enum_names = {
                0: "DEFECT_CATEGORY_TYPE_UNSPECIFIED",
                1: "DEFECT_CATEGORY_TYPE_DUPLICATE_INFORMATION",
                2: "DEFECT_CATEGORY_TYPE_MISSING_SPECIFICITY",
                3: "DEFECT_CATEGORY_TYPE_INSTRUCTION_FOLLOWING_FAILURES",
                4: "DEFECT_CATEGORY_TYPE_CONFLICTING_INFORMATION",
                5: "DEFECT_CATEGORY_TYPE_MISSING_KEY_INFORMATION",
                6: "DEFECT_CATEGORY_TYPE_FORMAT_STRUCTURE_PROBLEMS",
                7: "DEFECT_CATEGORY_TYPE_HALLUCINATION_PATTERNS",
                8: "DEFECT_CATEGORY_TYPE_OVER_SPECIFICITY",
                9: "DEFECT_CATEGORY_TYPE_TONE_STYLE_ISSUES",
                10: "DEFECT_CATEGORY_TYPE_CONTEXT_MISUNDERSTANDING"
            }
        else:
            enum_names = {}
        
        enum_str = enum_names.get(enum_value, f"{enum_class.__name__.upper()}_UNSPECIFIED")
    else:
        enum_str = str(enum_value)
    
    # Try to find matching enum value
    for enum_val in enum_class:
        if enum_val.value == enum_str:
            return enum_val
    
    return enum_class.UNSPECIFIED


def convert_evaluator_result(evaluator_result_pb) -> EvaluatorResult:
    """Convert protobuf EvaluatorResult to pythonic EvaluatorResult."""
    return EvaluatorResult(
        evaluator_name=getattr(evaluator_result_pb, 'evaluator_name', ''),
        output=getattr(evaluator_result_pb, 'output', ''),
        state=_parse_enum_state(getattr(evaluator_result_pb, 'state', 0), EvaluatorResultState),
        error_message=getattr(evaluator_result_pb, 'error_message', None) or None
    )


def convert_evaluation_run(evaluation_run_pb) -> EvaluationRun:
    """Convert protobuf EvaluationRun to pythonic EvaluationRun."""
    
    # Convert evaluator results
    evaluator_results = {}
    evaluator_results_pb = getattr(evaluation_run_pb, 'evaluator_results', {})
    if hasattr(evaluator_results_pb, 'items'):
        for name, result_pb in evaluator_results_pb.items():
            evaluator_results[name] = convert_evaluator_result(result_pb)
    
    # Convert metadata
    metadata = {}
    metadata_pb = getattr(evaluation_run_pb, 'metadata', {})
    if hasattr(metadata_pb, 'items'):
        for key, score_value_pb in metadata_pb.items():
            metadata[key] = _parse_score_value(score_value_pb)
    
    # Convert evaluator names list
    evaluator_names = []
    evaluator_names_pb = getattr(evaluation_run_pb, 'evaluator_names', [])
    if hasattr(evaluator_names_pb, '__iter__'):
        evaluator_names = list(evaluator_names_pb)
    
    return EvaluationRun(
        name=getattr(evaluation_run_pb, 'name', ''),
        state=_parse_enum_state(getattr(evaluation_run_pb, 'state', 0), EvaluationState),
        evaluator_names=evaluator_names,
        user_question=getattr(evaluation_run_pb, 'user_question', ''),
        agent_answer=getattr(evaluation_run_pb, 'agent_answer', ''),
        ground_truth=getattr(evaluation_run_pb, 'ground_truth', ''),
        instructions=getattr(evaluation_run_pb, 'instructions', ''),
        evaluator_results=evaluator_results,
        agent_name=getattr(evaluation_run_pb, 'agent_name', ''),
        agent_version=getattr(evaluation_run_pb, 'agent_version', ''),
        evaluation_hash=getattr(evaluation_run_pb, 'evaluation_hash', ''),
        metadata=metadata,
        create_time=_parse_timestamp(getattr(evaluation_run_pb, 'create_time', None)),
        update_time=_parse_timestamp(getattr(evaluation_run_pb, 'update_time', None))
    )


def convert_evaluator(evaluator_pb) -> Evaluator:
    """Convert protobuf Evaluator to pythonic Evaluator."""
    
    # Convert hashed fields list
    hashed_fields = []
    hashed_fields_pb = getattr(evaluator_pb, 'hashed_fields', [])
    if hasattr(hashed_fields_pb, '__iter__'):
        hashed_fields = list(hashed_fields_pb)
    
    return Evaluator(
        name=getattr(evaluator_pb, 'name', ''),
        display_name=getattr(evaluator_pb, 'display_name', ''),
        description=getattr(evaluator_pb, 'description', ''),
        hashed_fields=hashed_fields
    )


def convert_list_evaluators_response(response_pb) -> ListEvaluatorsResponse:
    """Convert protobuf ListEvaluatorsResponse to pythonic version."""
    
    evaluators = []
    evaluators_pb = getattr(response_pb, 'evaluators', [])
    if hasattr(evaluators_pb, '__iter__'):
        evaluators = [convert_evaluator(evaluator_pb) for evaluator_pb in evaluators_pb]
    
    return ListEvaluatorsResponse(
        evaluators=evaluators,
        next_page_token=getattr(response_pb, 'next_page_token', '')
    )


def convert_list_evaluation_runs_response(response_pb) -> ListEvaluationRunsResponse:
    """Convert protobuf ListEvaluationRunsResponse to pythonic version."""
    
    evaluation_runs = []
    evaluation_runs_pb = getattr(response_pb, 'evaluation_runs', [])
    if hasattr(evaluation_runs_pb, '__iter__'):
        evaluation_runs = [convert_evaluation_run(run_pb) for run_pb in evaluation_runs_pb]
    
    return ListEvaluationRunsResponse(
        evaluation_runs=evaluation_runs,
        next_page_token=getattr(response_pb, 'next_page_token', '')
    )


# Convenience function to convert any supported type
def convert_protobuf_object(pb_object):
    """Automatically convert a protobuf object to its pythonic equivalent."""
    
    # Get the object's type name
    type_name = type(pb_object).__name__
    
    # Map type names to converter functions
    converters = {
        'EvaluationRun': convert_evaluation_run,
        'EvaluatorResult': convert_evaluator_result,
        'Evaluator': convert_evaluator,
        'ListEvaluatorsResponse': convert_list_evaluators_response,
        'ListEvaluationRunsResponse': convert_list_evaluation_runs_response,
        'Agent': convert_agent,
        'AgentVersion': convert_agent_version,
        'ListAgentVersionsResponse': convert_list_agent_versions_response,
        'AnalysisSession': convert_analysis_session,
        'ListAnalysisSessionsResponse': convert_list_analysis_sessions_response,
        'AnalysisData': convert_analysis_data,
        'OptimizationOpportunity': convert_optimization_opportunity,
        'FailurePattern': convert_failure_pattern,
        'StatisticalSummary': convert_statistical_summary,
        'DefectCategory': convert_defect_category,
        'DefectFrequencyAnalysis': convert_defect_frequency_analysis,
    }
    
    converter = converters.get(type_name)
    if converter:
        return converter(pb_object)
    
    # If no specific converter found, return the original object
    return pb_object


def _parse_struct_to_dict(struct_pb) -> Dict[str, Union[str, int, bool, float]]:
    """Convert protobuf Struct to Python dict."""
    if struct_pb is None:
        return {}
    
    result = {}
    for key, value in struct_pb.fields.items():
        # Convert protobuf Value to python type
        if value.HasField('string_value'):
            result[key] = value.string_value
        elif value.HasField('number_value'):
            result[key] = value.number_value
        elif value.HasField('bool_value'):
            result[key] = value.bool_value
        elif value.HasField('null_value'):
            result[key] = None
        else:
            # For complex types, convert to string
            result[key] = str(value)
    
    return result


def convert_agent(agent_pb) -> Agent:
    """Convert protobuf Agent to pythonic Agent."""
    return Agent(
        name=getattr(agent_pb, 'name', ''),
        display_name=getattr(agent_pb, 'display_name', ''),
        description=getattr(agent_pb, 'description', ''),
        parent=getattr(agent_pb, 'parent', ''),
        created_by=getattr(agent_pb, 'created_by', ''),
        create_time=_parse_timestamp(getattr(agent_pb, 'create_time', None)),
        update_time=_parse_timestamp(getattr(agent_pb, 'update_time', None))
    )


def convert_agent_version(agent_version_pb) -> AgentVersion:
    """Convert protobuf AgentVersion to pythonic AgentVersion."""
    
    # Convert prompts dict
    prompts = {}
    prompts_pb = getattr(agent_version_pb, 'prompts', {})
    if hasattr(prompts_pb, 'items'):
        for key, value in prompts_pb.items():
            prompts[key] = value
    
    # Convert metadata from google.protobuf.Struct
    metadata = _parse_struct_to_dict(getattr(agent_version_pb, 'metadata', None))
    
    return AgentVersion(
        name=getattr(agent_version_pb, 'name', ''),
        version=getattr(agent_version_pb, 'version', ''),
        prompts=prompts,
        content_hash=getattr(agent_version_pb, 'content_hash', ''),
        parent=getattr(agent_version_pb, 'parent', ''),
        created_by=getattr(agent_version_pb, 'created_by', ''),
        updated_by=getattr(agent_version_pb, 'updated_by', ''),
        metadata=metadata,
        create_time=_parse_timestamp(getattr(agent_version_pb, 'create_time', None)),
        update_time=_parse_timestamp(getattr(agent_version_pb, 'update_time', None))
    )


def convert_list_agent_versions_response(response_pb) -> ListAgentVersionsResponse:
    """Convert protobuf ListAgentVersionsResponse to pythonic version."""
    
    agent_versions = []
    agent_versions_pb = getattr(response_pb, 'agent_versions', [])
    if hasattr(agent_versions_pb, '__iter__'):
        agent_versions = [convert_agent_version(version_pb) for version_pb in agent_versions_pb]
    
    return ListAgentVersionsResponse(
        agent_versions=agent_versions,
        next_page_token=getattr(response_pb, 'next_page_token', '')
    )


def convert_optimization_opportunity(opp_pb) -> OptimizationOpportunity:
    """Convert protobuf OptimizationOpportunity to pythonic version."""
    return OptimizationOpportunity(
        type=_parse_analysis_enum(getattr(opp_pb, 'type', 0), OptimizationType),
        priority=_parse_analysis_enum(getattr(opp_pb, 'priority', 0), Priority),
        description=getattr(opp_pb, 'description', ''),
        suggested_action=getattr(opp_pb, 'suggested_action', ''),
        confidence_score=getattr(opp_pb, 'confidence_score', 0.0)
    )


def convert_failure_pattern(pattern_pb) -> FailurePattern:
    """Convert protobuf FailurePattern to pythonic version."""
    examples = []
    examples_pb = getattr(pattern_pb, 'examples', [])
    if hasattr(examples_pb, '__iter__'):
        examples = list(examples_pb)
    
    return FailurePattern(
        pattern_id=getattr(pattern_pb, 'pattern_id', ''),
        description=getattr(pattern_pb, 'description', ''),
        frequency=getattr(pattern_pb, 'frequency', 0),
        examples=examples
    )


def convert_evaluator_stats(stats_pb) -> EvaluatorStats:
    """Convert protobuf EvaluatorStats to pythonic version."""
    return EvaluatorStats(
        average_score=getattr(stats_pb, 'average_score', 0.0),
        min_score=getattr(stats_pb, 'min_score', 0.0),
        max_score=getattr(stats_pb, 'max_score', 0.0),
        total_evaluations=getattr(stats_pb, 'total_evaluations', 0),
        successful_evaluations=getattr(stats_pb, 'successful_evaluations', 0)
    )


def convert_statistical_summary(summary_pb) -> StatisticalSummary:
    """Convert protobuf StatisticalSummary to pythonic version."""
    evaluator_stats = {}
    evaluator_stats_pb = getattr(summary_pb, 'evaluator_stats', {})
    if hasattr(evaluator_stats_pb, 'items'):
        for name, stats_pb in evaluator_stats_pb.items():
            evaluator_stats[name] = convert_evaluator_stats(stats_pb)
    
    return StatisticalSummary(
        success_rate=getattr(summary_pb, 'success_rate', 0.0),
        average_score=getattr(summary_pb, 'average_score', 0.0),
        score_std_dev=getattr(summary_pb, 'score_std_dev', 0.0),
        evaluator_stats=evaluator_stats
    )


def convert_defect_example(example_pb) -> DefectExample:
    """Convert protobuf DefectExample to pythonic version."""
    return DefectExample(
        evaluation_run_id=getattr(example_pb, 'evaluation_run_id', ''),
        context=getattr(example_pb, 'context', ''),
        defect_text=getattr(example_pb, 'defect_text', ''),
        rationale=getattr(example_pb, 'rationale', '')
    )


def convert_defect_category(category_pb) -> DefectCategory:
    """Convert protobuf DefectCategory to pythonic version."""
    examples = []
    examples_pb = getattr(category_pb, 'examples', [])
    if hasattr(examples_pb, '__iter__'):
        examples = [convert_defect_example(example_pb) for example_pb in examples_pb]
    
    recommendations = []
    recommendations_pb = getattr(category_pb, 'recommendations', [])
    if hasattr(recommendations_pb, '__iter__'):
        recommendations = list(recommendations_pb)
    
    return DefectCategory(
        category_type=_parse_analysis_enum(getattr(category_pb, 'category_type', 0), DefectCategoryType),
        frequency=getattr(category_pb, 'frequency', 0),
        examples=examples,
        description=getattr(category_pb, 'description', ''),
        severity=getattr(category_pb, 'severity', ''),
        recommendations=recommendations
    )


def convert_defect_trend(trend_pb) -> DefectTrend:
    """Convert protobuf DefectTrend to pythonic version."""
    return DefectTrend(
        category_type=_parse_analysis_enum(getattr(trend_pb, 'category_type', 0), DefectCategoryType),
        direction=_parse_analysis_enum(getattr(trend_pb, 'direction', 0), TrendDirection),
        strength=getattr(trend_pb, 'strength', 0.0)
    )


def convert_defect_frequency_analysis(analysis_pb) -> DefectFrequencyAnalysis:
    """Convert protobuf DefectFrequencyAnalysis to pythonic version."""
    defects_by_category = {}
    defects_by_category_pb = getattr(analysis_pb, 'defects_by_category', {})
    if hasattr(defects_by_category_pb, 'items'):
        for key, value in defects_by_category_pb.items():
            defects_by_category[key] = value
    
    defects_by_severity = {}
    defects_by_severity_pb = getattr(analysis_pb, 'defects_by_severity', {})
    if hasattr(defects_by_severity_pb, 'items'):
        for key, value in defects_by_severity_pb.items():
            defects_by_severity[key] = value
    
    defect_trends = []
    defect_trends_pb = getattr(analysis_pb, 'defect_trends', [])
    if hasattr(defect_trends_pb, '__iter__'):
        defect_trends = [convert_defect_trend(trend_pb) for trend_pb in defect_trends_pb]
    
    return DefectFrequencyAnalysis(
        total_defects_found=getattr(analysis_pb, 'total_defects_found', 0),
        defects_by_category=defects_by_category,
        defects_by_severity=defects_by_severity,
        most_common_defect_category=_parse_analysis_enum(getattr(analysis_pb, 'most_common_defect_category', 0), DefectCategoryType),
        defect_trends=defect_trends
    )


def convert_analysis_data(analysis_data_pb) -> AnalysisData:
    """Convert protobuf AnalysisData to pythonic version."""
    failure_patterns = []
    failure_patterns_pb = getattr(analysis_data_pb, 'failure_patterns', [])
    if hasattr(failure_patterns_pb, '__iter__'):
        failure_patterns = [convert_failure_pattern(pattern_pb) for pattern_pb in failure_patterns_pb]
    
    optimization_opportunities = []
    optimization_opportunities_pb = getattr(analysis_data_pb, 'optimization_opportunities', [])
    if hasattr(optimization_opportunities_pb, '__iter__'):
        optimization_opportunities = [convert_optimization_opportunity(opp_pb) for opp_pb in optimization_opportunities_pb]
    
    defect_categories = []
    defect_categories_pb = getattr(analysis_data_pb, 'defect_categories', [])
    if hasattr(defect_categories_pb, '__iter__'):
        defect_categories = [convert_defect_category(cat_pb) for cat_pb in defect_categories_pb]
    
    return AnalysisData(
        evaluation_runs_analyzed=getattr(analysis_data_pb, 'evaluation_runs_analyzed', 0),
        failure_patterns=failure_patterns,
        statistical_summary=convert_statistical_summary(getattr(analysis_data_pb, 'statistical_summary', None)),
        optimization_opportunities=optimization_opportunities,
        defect_categories=defect_categories,
        defect_frequency_analysis=convert_defect_frequency_analysis(getattr(analysis_data_pb, 'defect_frequency_analysis', None)),
        natural_language_report=getattr(analysis_data_pb, 'natural_language_report', '')
    )


def convert_analysis_session(session_pb) -> AnalysisSession:
    """Convert protobuf AnalysisSession to pythonic version."""
    return AnalysisSession(
        id=getattr(session_pb, 'id', ''),
        project_id=getattr(session_pb, 'project_id', ''),
        agent_version_id=getattr(session_pb, 'agent_version_id', ''),
        analysis_period_start=_parse_timestamp(getattr(session_pb, 'analysis_period_start', None)),
        analysis_period_end=_parse_timestamp(getattr(session_pb, 'analysis_period_end', None)),
        analysis_data=convert_analysis_data(getattr(session_pb, 'analysis_data', None)),
        created_at=_parse_timestamp(getattr(session_pb, 'created_at', None)),
        updated_at=_parse_timestamp(getattr(session_pb, 'updated_at', None)),
        status=_parse_analysis_enum(getattr(session_pb, 'status', 0), AnalysisStatus),
        error_message=getattr(session_pb, 'error_message', None) or None
    )


def convert_list_analysis_sessions_response(response_pb) -> ListAnalysisSessionsResponse:
    """Convert protobuf ListAnalysisSessionsResponse to pythonic version."""
    sessions = []
    sessions_pb = getattr(response_pb, 'sessions', [])
    if hasattr(sessions_pb, '__iter__'):
        sessions = [convert_analysis_session(session_pb) for session_pb in sessions_pb]
    
    return ListAnalysisSessionsResponse(
        sessions=sessions,
        next_page_token=getattr(response_pb, 'next_page_token', ''),
        previous_page_token=getattr(response_pb, 'previous_page_token', ''),
        total_size=getattr(response_pb, 'total_size', 0)
    )

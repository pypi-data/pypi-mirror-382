"""Pythonic models for AgentLab SDK.

This module provides more pythonic wrapper classes for the protobuf-generated models,
making them easier to work with, serialize, and print.
"""

import json
from datetime import datetime
from typing import Dict, List, Optional, Union, Any
from dataclasses import dataclass, field
from enum import Enum


class EvaluationState(Enum):
    """State of an evaluation run."""
    UNSPECIFIED = "STATE_UNSPECIFIED"
    PENDING = "PENDING" 
    RUNNING = "RUNNING"
    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"


class EvaluatorResultState(Enum):
    """State of an individual evaluator result."""
    UNSPECIFIED = "STATE_UNSPECIFIED"
    PENDING = "PENDING"
    RUNNING = "RUNNING" 
    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"


class AnalysisStatus(Enum):
    """Status of an analysis session."""
    UNSPECIFIED = "ANALYSIS_STATUS_UNSPECIFIED"
    PENDING = "ANALYSIS_STATUS_PENDING"
    PROCESSING = "ANALYSIS_STATUS_PROCESSING"
    COMPLETED = "ANALYSIS_STATUS_COMPLETED"
    FAILED = "ANALYSIS_STATUS_FAILED"


class OptimizationType(Enum):
    """Type of optimization opportunity."""
    UNSPECIFIED = "OPTIMIZATION_TYPE_UNSPECIFIED"
    PROMPT_REFINEMENT = "OPTIMIZATION_TYPE_PROMPT_REFINEMENT"
    PARAMETER_ADJUSTMENT = "OPTIMIZATION_TYPE_PARAMETER_ADJUSTMENT"
    EVALUATION_FOCUS = "OPTIMIZATION_TYPE_EVALUATION_FOCUS"


class Priority(Enum):
    """Priority level."""
    UNSPECIFIED = "PRIORITY_UNSPECIFIED"
    LOW = "PRIORITY_LOW"
    MEDIUM = "PRIORITY_MEDIUM"
    HIGH = "PRIORITY_HIGH"


class TrendDirection(Enum):
    """Direction of a trend."""
    UNSPECIFIED = "TREND_DIRECTION_UNSPECIFIED"
    IMPROVING = "TREND_DIRECTION_IMPROVING"
    DECLINING = "TREND_DIRECTION_DECLINING"
    STABLE = "TREND_DIRECTION_STABLE"


class DefectCategoryType(Enum):
    """Type of defect category."""
    UNSPECIFIED = "DEFECT_CATEGORY_TYPE_UNSPECIFIED"
    DUPLICATE_INFORMATION = "DEFECT_CATEGORY_TYPE_DUPLICATE_INFORMATION"
    MISSING_SPECIFICITY = "DEFECT_CATEGORY_TYPE_MISSING_SPECIFICITY"
    INSTRUCTION_FOLLOWING_FAILURES = "DEFECT_CATEGORY_TYPE_INSTRUCTION_FOLLOWING_FAILURES"
    CONFLICTING_INFORMATION = "DEFECT_CATEGORY_TYPE_CONFLICTING_INFORMATION"
    MISSING_KEY_INFORMATION = "DEFECT_CATEGORY_TYPE_MISSING_KEY_INFORMATION"
    FORMAT_STRUCTURE_PROBLEMS = "DEFECT_CATEGORY_TYPE_FORMAT_STRUCTURE_PROBLEMS"
    HALLUCINATION_PATTERNS = "DEFECT_CATEGORY_TYPE_HALLUCINATION_PATTERNS"
    OVER_SPECIFICITY = "DEFECT_CATEGORY_TYPE_OVER_SPECIFICITY"
    TONE_STYLE_ISSUES = "DEFECT_CATEGORY_TYPE_TONE_STYLE_ISSUES"
    CONTEXT_MISUNDERSTANDING = "DEFECT_CATEGORY_TYPE_CONTEXT_MISUNDERSTANDING"


@dataclass
class EvaluatorResult:
    """Result from a single evaluator."""
    evaluator_name: str
    output: str
    state: EvaluatorResultState
    error_message: Optional[str] = None
    _evaluation_run: Optional['EvaluationRun'] = None  # Reference to parent evaluation run
    
    @property
    def parsed_output(self) -> Dict[str, Any]:
        """Parse the output JSON if possible, otherwise return raw output in a dict."""
        try:
            return json.loads(self.output)
        except (json.JSONDecodeError, TypeError):
            return {"raw": self.output}
    
    @property
    def score(self) -> Optional[float]:
        """Get the score for this evaluator from the evaluation run metadata."""
        if self._evaluation_run is None:
            # Try to extract score from parsed output as fallback
            parsed = self.parsed_output
            if isinstance(parsed, dict) and "score" in parsed:
                try:
                    return float(parsed["score"])
                except (ValueError, TypeError):
                    pass
            return None
        
        # Look for score in metadata using evaluator name as key
        metadata = self._evaluation_run.metadata
        if self.evaluator_name in metadata:
            score_val = metadata[self.evaluator_name]
            if isinstance(score_val, (int, float)):
                return float(score_val)
        
        # Also try to extract from parsed output
        parsed = self.parsed_output
        if isinstance(parsed, dict) and "score" in parsed:
            try:
                return float(parsed["score"])
            except (ValueError, TypeError):
                pass
        
        return None
    
    def __repr__(self) -> str:
        score = self.score
        return (f"EvaluatorResult(evaluator='{self.evaluator_name}', "
                f"state={self.state.value}, score={score})")


@dataclass  
class EvaluationRun:
    """A complete evaluation run with results from multiple evaluators."""
    name: str
    state: EvaluationState
    evaluator_names: List[str]
    user_question: str
    agent_answer: str
    ground_truth: str
    instructions: str
    evaluator_results: Dict[str, EvaluatorResult]
    agent_name: str
    agent_version: str
    evaluation_hash: str
    metadata: Dict[str, Union[str, int, bool, float]] = field(default_factory=dict)
    create_time: Optional[datetime] = None
    update_time: Optional[datetime] = None
    
    def __post_init__(self):
        """Set up back-references from evaluator results to this evaluation run."""
        for result in self.evaluator_results.values():
            result._evaluation_run = self
    
    def get_evaluator_result(self, evaluator_name: str) -> Optional[EvaluatorResult]:
        """Get result for a specific evaluator."""
        return self.evaluator_results.get(evaluator_name)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to a dictionary suitable for JSON serialization."""
        return {
            "name": self.name,
            "state": self.state.value,
            "evaluator_names": self.evaluator_names,
            "user_question": self.user_question,
            "agent_answer": self.agent_answer,
            "ground_truth": self.ground_truth,
            "instructions": self.instructions,
            "evaluator_results": {
                name: {
                    "evaluator_name": result.evaluator_name,
                    "output": result.parsed_output,
                    "state": result.state.value,
                    "score": result.score,
                    "error_message": result.error_message,
                }
                for name, result in self.evaluator_results.items()
            },
            "agent_name": self.agent_name,
            "agent_version": self.agent_version,
            "evaluation_hash": self.evaluation_hash,
            "metadata": self.metadata,
            "create_time": self.create_time.isoformat() if self.create_time else None,
            "update_time": self.update_time.isoformat() if self.update_time else None,
        }
    
    def to_json(self, indent: int = 2) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)
    
    def __repr__(self) -> str:
        return (f"EvaluationRun(name='{self.name}', state={self.state.value}, "
                f"evaluators={len(self.evaluator_results)}")
    
    def __str__(self) -> str:
        """Provide a nice string representation for printing."""
        lines = [
            f"🧪 Evaluation: {self.name}",
            f"📊 State: {self.state.value}",
            f"🤖 Agent: {self.agent_name} v{self.agent_version}",
            f"❓ Question: {self.user_question}",
            f"💬 Answer: {self.agent_answer}",
            f"✅ Ground Truth: {self.ground_truth}",
        ]
        
        lines.append("\n📋 Evaluator Results:")
        for name, result in self.evaluator_results.items():
            status_emoji = "✅" if result.state is EvaluatorResultState.SUCCEEDED else "❌"
            lines.append(f"  {status_emoji} {result.evaluator_name}: "
                        f"{result.state.value} (score: {result.score:.3f})")
            
            # Add parsed output if available
            try:
                parsed = result.parsed_output
                if "rationale" in parsed:
                    lines.append(f"    💭 {parsed['rationale']}")
            except Exception:
                pass
        
        if self.create_time:
            lines.append(f"\n🕒 Created: {self.create_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        return "\n".join(lines)


@dataclass
class Evaluator:
    """An evaluator definition."""
    name: str
    display_name: str
    description: str
    hashed_fields: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "display_name": self.display_name, 
            "description": self.description,
            "hashed_fields": self.hashed_fields
        }
    
    def to_json(self, indent: int = 2) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)
    
    def __repr__(self) -> str:
        return f"Evaluator(name='{self.name}', display_name='{self.display_name}')"


@dataclass
class ListEvaluatorsResponse:
    """Response containing a list of evaluators."""
    evaluators: List[Evaluator]
    next_page_token: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "evaluators": [evaluator.to_dict() for evaluator in self.evaluators],
            "next_page_token": self.next_page_token
        }
    
    def to_json(self, indent: int = 2) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)


@dataclass  
class ListEvaluationRunsResponse:
    """Response containing a list of evaluation runs."""
    evaluation_runs: List[EvaluationRun] 
    next_page_token: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "evaluation_runs": [run.to_dict() for run in self.evaluation_runs],
            "next_page_token": self.next_page_token
        }
    
    def to_json(self, indent: int = 2) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)


@dataclass
class Agent:
    """An agent definition."""
    name: str
    display_name: str
    description: str
    parent: str
    created_by: str
    create_time: Optional[datetime] = None
    update_time: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "display_name": self.display_name,
            "description": self.description,
            "parent": self.parent,
            "created_by": self.created_by,
            "create_time": self.create_time.isoformat() if self.create_time else None,
            "update_time": self.update_time.isoformat() if self.update_time else None,
        }
    
    def to_json(self, indent: int = 2) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)
    
    def __repr__(self) -> str:
        return f"Agent(name='{self.name}', display_name='{self.display_name}')"


@dataclass
class AgentVersion:
    """An agent version with prompts."""
    name: str
    version: str
    prompts: Dict[str, str]
    content_hash: str
    parent: str
    created_by: str
    updated_by: str
    metadata: Dict[str, Union[str, int, bool, float]] = field(default_factory=dict)
    create_time: Optional[datetime] = None
    update_time: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "version": self.version,
            "prompts": self.prompts,
            "content_hash": self.content_hash,
            "parent": self.parent,
            "created_by": self.created_by,
            "updated_by": self.updated_by,
            "metadata": self.metadata,
            "create_time": self.create_time.isoformat() if self.create_time else None,
            "update_time": self.update_time.isoformat() if self.update_time else None,
        }
    
    def to_json(self, indent: int = 2) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)
    
    def __repr__(self) -> str:
        return f"AgentVersion(name='{self.name}', version='{self.version}', prompts={len(self.prompts)})"
    
    def __str__(self) -> str:
        """Provide a nice string representation for printing."""
        lines = [
            f"🤖 Agent Version: {self.name}",
            f"📄 Version: {self.version}",
            f"🔗 Content Hash: {self.content_hash}",
            f"👤 Created by: {self.created_by}",
        ]
        
        if self.create_time:
            lines.append(f"🕒 Created: {self.create_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        lines.append(f"\n📝 Prompts ({len(self.prompts)}):")
        for prompt_name, prompt_content in self.prompts.items():
            lines.append(f"  • {prompt_name}: {len(prompt_content)} chars")
            # Show a preview of the prompt content
            preview = prompt_content[:100] + "..." if len(prompt_content) > 100 else prompt_content
            lines.append(f"    \"{preview}\"")
        
        if self.metadata:
            lines.append(f"\n🏷️  Metadata:")
            for key, value in self.metadata.items():
                lines.append(f"  • {key}: {value}")
        
        return "\n".join(lines)


@dataclass
class ListAgentVersionsResponse:
    """Response containing a list of agent versions."""
    agent_versions: List[AgentVersion]
    next_page_token: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "agent_versions": [version.to_dict() for version in self.agent_versions],
            "next_page_token": self.next_page_token
        }
    
    def to_json(self, indent: int = 2) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)


@dataclass
class OptimizationOpportunity:
    """An optimization opportunity identified by analysis."""
    type: OptimizationType
    priority: Priority
    description: str
    suggested_action: str
    confidence_score: float
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "type": self.type.value,
            "priority": self.priority.value,
            "description": self.description,
            "suggested_action": self.suggested_action,
            "confidence_score": self.confidence_score
        }


@dataclass
class FailurePattern:
    """A failure pattern identified in evaluations."""
    pattern_id: str
    description: str
    frequency: int
    examples: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "pattern_id": self.pattern_id,
            "description": self.description,
            "frequency": self.frequency,
            "examples": self.examples
        }


@dataclass
class EvaluatorStats:
    """Statistics for a specific evaluator."""
    average_score: float
    min_score: float
    max_score: float
    total_evaluations: int
    successful_evaluations: int
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "average_score": self.average_score,
            "min_score": self.min_score,
            "max_score": self.max_score,
            "total_evaluations": self.total_evaluations,
            "successful_evaluations": self.successful_evaluations
        }


@dataclass
class StatisticalSummary:
    """Statistical summary of evaluation results."""
    success_rate: float
    average_score: float
    score_std_dev: float
    evaluator_stats: Dict[str, EvaluatorStats] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "success_rate": self.success_rate,
            "average_score": self.average_score,
            "score_std_dev": self.score_std_dev,
            "evaluator_stats": {k: v.to_dict() for k, v in self.evaluator_stats.items()}
        }


@dataclass
class DefectExample:
    """Example of a defect found in evaluations."""
    evaluation_run_id: str
    context: str
    defect_text: str
    rationale: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "evaluation_run_id": self.evaluation_run_id,
            "context": self.context,
            "defect_text": self.defect_text,
            "rationale": self.rationale
        }


@dataclass
class DefectCategory:
    """A category of defects found in evaluations."""
    category_type: DefectCategoryType
    frequency: int
    examples: List[DefectExample]
    description: str
    severity: str
    recommendations: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "category_type": self.category_type.value,
            "frequency": self.frequency,
            "examples": [example.to_dict() for example in self.examples],
            "description": self.description,
            "severity": self.severity,
            "recommendations": self.recommendations
        }


@dataclass
class DefectTrend:
    """Trend data for a defect category."""
    category_type: DefectCategoryType
    direction: TrendDirection
    strength: float
    # Note: data_points would be a list of DataPoint objects, but we'll simplify for now
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "category_type": self.category_type.value,
            "direction": self.direction.value,
            "strength": self.strength
        }


@dataclass
class DefectFrequencyAnalysis:
    """Analysis of defect frequency across categories."""
    total_defects_found: int
    defects_by_category: Dict[str, int]
    defects_by_severity: Dict[str, int]
    most_common_defect_category: DefectCategoryType
    defect_trends: List[DefectTrend] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "total_defects_found": self.total_defects_found,
            "defects_by_category": self.defects_by_category,
            "defects_by_severity": self.defects_by_severity,
            "most_common_defect_category": self.most_common_defect_category.value,
            "defect_trends": [trend.to_dict() for trend in self.defect_trends]
        }


@dataclass
class AnalysisData:
    """Complete analysis data from an analysis session."""
    evaluation_runs_analyzed: int
    failure_patterns: List[FailurePattern]
    statistical_summary: StatisticalSummary
    optimization_opportunities: List[OptimizationOpportunity]
    defect_categories: List[DefectCategory]
    defect_frequency_analysis: DefectFrequencyAnalysis
    natural_language_report: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "evaluation_runs_analyzed": self.evaluation_runs_analyzed,
            "failure_patterns": [pattern.to_dict() for pattern in self.failure_patterns],
            "statistical_summary": self.statistical_summary.to_dict(),
            "optimization_opportunities": [opp.to_dict() for opp in self.optimization_opportunities],
            "defect_categories": [cat.to_dict() for cat in self.defect_categories],
            "defect_frequency_analysis": self.defect_frequency_analysis.to_dict(),
            "natural_language_report": self.natural_language_report
        }


@dataclass
class AnalysisSession:
    """An analysis session containing analysis results."""
    id: str
    project_id: str
    agent_version_id: str
    analysis_period_start: Optional[datetime]
    analysis_period_end: Optional[datetime]
    analysis_data: AnalysisData
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    status: AnalysisStatus
    error_message: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "project_id": self.project_id,
            "agent_version_id": self.agent_version_id,
            "analysis_period_start": self.analysis_period_start.isoformat() if self.analysis_period_start else None,
            "analysis_period_end": self.analysis_period_end.isoformat() if self.analysis_period_end else None,
            "analysis_data": self.analysis_data.to_dict(),
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "status": self.status.value,
            "error_message": self.error_message
        }
    
    def to_json(self, indent: int = 2) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)
    
    def __repr__(self) -> str:
        return f"AnalysisSession(id='{self.id}', status={self.status.value}, runs_analyzed={self.analysis_data.evaluation_runs_analyzed})"
    
    def __str__(self) -> str:
        """Provide a nice string representation for printing."""
        lines = [
            f"📊 Analysis Session: {self.id}",
            f"🔍 Status: {self.status.value}",
            f"🤖 Agent Version: {self.agent_version_id}",
            f"📈 Runs Analyzed: {self.analysis_data.evaluation_runs_analyzed}",
        ]
        
        if self.analysis_period_start and self.analysis_period_end:
            lines.append(f"📅 Period: {self.analysis_period_start.strftime('%Y-%m-%d')} to {self.analysis_period_end.strftime('%Y-%m-%d')}")
        
        if self.status == AnalysisStatus.COMPLETED:
            stats = self.analysis_data.statistical_summary
            lines.append(f"✅ Success Rate: {stats.success_rate:.1%}")
            lines.append(f"📊 Average Score: {stats.average_score:.3f} (±{stats.score_std_dev:.3f})")
            
            if self.analysis_data.optimization_opportunities:
                lines.append(f"\n🎯 Optimization Opportunities ({len(self.analysis_data.optimization_opportunities)}):")
                for opp in self.analysis_data.optimization_opportunities[:3]:  # Show top 3
                    emoji = "🔴" if opp.priority == Priority.HIGH else "🟡" if opp.priority == Priority.MEDIUM else "🟢"
                    lines.append(f"  {emoji} {opp.description}")
            
            if self.analysis_data.failure_patterns:
                lines.append(f"\n⚠️ Failure Patterns ({len(self.analysis_data.failure_patterns)}):")
                for pattern in self.analysis_data.failure_patterns[:3]:  # Show top 3
                    lines.append(f"  • {pattern.description} (frequency: {pattern.frequency})")
            
            if self.analysis_data.natural_language_report:
                preview = self.analysis_data.natural_language_report[:200] + "..." if len(self.analysis_data.natural_language_report) > 200 else self.analysis_data.natural_language_report
                lines.append(f"\n📝 Report Preview:\n{preview}")
        
        elif self.status == AnalysisStatus.FAILED and self.error_message:
            lines.append(f"❌ Error: {self.error_message}")
        
        if self.created_at:
            lines.append(f"\n🕒 Created: {self.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
        
        return "\n".join(lines)


@dataclass
class ListAnalysisSessionsResponse:
    """Response containing a list of analysis sessions."""
    sessions: List[AnalysisSession]
    next_page_token: str = ""
    previous_page_token: str = ""
    total_size: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "sessions": [session.to_dict() for session in self.sessions],
            "next_page_token": self.next_page_token,
            "previous_page_token": self.previous_page_token,
            "total_size": self.total_size
        }
    
    def to_json(self, indent: int = 2) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)

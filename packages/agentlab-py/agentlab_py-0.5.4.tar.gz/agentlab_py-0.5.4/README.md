# AgentLab Python Client

[![PyPI version](https://badge.fury.io/py/agentlab-py.svg)](https://badge.fury.io/py/agentlab-py)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A Python client library for the AgentLab evaluation platform using Connect RPC. This library provides a simple and intuitive interface for running AI agent evaluations, managing evaluators, and accessing evaluation results.

## 🚀 Quick Start

```bash
pip install agentlab-py
```

Set your API token as an environment variable:
```bash
export AGENTLAB_API_TOKEN=your-api-token-here
```

```python
from agentlab import AgentLabClient, CreateEvaluationOptions

client = AgentLabClient()

evaluation = client.run_evaluation(CreateEvaluationOptions(
    agent_name='my-agent',
    agent_version='1.0.0',
    evaluator_names=['correctness-v1'],
    user_question='What is the capital of France?',
    agent_answer='The capital of France is Paris.',
    ground_truth='Paris is the capital of France',
    metadata={'confidence': 0.95}
))

print(f"Evaluation completed: {evaluation.name}")
```

### Retrieving Results

```python
evaluation_run = client.get_evaluation_run('evaluation-run-id')

result_data = client.get_evaluation_result('evaluation-run-id')
print(result_data['results'])  # Parsed evaluator outputs

for evaluator_name, result in evaluation_run.evaluator_results.items():
    print(f"{evaluator_name}: {result.output}")
```

### Listing Evaluation Runs

```python
runs_response = client.list_evaluation_runs('project-123')
for run in runs_response.evaluation_runs:
    print(f"Run: {run.name} - Question: {run.user_question}")
```

### Managing Agent Prompts

```python
from agentlab import CreateAgentVersionOptions

# Publish agent version with prompts (idempotent)
result = client.publish_agent_version(CreateAgentVersionOptions(
    agent_name='my-assistant',
    version='1.0.0',
    prompts={
        'system': 'You are a helpful AI assistant...',
        'guidelines': 'Always be polite and professional.'
    }
))

print(f"Published version: {result.create_time}")
for name, content in result.prompts.items():
    print(f"  {name}: {content[:50]}...")
```

### Analyzing Agent Performance

```python
from agentlab import AnalysisParameters

# Create analysis for the last 30 days
params = AnalysisParameters(min_evaluation_runs=5, time_range_days=30)
session = client.analyze_agent('my-agent', '1.0.0', params)

# Get results
session = client.get_analysis_session(session.id)
if session.status.value == "ANALYSIS_STATUS_COMPLETED":
    stats = session.analysis_data.statistical_summary
    print(f"Success rate: {stats.success_rate:.1%}")
    print(f"Average score: {stats.average_score:.3f}")
```

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Issues and Feature Requests

- 🐛 [Report a bug](https://github.com/VectorLabsCZ/agentlab-py/issues/new?template=bug_report.md)
- 💡 [Request a feature](https://github.com/VectorLabsCZ/agentlab-py/issues/new?template=feature_request.md)

## 🔗 Links

- [AgentLab Platform](https://agentlab.vectorlabs.cz)
- [JavaScript SDK](https://github.com/VectorLabsCZ/agentlab-js)

## 🏢 About VectorLabs

AgentLab is developed by [VectorLabs](https://vectorlabs.cz), a company focused on advancing AI agent evaluation and development tools.

---

Made with ❤️ by the VectorLabs team


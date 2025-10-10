#!/usr/bin/env python3
"""
Example usage of the AgentLab SDK in Python.

This example demonstrates how to:
- Initialize the AgentLab client with environment variable authentication
- Run evaluations with multiple evaluators
- Access and display evaluation results
- Handle errors gracefully

Setup:
1. Set your API token as an environment variable:
   export AGENTLAB_API_TOKEN=your-api-token-here
   
2. Or pass it directly to AgentLabClientOptions (api_token parameter takes precedence):
   AgentLabClientOptions(api_token='your-token-here')
"""

import asyncio
import json
import sys
import os

# Add the parent directory to the path to import agentlab
project_root = os.path.join(os.path.dirname(__file__), '..')
sys.path.insert(0, project_root)
# Also add the project root so 'proto.agentlab' imports work
sys.path.insert(0, project_root)

from agentlab import AgentLabClient, AgentLabClientOptions, CreateEvaluationOptions, EvaluationRun

def run_sync_example():
    """Run the example synchronously."""
    
    client = AgentLabClient()

    try:
        print('🚀 Starting AgentLab evaluation example...\n')
        
        evaluation_options = CreateEvaluationOptions(
            agent_name='test-agent',
            agent_version='1.0.0',
            evaluator_names=['correctness-v1'],
            user_question='What is the capital of France?',
            agent_answer='The capital of France is Paris.',
            ground_truth='Paris is the capital of France',
            instructions='Provide factual and accurate information',
            metadata={
                'confidence': 0.95,
                'difficulty': 1,
                'verified': True
            }
        )
        
        print('📝 Running evaluation with the following parameters:')
        print(f'  - Agent: {evaluation_options.agent_name} v{evaluation_options.agent_version}')
        print(f'  - Evaluators: {", ".join(evaluation_options.evaluator_names)}')
        print(f'  - Question: {evaluation_options.user_question}')
        print(f'  - Answer: {evaluation_options.agent_answer}')
        print()
        
        evaluation = client.run_evaluation(evaluation_options)

        print('✅ Evaluation completed!')
        print(f'📊 Result type: {type(evaluation).__name__}')
        print(f'📊 Is pythonic model: {isinstance(evaluation, EvaluationRun)}')
        
        print('\n📊 Individual Results:')
        
        # Access evaluator results - clean pythonic access
        if not evaluation.evaluator_results:
            print('⚠️  No evaluator results found')
            return True
            
        for evaluator_name, result in evaluation.evaluator_results.items():
            print(f'\n🔍 {evaluator_name}:')
            print(f'  - State: {result.state.value}')
            print(f'  - Score: {result.score:.3f}')
            
            # Parsed output is automatically available
            parsed_output = result.parsed_output
            if 'rationale' in parsed_output:
                print(f'  - Rationale: {parsed_output["rationale"]}')
            if 'explanation' in parsed_output:
                print(f'  - Explanation: {parsed_output["explanation"]}')

        # Show JSON serialization
        print('\n📄 JSON Serialization')
        json_output = evaluation.to_json(indent=2)
        print(json_output)
        
        print('\n Dict Serialization:')
        print(evaluation.to_dict())

        print('\nDict evalresult')
        print(evaluation.to_dict()['evaluator_results']['correctness-v1']['score'])
        print(evaluation.to_dict()['evaluator_results']['correctness-v1']['output']['rationale'])

            
    except Exception as error:
        print(f'❌ Error: {error}')
        import traceback
        print('\n🔍 Full traceback:')
        traceback.print_exc()
        return False
    
    return True


# Additional helper functions for demonstration
def list_evaluators_example():
    """Example of listing available evaluators."""
    print('\n🔍 Listing available evaluators...')
    
    client = AgentLabClient()
    
    try:
        response = client.list_evaluators()
        evaluators = getattr(response, 'evaluators', [])
        
        if evaluators:
            print(f'Found {len(evaluators)} evaluators:')
            for evaluator in evaluators:
                name = getattr(evaluator, 'name', 'Unknown')
                display_name = getattr(evaluator, 'display_name', 'No display name')
                description = getattr(evaluator, 'description', 'No description')
                print(f'  - {name}: {display_name}')
                if description:
                    print(f'    {description}')
        else:
            print('No evaluators found')
            
    except Exception as error:
        print(f'❌ Error listing evaluators: {error}')


def list_evaluation_runs_example():
    """Example of listing evaluation runs."""
    print('\n📋 Listing recent evaluation runs...')
    
    client = AgentLabClient()
    
    try:
        response = client.list_evaluation_runs()
        evaluation_runs = getattr(response, 'evaluation_runs', [])
        
        if evaluation_runs:
            print(f'Found {len(evaluation_runs)} evaluation runs:')
            for run in evaluation_runs[:5]:  # Show first 5
                name = getattr(run, 'name', 'Unknown')
                question = getattr(run, 'user_question', 'No question')
                print(f'  - {name}')
                print(f'    Question: {question[:60]}{"..." if len(question) > 60 else ""}')
        else:
            print('No evaluation runs found')
            
    except Exception as error:
        print(f'❌ Error listing evaluation runs: {error}')


# Run the example if this file is executed directly
if __name__ == '__main__':
    print('🐍 AgentLab Python Client - Basic Usage Example')
    print('=' * 50)
    
    # Run the main example
    success = run_sync_example()
    
    if success:
        print('\n' + '=' * 50)
        print('✨ Example completed successfully!')
        
        # Run additional examples
        list_evaluators_example()
        list_evaluation_runs_example()
        
        print('\n📚 Next steps:')
        print('  - Set your API token: export AGENTLAB_API_TOKEN=your-token-here')
        print('  - The project ID is now auto-detected from your auth context')
        print('  - Explore other methods like get_evaluator() and get_evaluation_run()')
        print('  - Check out the async examples for concurrent operations')
        print('  - Try the pythonic_usage.py example to see the new pythonic models!')
        print('  - Use pythonic models (default) for better developer experience')
    else:
        print('\n💡 Tips for troubleshooting:')
        print('  - Set your API token: export AGENTLAB_API_TOKEN=your-token-here')
        print('  - Verify your API token is correct and has proper permissions')
        print('  - Ensure you have access to at least one project')
        print('  - Check that the evaluator names are valid')
        print('  - Verify network connectivity to the AgentLab API')
        
        sys.exit(1)

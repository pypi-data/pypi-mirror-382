#!/usr/bin/env python3
"""
Async example usage of the AgentLab SDK in Python.

This example demonstrates how to use the async version of the client
for better performance when making multiple concurrent requests.

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
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from agentlab import AgentLabClient, AgentLabClientOptions, CreateEvaluationOptions


async def run_async_example():
    """Run an async evaluation example with concurrent operations."""
    
    print('🐍 AgentLab Python Client - Async Usage Example')
    print('=' * 50)
    
    client = AgentLabClient()

    try:
        print('🚀 Running multiple evaluations concurrently...\n')
        
        # Define multiple evaluation scenarios
        evaluation_scenarios = [
            {
                'name': 'Geography Question',
                'options': CreateEvaluationOptions(
                    agent_name='geography-agent',
                    agent_version='1.0.0',
                    evaluator_names=['correctness-v1'],
                    user_question='What is the capital of France?',
                    agent_answer='The capital of France is Paris.',
                    ground_truth='Paris is the capital of France',
                    instructions='Provide factual geographical information',
                    metadata={'confidence': 0.95, 'difficulty': 1}
                )
            },
            {
                'name': 'Math Question',
                'options': CreateEvaluationOptions(
                    agent_name='math-agent',
                    agent_version='1.2.0',
                    evaluator_names=['correctness-v1'],
                    user_question='What is 2 + 2?',
                    agent_answer='2 + 2 equals 4.',
                    ground_truth='4',
                    instructions='Provide accurate mathematical calculations',
                    metadata={'confidence': 1.0, 'difficulty': 1}
                )
            },
            {
                'name': 'Science Question',
                'options': CreateEvaluationOptions(
                    agent_name='science-agent',
                    agent_version='0.9.0',
                    evaluator_names=['correctness-v1'],
                    user_question='What is the speed of light?',
                    agent_answer='The speed of light in vacuum is approximately 299,792,458 meters per second.',
                    ground_truth='299,792,458 m/s',
                    instructions='Provide accurate scientific information',
                    metadata={'confidence': 0.9, 'difficulty': 3}
                )
            }
        ]
        
        # In a real async implementation, you would run these concurrently
        # For now, we'll simulate async behavior by running them sequentially
        # but showing how the code would be structured
        
        results = []
        
        for scenario in evaluation_scenarios:
            print(f'📝 Running evaluation: {scenario["name"]}')
            
            # Simulate async delay
            await asyncio.sleep(0.1)
            
            try:
                evaluation = client.run_evaluation(scenario['options'])
                results.append({
                    'scenario': scenario['name'],
                    'evaluation': evaluation,
                    'success': True
                })
                print(f'  ✅ {scenario["name"]} completed')
                
            except Exception as e:
                results.append({
                    'scenario': scenario['name'],
                    'error': str(e),
                    'success': False
                })
                print(f'  ❌ {scenario["name"]} failed: {e}')
        
        # Display results
        print('\n📊 All Evaluations Completed!')
        print('=' * 50)
        
        successful_results = [r for r in results if r['success']]
        failed_results = [r for r in results if not r['success']]
        
        print(f'✅ Successful: {len(successful_results)}')
        print(f'❌ Failed: {len(failed_results)}')
        
        # Show detailed results for successful evaluations
        for result in successful_results:
            print(f'\n🔍 {result["scenario"]} Results:')
            evaluation = result['evaluation']
            
            evaluator_results = getattr(evaluation, 'evaluator_results', {})
            if evaluator_results:
                for evaluator_name, eval_result in evaluator_results.items():
                    print(f'  {evaluator_name}:')
                    print(f'    - State: {getattr(eval_result, "state", "N/A")}')
                    print(f'    - Score: {getattr(eval_result, "score", "N/A")}')
            else:
                print('  No evaluator results available')
        
        # Show errors for failed evaluations
        if failed_results:
            print('\n❌ Failed Evaluations:')
            for result in failed_results:
                print(f'  {result["scenario"]}: {result["error"]}')
        
        return True
        
    except Exception as error:
        print(f'❌ Async example error: {error}')
        import traceback
        traceback.print_exc()
        return False


async def concurrent_operations_example():
    """Example showing how to perform concurrent operations."""
    
    print('\n🔄 Concurrent Operations Example')
    print('-' * 30)
    
    client = AgentLabClient()
    
    # Simulate concurrent operations (in real async implementation)
    async def fetch_evaluators():
        """Simulate fetching evaluators."""
        await asyncio.sleep(0.2)  # Simulate network delay
        try:
            return client.list_evaluators()
        except Exception as e:
            print(f'Error fetching evaluators: {e}')
            return None
    
    async def fetch_evaluation_runs():
        """Simulate fetching evaluation runs."""
        await asyncio.sleep(0.3)  # Simulate network delay
        try:
            return client.list_evaluation_runs()
        except Exception as e:
            print(f'Error fetching evaluation runs: {e}')
            return None
    
    # Run operations concurrently
    print('🔄 Fetching data concurrently...')
    start_time = asyncio.get_event_loop().time()
    
    evaluators_task = asyncio.create_task(fetch_evaluators())
    evaluation_runs_task = asyncio.create_task(fetch_evaluation_runs())
    
    evaluators_response, evaluation_runs_response = await asyncio.gather(
        evaluators_task, 
        evaluation_runs_task,
        return_exceptions=True
    )
    
    end_time = asyncio.get_event_loop().time()
    
    print(f'⏱️  Total time: {end_time - start_time:.2f} seconds')
    
    # Process results
    if evaluators_response and not isinstance(evaluators_response, Exception):
        evaluators = getattr(evaluators_response, 'evaluators', [])
        print(f'📋 Found {len(evaluators)} evaluators')
    else:
        print('❌ Could not fetch evaluators')
    
    if evaluation_runs_response and not isinstance(evaluation_runs_response, Exception):
        runs = getattr(evaluation_runs_response, 'evaluation_runs', [])
        print(f'📈 Found {len(runs)} evaluation runs')
    else:
        print('❌ Could not fetch evaluation runs')


# Run the async example if this file is executed directly
if __name__ == '__main__':
    async def main():
        """Main async function."""
        success = await run_async_example()
        
        if success:
            await concurrent_operations_example()
            
            print('\n✨ Async example completed!')
            print('\n📚 Async Benefits:')
            print('  - Better performance for multiple concurrent requests')
            print('  - Non-blocking I/O operations')
            print('  - Improved scalability for high-throughput applications')
            print('\n💡 Next Steps:')
            print('  - Set your API token: export AGENTLAB_API_TOKEN=your-token-here')
            print('  - Implement proper async client with aiohttp')
            print('  - Use asyncio.gather() for true concurrent operations')
            print('  - Add proper error handling and retry logic')
        else:
            print('\n❌ Async example failed')
            sys.exit(1)
    
    # Run the async main function
    asyncio.run(main())

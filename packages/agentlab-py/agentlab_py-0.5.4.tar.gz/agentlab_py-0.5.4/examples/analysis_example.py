#!/usr/bin/env python3
"""Simple example showing AgentLab analysis functionality."""

import os
import sys

# Add the parent directory to the path so we can import agentlab
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from agentlab import AgentLabClient, AnalysisParameters


def main():
    """Demonstrate analysis functionality."""
    client = AgentLabClient()
    
    agent_name = "architect"
    agent_version = "1.0.0"
    
    try:
        # Create analysis for last 30 days
        print(f"Creating analysis for {agent_name} v{agent_version}...")
        params = AnalysisParameters(min_evaluation_runs=5, time_range_days=30)
        session = client.analyze_agent(agent_name, agent_version, params)
        
        print(f"Created: {session.id} ({session.status.value})")
        
        # Get analysis results
        session = client.get_analysis_session(session.id)
        
        if session.status.value == "ANALYSIS_STATUS_COMPLETED":
            data = session.analysis_data
            stats = data.statistical_summary
            
            print(f"Analyzed {data.evaluation_runs_analyzed} runs")
            print(f"Success rate: {stats.success_rate:.1%}")
            print(f"Average score: {stats.average_score:.3f}")
            
            if data.optimization_opportunities:
                print(f"\nOptimization opportunities:")
                for opp in data.optimization_opportunities[:2]:
                    print(f"- {opp.description}")
            
            if data.failure_patterns:
                print(f"\nFailure patterns:")
                for pattern in data.failure_patterns[:2]:
                    print(f"- {pattern.description} ({pattern.frequency}x)")
        
        else:
            print(f"Status: {session.status.value}")
    
    except Exception as e:
        print(f"Error: {e}")
        return 1
    
    print("Done!")
    return 0


if __name__ == "__main__":
    sys.exit(main())

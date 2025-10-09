#!/usr/bin/env python3
"""Simple example showing AgentLab prompt management with publish_agent_version.

This example demonstrates the idempotent publish_agent_version method which:
- Creates the agent and version if they don't exist
- Is truly idempotent - can be safely called multiple times with the same values
- Prevents changing existing prompt values (ensuring consistency across runs)
- Is ideal for CI/CD pipelines where you want to ensure prompts exist without errors
"""

import sys
import os
from datetime import datetime

# Add the parent directory to the path to import agentlab
project_root = os.path.join(os.path.dirname(__file__), '..')
sys.path.insert(0, project_root)

from agentlab import AgentLabClient, CreateAgentVersionOptions

AGENT_NAME = "example-assistant"
# Use a date-based version for this demo
PROMPT_VERSION = f"1.4.2"
PROMPTS = {
    "system": """You are an advanced AI assistant specialized in providing detailed, accurate, and helpful responses. 
Always be polite, professional, and aim to understand the user's context before responding. 
When uncertain, ask clarifying questions. Remember to be concise yet thorough in your explanations.""",
    "version": "1.4.2"
}

def main():
    """Demonstrate prompt management using publish_agent_version (idempotent)."""
    try:
        client = AgentLabClient()
        
        print(f"Publishing prompts for agent '{AGENT_NAME}' version '{PROMPT_VERSION}'...")
        print(f"Prompts to publish: {list(PROMPTS.keys())}\n")
        
        # Publish agent version (idempotent - creates if doesn't exist, validates if exists)
        options = CreateAgentVersionOptions(
            agent_name=AGENT_NAME,
            version=PROMPT_VERSION,
            prompts=PROMPTS
        )
        
        try:
            result = client.publish_agent_version(options)
            print("✓ Successfully published agent version")
            print(f"  Created: {result.create_time}")
            print(f"  Updated: {result.update_time}")
        except Exception as e:
            if "cannot be changed" in str(e):
                print("⚠️  Version already exists with different prompt values")
                print("   publish_agent_version is idempotent - it preserves existing values")
                print("\nRetrieving existing version instead...")
                result = client.get_agent_version(AGENT_NAME, PROMPT_VERSION)
            else:
                raise e
        
        # Display current prompts
        print(f"\nCurrent prompts in version '{PROMPT_VERSION}':")
        for name, content in sorted(result.prompts.items()):
            # Truncate long prompts for display
            display_content = content if len(content) <= 60 else content[:57] + "..."
            print(f"  • {name}: {display_content}")
        
        # Demonstrate idempotency - call again with same values
        print("\n" + "="*60)
        print("Demonstrating idempotency - calling publish again...")
        print("="*60)
        
        result2 = client.publish_agent_version(options)
        print("✓ Second call succeeded (idempotent behavior)")
        print(f"  Prompts unchanged: {sorted(result2.prompts.keys()) == sorted(result.prompts.keys())}")
        
        print("\n✓ Done! The publish_agent_version method can be safely called")
        print("  multiple times in CI/CD pipelines without errors.")
        return 0
    
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
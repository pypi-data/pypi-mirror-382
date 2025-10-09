#!/usr/bin/env python3
"""
ADK Book Agent - AgentLab Evaluation Script with Prompt Management

This script demonstrates how to:
1. Manage agent prompts with versioning using AgentLab
2. Automatically upload new prompts if they don't exist  
3. Run evaluations using the managed prompts
4. Allow easy prompt updates and version management

Setup:
Set your API token as an environment variable:
export AGENTLAB_API_TOKEN=your-api-token-here
"""

import sys
import os
from datetime import datetime

# Add the parent directory to the path to import agentlab
project_root = os.path.join(os.path.dirname(__file__), '..', '..')
sys.path.insert(0, project_root)

from agentlab import AgentLabClient, AgentLabClientOptions, CreateEvaluationOptions, CreateAgentVersionOptions


# =============================================================================
# AGENT CONFIGURATION - Update these to manage prompts and versions
# =============================================================================

AGENT_NAME = "adk_book_agent"
AGENT_VERSION = "v1.0.0"  # Increment this when you want to create a new prompt version

# Agent prompts - these will be uploaded to AgentLab for version management
AGENT_PROMPTS = {
    "system": """You are a knowledgeable and enthusiastic book librarian with access to a curated collection of classic literature. You can search for books and provide detailed information about them.

When users ask about books, you should:
1. Use search_books to find books by title, author, genre, or keywords
2. Use get_book_details to retrieve comprehensive information including funny stories, quotes, trivia, and lore
3. Be engaging, witty, and passionate about literature
4. Share the rich information from your database including funny stories and cultural context
5. Always cite specific details from your database when sharing information

You have access to two main tools:
- search_books: Find books matching a query
- get_book_details: Get complete information about a specific book including funny stories, lore, quotes, and trivia

Make your responses informative and entertaining using the rich data available in your book database.""",

    "greeting": "📚 Welcome! I'm your literary companion with access to a curated collection of classic books. Ask me about books, authors, funny stories, quotes, or recommendations!",
    
    "error_response": "❌ I encountered an error while searching my book database. Please try rephrasing your request or ask about a different book.",
    
    "no_results": "📖 I couldn't find any books matching your search in my curated collection. Try searching by title, author, or genre, or ask me for recommendations!",
    
    "tool_usage_guide": """I can help you with:
• Book searches by title, author, or genre
• Detailed book information with stories and trivia  
• Author background and funny anecdotes
• Book recommendations based on your interests
• Quotes and cultural context from classic literature"""
}

# Prompt metadata for versioning
PROMPT_METADATA = {
    "author": "AgentLab Team",
    "purpose": "ADK Book Agent system prompts for literary assistance",
    "version_notes": "v1.0.0: Initial version with comprehensive book search and detail prompts",
    "tools": ["search_books", "get_book_details"],
    "domain": "literature",
    "created_at": datetime.now().isoformat()
}

# =============================================================================
# EVALUATION TEST CASES  
# =============================================================================

# Realistic agent responses that simulate actual book agent behavior
REALISTIC_RESPONSES = {
    "hitchhiker_search": """📚 The Hitchhiker's Guide to the Galaxy is a comedic science fiction novel by Douglas Adams, published in 1979. It follows Arthur Dent's adventures through space after Earth is destroyed to make way for a hyperspace bypass.

The book is famous for introducing the number 42 as 'the answer to the ultimate question of life, the universe, and everything.' Here's a funny story: Douglas Adams wrote much of it in a hotel room in Innsbruck, Austria, after his editor literally locked him in until he finished it due to missed deadlines!

Rating: 4.8/5, 224 pages. It's become a cultural phenomenon with phrases like 'Don't panic!' entering popular culture.""",

    "austen_search": """📖 I have one book by Jane Austen in my collection: **Pride and Prejudice** (1813). It's a witty exploration of love, class, and social expectations in Regency England, with a rating of 4.7/5.

Fun fact: Austen originally titled it 'First Impressions' and it was rejected by publisher Thomas Cadell without even being read! He returned it immediately with 'declined by return of post.' Years later, publishers were begging for her work.""",

    "orwell_detailed": """📚 **1984** by George Orwell is a dystopian novel published in 1949 about totalitarian control and surveillance. It features Big Brother, Room 101, telescreens, and Newspeak.

Interesting backstory: Room 101 was named after a real BBC meeting room where Orwell had boring meetings! The telescreen concept was inspired by early BBC television. Originally, Orwell wanted to call it '1980' but his publisher thought that was too close to publication date, so he reversed '1948' to get '1984.'

Rating: 4.6/5, 328 pages."""
}


def ensure_agent_prompts_uploaded(client):
    """Ensure agent prompts are uploaded to AgentLab. Create if they don't exist."""
    print("🔍 Checking agent prompts in AgentLab...")
    
    try:
        # Try to get existing prompt version
        existing_prompts = client.get_agent_version(AGENT_NAME, AGENT_VERSION)
        print(f"✅ Found existing prompts for {AGENT_NAME} {AGENT_VERSION}")
        print(f"   Content hash: {existing_prompts.content_hash}")
        print(f"   Created: {existing_prompts.create_time.strftime('%Y-%m-%d %H:%M:%S') if existing_prompts.create_time else 'Unknown'}")
        return existing_prompts
        
    except Exception as error:
        # Check if it's a 404 (Not Found) error
        if "404" in str(error) or "not found" in str(error).lower():
            print(f"❌ Prompts not found for {AGENT_NAME} {AGENT_VERSION}. Creating new version...")
            
            # Create new prompt version
            options = CreateAgentVersionOptions(
                agent_name=AGENT_NAME,
                version=AGENT_VERSION,
                prompts=AGENT_PROMPTS,
                metadata=PROMPT_METADATA,
                description=f"ADK Book Agent prompts version {AGENT_VERSION} - Literary assistance with book search and detailed information capabilities"
            )
            
            created_prompts = client.create_agent_version(options)
            print(f"✅ Successfully created prompts!")
            print(f"   Resource name: {created_prompts.name}")
            print(f"   Content hash: {created_prompts.content_hash}")
            print(f"   Prompt count: {len(created_prompts.prompts)}")
            
            return created_prompts
        else:
            # Re-raise if it's a different error
            raise error


def show_agent_prompt_info(agent_version):
    """Display information about the current agent prompts."""
    print("\n📋 Current Agent Prompts:")
    print("=" * 50)
    
    if agent_version and agent_version.prompts:
        for prompt_name, prompt_content in agent_version.prompts.items():
            print(f"\n{prompt_name.upper()}:")
            print("-" * 20)
            # Show preview of prompt content
            preview = prompt_content[:200] + "..." if len(prompt_content) > 200 else prompt_content
            print(preview)
    
    if agent_version and agent_version.metadata:
        print(f"\n🏷️  Metadata:")
        print("-" * 20)
        for key, value in agent_version.metadata.items():
            print(f"{key}: {value}")


def run_evaluations():
    """Run AgentLab evaluations with prompt management integration."""
    
    print("📚 ADK Book Agent - AgentLab Evaluation with Prompt Management")
    print("=" * 65)
    print(f"Agent: {AGENT_NAME} | Version: {AGENT_VERSION}")
    print()
    
    # Initialize AgentLab client (API token loaded from AGENTLAB_API_TOKEN environment variable)
    client = AgentLabClient(AgentLabClientOptions())
    
    # Step 1: Ensure agent prompts are uploaded to AgentLab
    agent_version = ensure_agent_prompts_uploaded(client)
    
    # Step 2: Show current prompt information
    show_agent_prompt_info(agent_version)
    
    print("\n" + "=" * 50)
    print("🔄 STARTING EVALUATIONS")
    print("=" * 50)
    
    # Define test scenarios with realistic responses
    scenarios = [
        {
            "name": "Hitchhiker's Guide Search",
            "user_question": "Tell me about The Hitchhiker's Guide to the Galaxy",
            "agent_answer": REALISTIC_RESPONSES["hitchhiker_search"],
            "ground_truth": "The Hitchhiker's Guide to the Galaxy is a comedic science fiction novel by Douglas Adams published in 1979. It follows Arthur Dent's adventures through space and is famous for the number 42. Douglas Adams wrote much of it in a hotel room after his editor locked him in until he finished it.",
            "category": "book_search"
        },
        {
            "name": "Jane Austen Author Search",
            "user_question": "What books do you have by Jane Austen?",
            "agent_answer": REALISTIC_RESPONSES["austen_search"],
            "ground_truth": "Pride and Prejudice (1813) by Jane Austen. Originally titled 'First Impressions' and rejected without being read.",
            "category": "author_search"
        },
        {
            "name": "1984 Detailed Information",
            "user_question": "Give me detailed information about 1984, including any interesting stories",
            "agent_answer": REALISTIC_RESPONSES["orwell_detailed"],
            "ground_truth": "1984 is a dystopian novel by George Orwell published in 1949. Room 101 was named after a BBC meeting room where Orwell had boring meetings. Originally going to be called '1980'.",
            "category": "detailed_info"
        }
    ]
    
    print(f"🔄 Running {len(scenarios)} evaluation scenarios...")
    print()
    
    results = []
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"📝 {i}. {scenario['name']}")
        print(f"   Question: {scenario['user_question']}")
        print(f"   Response preview: {scenario['agent_answer'][:100]}...")
        
        try:
            # Create evaluation using our managed agent prompts with multiple evaluators
            evaluation = client.run_evaluation(CreateEvaluationOptions(
                agent_name=AGENT_NAME,
                agent_version=AGENT_VERSION,
                evaluator_names=['correctness-v1', 'bleu-v1', 'relevancy-v1'],
                user_question=scenario['user_question'],
                agent_answer=scenario['agent_answer'],
                ground_truth=scenario['ground_truth'],
                instructions=f"Evaluate the agent's {scenario['category']} capability. Check for accuracy, completeness, proper use of search_books and get_book_details tools, language quality, and relevance to the user question.",
                metadata={
                    'category': scenario['category'],
                    'difficulty': 3,
                    'tool_usage': 'search_books,get_book_details',
                    'evaluators': 'correctness,bleu,relevancy'
                }
            ))
            
            print(f"   ✅ Completed: {evaluation.name.split('/')[-1]}")
            
            # Try to get detailed results from all evaluators
            try:
                result_data = client.get_evaluation_result(evaluation.name)
                if 'results' in result_data:
                    evaluator_names = ['correctness-v1', 'bleu-v1', 'relevancy-v1']
                    for evaluator_name in evaluator_names:
                        result = result_data['results'].get(evaluator_name, {})
                        if result:
                            score = result.get('score', 'N/A')
                            evaluator_display = evaluator_name.replace('-v1', '').title()
                            print(f"   🎯 {evaluator_display}: {score}")
                            
                            # Show rationale for correctness and relevancy
                            if evaluator_name in ['correctness-v1', 'relevancy-v1']:
                                rationale = result.get('rationale', '')
                                if rationale:
                                    print(f"   📝 {evaluator_display} Notes: {rationale[:120]}...")
            except Exception as e:
                print(f"   ⏳ Results processing (may take a moment)...")
            
            results.append({'scenario': scenario['name'], 'status': 'success'})
            
        except Exception as e:
            print(f"   ❌ Failed: {e}")
            results.append({'scenario': scenario['name'], 'status': 'failed', 'error': str(e)})
        
        print()
    
    # Summary
    successful = sum(1 for r in results if r['status'] == 'success')
    print(f"📊 Results: {successful}/{len(results)} evaluations successful")
    
    if successful > 0:
        print("\n✨ Evaluation completed successfully!")
        print(f"\n🔧 To update prompts:")
        print(f"  1. Modify AGENT_PROMPTS in this file")
        print(f"  2. Update AGENT_VERSION to '{AGENT_VERSION[:-1]}{int(AGENT_VERSION[-1])+1}'")
        print(f"  3. Run this script again - new prompts will be auto-uploaded")
        
        print("\n💡 Key insights:")
        print("  • Agent prompts are now versioned and managed in AgentLab")  
        print("  • Evaluations use 3 evaluators: Correctness, BLEU, and Relevancy")
        print("  • Correctness: Factual accuracy and completeness")
        print("  • BLEU: Language quality and fluency compared to ground truth")
        print("  • Relevancy: How well the response addresses the user's question")
        print("  • Use multi-metric feedback to iterate and improve prompts & responses")
    
    # Show version management info
    try:
        print(f"\n📚 All versions for agent '{AGENT_NAME}':")
        versions = client.list_agent_versions(AGENT_NAME)
        if versions.agent_versions:
            for i, version in enumerate(versions.agent_versions):
                created = version.create_time.strftime('%Y-%m-%d %H:%M:%S') if version.create_time else 'Unknown'
                print(f"  {i+1}. {version.version} - Created: {created} - Prompts: {len(version.prompts)}")
        else:
            print("  No versions found")
    except Exception as e:
        print(f"  Error listing versions: {e}")
    
    return results


if __name__ == "__main__":
    run_evaluations()

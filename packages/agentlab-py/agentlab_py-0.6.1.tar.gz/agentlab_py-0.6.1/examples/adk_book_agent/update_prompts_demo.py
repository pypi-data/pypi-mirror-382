#!/usr/bin/env python3
"""
ADK Book Agent - Prompt Update Demo

This script demonstrates how to easily update agent prompts to a new version.
Simply modify the prompts below and run this script to create a new version.
"""

import sys
import os
from datetime import datetime

# Add the parent directory to the path to import agentlab
project_root = os.path.join(os.path.dirname(__file__), '..', '..')
sys.path.insert(0, project_root)

from agentlab import AgentLabClient, CreateAgentVersionOptions

# =============================================================================
# UPDATED PROMPTS - Modify these to create a new version
# =============================================================================

AGENT_NAME = "adk_book_agent"
AGENT_VERSION = "v1.1.0"  # NEW VERSION!

# Enhanced prompts with improvements
UPDATED_AGENT_PROMPTS = {
    "system": """You are a knowledgeable and enthusiastic book librarian with access to a curated collection of classic literature. You can search for books and provide detailed information about them.

When users ask about books, you should:
1. Use search_books to find books by title, author, genre, or keywords
2. Use get_book_details to retrieve comprehensive information including funny stories, quotes, trivia, and lore
3. Be engaging, witty, and passionate about literature
4. Share the rich information from your database including funny stories and cultural context
5. Always cite specific details from your database when sharing information
6. 🆕 Ask follow-up questions to provide more personalized recommendations
7. 🆕 Connect books to current events or popular culture when relevant

You have access to two main tools:
- search_books: Find books matching a query
- get_book_details: Get complete information about a specific book including funny stories, lore, quotes, and trivia

Make your responses informative, entertaining, and conversational. Remember, you're not just providing information - you're sharing your love of literature! 📚""",

    "greeting": "📚 Welcome! I'm your enthusiastic literary companion with access to a curated collection of classic books. Ask me about books, authors, funny stories, quotes, or let me recommend something perfect for you! What kind of reading adventure are you in the mood for? ✨",
    
    "error_response": "❌ I encountered an error while searching my book database. Please try rephrasing your request or ask about a different book. Perhaps I can suggest a popular title instead?",
    
    "no_results": "📖 I couldn't find any books matching your search in my curated collection. But don't worry! Try searching by title, author, or genre, or let me recommend something wonderful based on your interests. What genres do you enjoy?",
    
    "tool_usage_guide": """I can help you with:
• Book searches by title, author, or genre
• Detailed book information with stories and trivia  
• Author background and funny anecdotes
• Personalized book recommendations based on your interests
• Quotes and cultural context from classic literature
• Fun book facts and connections to modern culture
• 🆕 Reading suggestions for different moods and occasions""",

    "recommendation_prompt": "Based on what you've told me about your reading preferences, I think you'd really enjoy these books from my collection. Here's why each one might be perfect for you:",

    "cultural_context": "One fascinating thing about this book is how it connects to the world we live in today. Let me share some interesting parallels..."
}

# Updated metadata
UPDATED_METADATA = {
    "author": "AgentLab Team",
    "purpose": "Enhanced ADK Book Agent with personalized recommendations and cultural connections",
    "version_notes": "v1.1.0: Added follow-up questions, cultural connections, personalized recommendations, enhanced conversation flow, added emoji to system prompt",
    "tools": ["search_books", "get_book_details"],
    "domain": "literature",
    "enhancements": ["conversational_flow", "personalization", "cultural_relevance"],
    "created_at": datetime.now().isoformat()
}


def create_updated_prompts():
    """Create the updated prompt version in AgentLab."""
    
    print("📚 ADK Book Agent - Prompt Update Demo")
    print("=" * 45)
    print(f"Creating new prompt version: {AGENT_NAME} {AGENT_VERSION}")
    print()
    
    # Initialize AgentLab client
    client = AgentLabClient()
    
    # Check if this version already exists
    try:
        existing = client.get_agent_version(AGENT_NAME, AGENT_VERSION)
        print(f"⚠️  Version {AGENT_VERSION} already exists!")
        print(f"   Content hash: {existing.content_hash}")
        print(f"   Created: {existing.create_time.strftime('%Y-%m-%d %H:%M:%S') if existing.create_time else 'Unknown'}")
        
        choice = input("\n🤔 Do you want to create a new version instead? (y/N): ").lower()
        if choice == 'y':
            # Increment version automatically
            version_parts = AGENT_VERSION.split('.')
            version_parts[-1] = str(int(version_parts[-1]) + 1)
            new_version = '.'.join(version_parts)
            print(f"📝 Creating version {new_version} instead...")
            global AGENT_VERSION
            AGENT_VERSION = new_version
        else:
            print("✋ Skipping creation. Use different version number if you want to create new prompts.")
            return existing
            
    except Exception as e:
        if "404" in str(e) or "not found" in str(e).lower():
            print(f"✅ Version {AGENT_VERSION} doesn't exist yet. Creating new version...")
        else:
            raise e
    
    # Create new prompt version
    print(f"\n📤 Uploading prompts to AgentLab...")
    
    options = CreateAgentVersionOptions(
        agent_name=AGENT_NAME,
        version=AGENT_VERSION,
        prompts=UPDATED_AGENT_PROMPTS,
        metadata=UPDATED_METADATA,
        description=f"ADK Book Agent enhanced prompts version {AGENT_VERSION} - Improved conversational flow with personalized recommendations and cultural connections"
    )
    
    created_prompts = client.create_agent_version(options)
    
    print(f"🎉 Successfully created prompts version {AGENT_VERSION}!")
    print(f"   Resource name: {created_prompts.name}")
    print(f"   Content hash: {created_prompts.content_hash}")
    print(f"   Prompt count: {len(created_prompts.prompts)}")
    print(f"   Created by: {created_prompts.created_by}")
    
    # Show improvements
    print(f"\n✨ New in version {AGENT_VERSION}:")
    enhancements = UPDATED_METADATA.get("enhancements", [])
    for enhancement in enhancements:
        print(f"   • {enhancement.replace('_', ' ').title()}")
    
    # Show all versions
    try:
        print(f"\n📚 All versions for '{AGENT_NAME}':")
        versions = client.list_agent_versions(AGENT_NAME)
        if versions.agent_versions:
            for i, version in enumerate(versions.agent_versions):
                created = version.create_time.strftime('%Y-%m-%d %H:%M:%S') if version.create_time else 'Unknown'
                indicator = " ← NEW!" if version.version == AGENT_VERSION else ""
                print(f"  {i+1}. {version.version} - Created: {created} - Prompts: {len(version.prompts)}{indicator}")
        
        print(f"\n🔄 To use this version in evaluations:")
        print(f"  1. Edit evaluate_agent.py")
        print(f"  2. Change AGENT_VERSION to '{AGENT_VERSION}'")
        print(f"  3. Run the evaluation script")
        
    except Exception as e:
        print(f"  Error listing versions: {e}")
    
    return created_prompts


if __name__ == "__main__":
    create_updated_prompts()

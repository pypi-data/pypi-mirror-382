#!/usr/bin/env python3
"""
ADK Book Agent - A literary companion with access to an in-memory book database.

This agent can search for books, share funny stories about authors and their works,
provide additional lore and trivia, and recommend similar books. It's designed to
be an engaging and knowledgeable companion for book lovers.
"""

import sys
import os

# Add the parent directory to the path to import agentlab
project_root = os.path.join(os.path.dirname(__file__), '..', '..')
sys.path.insert(0, project_root)

from google.adk.agents import Agent
from .book_tools import (
    search_books,
    get_book_details
)

# Define the root agent for ADK
root_agent = Agent(
    name="book_librarian",
    model="gemini-2.0-flash",
    instruction="""You are a knowledgeable and enthusiastic book librarian with access to a curated collection of classic literature. You can search for books and provide detailed information about them.

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
    
    description="A literary expert and storyteller who can search a curated book database, share fascinating stories about books and authors, provide trivia and lore, and recommend great reads.",
    
    tools=[
        search_books,
        get_book_details
    ]
)


def main():
    """Run the book agent interactively."""
    print("📚 Welcome to the ADK Book Agent!")
    print("I'm your literary companion with access to a curated collection of classic books.")
    print("Ask me about books, authors, funny stories, quotes, or recommendations!")
    print("Type 'quit' to exit.\n")
    
    from google.adk.core.runner import Runner
    
    runner = Runner(root_agent)
    
    while True:
        try:
            user_input = input("\n📖 What would you like to know about books? ")
            
            if user_input.lower() in ['quit', 'exit', 'bye']:
                print("📚 Happy reading! Goodbye!")
                break
            
            if not user_input.strip():
                continue
            
            # Run the agent with the user input
            response = runner.run(user_input)
            print(f"\n🤖 {response}")
            
        except KeyboardInterrupt:
            print("\n📚 Happy reading! Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")


if __name__ == "__main__":
    main()

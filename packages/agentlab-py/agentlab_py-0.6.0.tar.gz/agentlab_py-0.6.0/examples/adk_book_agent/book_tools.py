#!/usr/bin/env python3
"""
Book lookup tools for the ADK Book Agent.

This module provides tool functions that the ADK agent can use to search and
retrieve information from the book database, including funny stories and lore.
"""

from typing import List, Dict, Any, Optional
import json

from .book_database import book_database, Book


def search_books(query: str) -> str:
    """
    Search for books in the database by title, author, genre, or keywords.
    
    Args:
        query: The search term to look for in books
        
    Returns:
        JSON string containing search results with book information
    """
    results = book_database.search_books(query)
    
    if not results:
        return json.dumps({
            "status": "no_results",
            "message": f"No books found matching '{query}'",
            "suggestions": ["Try searching by author name", "Try searching by genre", "Try broader keywords"]
        })
    
    books_info = []
    for book in results:
        books_info.append({
            "id": book.id,
            "title": book.title,
            "author": book.author,
            "genre": book.genre,
            "year_published": book.year_published,
            "rating": book.rating,
            "description": book.description[:200] + "..." if len(book.description) > 200 else book.description
        })
    
    return json.dumps({
        "status": "success",
        "query": query,
        "results_count": len(results),
        "books": books_info
    })


def get_book_details(book_id: str) -> str:
    """
    Get detailed information about a specific book including funny stories and lore.
    
    Args:
        book_id: The ID of the book to retrieve
        
    Returns:
        JSON string containing detailed book information
    """
    book = book_database.get_book_by_id(book_id)
    
    if not book:
        return json.dumps({
            "status": "not_found",
            "message": f"Book with ID '{book_id}' not found",
            "suggestion": "Use search_books to find the correct book ID"
        })
    
    return json.dumps({
        "status": "success",
        "book": {
            "id": book.id,
            "title": book.title,
            "author": book.author,
            "genre": book.genre,
            "year_published": book.year_published,
            "pages": book.pages,
            "rating": book.rating,
            "isbn": book.isbn,
            "description": book.description,
            "funny_story": book.funny_story,
            "additional_lore": book.additional_lore,
            "quotes": book.quotes,
            "trivia": book.trivia
        }
    })



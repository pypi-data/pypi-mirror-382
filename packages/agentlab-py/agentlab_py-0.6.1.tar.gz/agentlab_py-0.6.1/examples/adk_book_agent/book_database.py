#!/usr/bin/env python3
"""
In-memory book database with sample data for the ADK Book Agent.

This module contains a collection of books with detailed information including
funny stories, additional lore, and rich metadata that the agent can use to
provide engaging responses about books.
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime


@dataclass
class Book:
    """Represents a book in our database with rich metadata."""
    id: str
    title: str
    author: str
    genre: str
    year_published: int
    description: str
    funny_story: str
    additional_lore: str
    quotes: List[str]
    trivia: List[str]
    rating: float
    pages: int
    isbn: str


class BookDatabase:
    """An in-memory database containing books with rich information."""
    
    def __init__(self):
        self.books: Dict[str, Book] = {}
        self._initialize_books()
    
    def _initialize_books(self):
        """Initialize the database with sample books."""
        books_data = [
            Book(
                id="1",
                title="The Hitchhiker's Guide to the Galaxy",
                author="Douglas Adams",
                genre="Science Fiction Comedy",
                year_published=1979,
                description="A comedic science fiction series following Arthur Dent's adventures through space.",
                funny_story="Douglas Adams famously wrote much of the book in a hotel room in Innsbruck, Austria, after his editor locked him in until he finished it. He had missed multiple deadlines and his editor literally wouldn't let him leave until the manuscript was complete. Adams later joked that this was the only way he could ever finish anything.",
                additional_lore="The number 42 as 'the answer to the ultimate question of life, the universe, and everything' has become a cultural phenomenon. Adams chose 42 because it was 'a completely ordinary number, a number not just divisible by two but also by six and seven.' The BBC has a radio show that still airs with sound effects Adams created using his own bathtub and rubber duck.",
                quotes=[
                    "Don't panic!",
                    "The answer to the ultimate question of life, the universe, and everything is 42.",
                    "So long, and thanks for all the fish!"
                ],
                trivia=[
                    "Adams wrote the original radio series while working as a security guard",
                    "The towel became a symbol of preparedness thanks to this book",
                    "Google Calculator will give you 42 if you search for 'the answer to life universe and everything'"
                ],
                rating=4.8,
                pages=224,
                isbn="9780345391803"
            ),
            Book(
                id="2",
                title="Pride and Prejudice",
                author="Jane Austen",
                genre="Romance/Classic Literature",
                year_published=1813,
                description="A witty exploration of love, class, and social expectations in Regency England.",
                funny_story="Jane Austen originally titled this novel 'First Impressions' and it was rejected by a publisher without even being read! The publisher Thomas Cadell returned it by return post with a note saying 'declined by return of post.' Austen's father had written offering to pay for publication himself, but Cadell wouldn't even consider it. Years later, after Austen became famous, publishers were begging for her work.",
                additional_lore="Mr. Darcy's famous estate Pemberley was inspired by Chatsworth House in Derbyshire. Austen visited the area and was so impressed by the grandeur that she used it as inspiration. The 2005 film actually used Chatsworth as a filming location, coming full circle. There's also a theory that Mr. Darcy was based on a real person - a politician named Tom Lefroy whom Austen briefly courted.",
                quotes=[
                    "It is a truth universally acknowledged, that a single man in possession of a good fortune, must be in want of a wife.",
                    "I declare after all there is no enjoyment like reading!",
                    "You have bewitched me, body and soul."
                ],
                trivia=[
                    "Austen earned only £110 from the novel during her lifetime",
                    "The BBC 1995 adaptation made Colin Firth's wet shirt scene iconic",
                    "There are over 50 film and TV adaptations of this novel"
                ],
                rating=4.7,
                pages=432,
                isbn="9780141439518"
            ),
            Book(
                id="3",
                title="1984",
                author="George Orwell",
                genre="Dystopian Fiction",
                year_published=1949,
                description="A dystopian social science fiction novel about totalitarian control and surveillance.",
                funny_story="Orwell originally wanted to call the book '1980' but his publisher thought that was too close to the publication date and might confuse readers into thinking it was non-fiction about current events. So Orwell simply reversed the last two digits of 1948 (the year he was writing) to get 1984. Ironically, when 1984 actually arrived, the book sales skyrocketed as people checked if Orwell's predictions came true.",
                additional_lore="Room 101, the torture chamber in the novel, was named after a meeting room at the BBC where Orwell had to sit through boring meetings during his time there. He said it was the worst room in the building. The telescreen concept was inspired by the BBC's early television experiments - Orwell was fascinated and horrified by the idea of a screen that could watch you back.",
                quotes=[
                    "Big Brother is watching you.",
                    "War is peace. Freedom is slavery. Ignorance is strength.",
                    "If you want to keep a secret, you must also hide it from yourself."
                ],
                trivia=[
                    "The book was banned in the USSR until 1988",
                    "Sales spike every time there's a political scandal involving surveillance",
                    "Apple's 1984 Super Bowl commercial was inspired by this book"
                ],
                rating=4.6,
                pages=328,
                isbn="9780451524935"
            ),
            Book(
                id="4",
                title="To Kill a Mockingbird",
                author="Harper Lee",
                genre="Southern Gothic/Coming-of-age",
                year_published=1960,
                description="A story of racial injustice and childhood innocence in the American South.",
                funny_story="Harper Lee was so nervous about the book's reception that she left New York City on publication day and went to hide out with friends in Kansas. She was convinced it would be a complete failure. Meanwhile, the book was selling like hotcakes and winning awards. Her friends had to drag her back to accept the Pulitzer Prize because she was still convinced the whole thing was a mistake.",
                additional_lore="The character of Dill was based on Harper Lee's childhood friend Truman Capote (who later wrote 'In Cold Blood'). They were neighbors in Monroeville, Alabama, and Capote helped inspire Lee to become a writer. In return, Lee helped Capote research 'In Cold Blood.' The town courthouse in the novel was modeled after the actual courthouse in Monroeville, which you can still visit today.",
                quotes=[
                    "You never really understand a person until you consider things from his point of view.",
                    "The one thing that doesn't abide by majority rule is a person's conscience.",
                    "People generally see what they look for, and hear what they listen for."
                ],
                trivia=[
                    "Harper Lee didn't publish another novel for 55 years",
                    "The book was almost titled 'Atticus' instead",
                    "It's taught in over 70% of American high schools"
                ],
                rating=4.5,
                pages=376,
                isbn="9780060935467"
            ),
            Book(
                id="5",
                title="The Great Gatsby",
                author="F. Scott Fitzgerald",
                genre="American Literature/Tragedy",
                year_published=1925,
                description="A critique of the American Dream set in the Jazz Age.",
                funny_story="F. Scott Fitzgerald was so disappointed with the book's initial reception and sales that he considered it a failure. It sold only about 20,000 copies during his lifetime, and he died thinking he was a forgotten writer. The book was so unpopular that when Fitzgerald died in 1940, all copies were out of print. It was only when free copies were distributed to WWII soldiers that it found its audience and became the classic we know today.",
                additional_lore="The green light at the end of Daisy's dock was inspired by a real green light that Fitzgerald could see from his home on Long Island. He and his wife Zelda lived in a house that looked across the bay, and there really was a green light across the water. The eyes of Doctor T.J. Eckleburg were inspired by a real billboard for an optometrist that Fitzgerald saw, though that billboard advertised spectacles, not eyes.",
                quotes=[
                    "So we beat on, boats against the current, borne back ceaselessly into the past.",
                    "I hope she'll be a fool -- that's the best thing a girl can be in this world, a beautiful little fool.",
                    "Gatsby believed in the green light, the orgastic future that year by year recedes before us."
                ],
                trivia=[
                    "The book was considered a failure until after WWII",
                    "There have been 5 major film adaptations",
                    "The original cover design is still copyrighted and costs $1000 to license"
                ],
                rating=4.4,
                pages=256,
                isbn="9780743273565"
            ),
            Book(
                id="6",
                title="Dune",
                author="Frank Herbert",
                genre="Science Fiction",
                year_published=1965,
                description="An epic space opera about politics, religion, and ecology on a desert planet.",
                funny_story="Frank Herbert spent six years researching and writing Dune, and it was rejected by 23 publishers before finally being accepted. One publisher said it was 'too long, too weird, and too complex.' Herbert had to take odd jobs to support his family while writing it, including working as a mushroom farmer. Ironically, his experience growing mushrooms in controlled environments helped him understand the ecological themes that became central to Dune.",
                additional_lore="Herbert was inspired to write Dune after visiting the Oregon coast and seeing efforts to stabilize sand dunes with grasses. He became fascinated with desert ecology and spent years studying how desert peoples survived. The spice melange was inspired by his research into psychoactive substances and their role in religious experiences. The Fremen culture was influenced by Bedouin and other desert societies, and Herbert learned Arabic to better understand their languages and customs.",
                quotes=[
                    "Fear is the mind-killer.",
                    "He who controls the spice controls the universe.",
                    "The beginning is a very delicate time."
                ],
                trivia=[
                    "Herbert created over 200 terms for the Dune universe",
                    "The novel predicted many environmental themes decades early",
                    "It won both the Hugo and Nebula awards"
                ],
                rating=4.6,
                pages=688,
                isbn="9780441172719"
            ),
            Book(
                id="7",
                title="Harry Potter and the Philosopher's Stone",
                author="J.K. Rowling",
                genre="Fantasy/Young Adult",
                year_published=1997,
                description="A young wizard discovers his magical heritage and attends Hogwarts School of Witchcraft and Wizardry.",
                funny_story="J.K. Rowling wrote the first book on napkins and scraps of paper while sitting in cafes in Edinburgh, often with her baby daughter sleeping in a stroller beside her. She couldn't afford a computer and wrote everything by hand. The idea came to her on a delayed train, and she spent the entire 4-hour journey developing the plot in her head. When she finally got home, she immediately started writing on whatever paper she could find.",
                additional_lore="The Hogwarts Express was inspired by the real Jacobite Steam Train in Scotland, which still runs today. Platform 9¾ at King's Cross Station now has a real plaque and shopping area. Rowling also hid many jokes in the names: 'Diagon Alley' sounds like 'diagonally,' 'Knockturn Alley' like 'nocturnally,' and 'Grimmauld Place' like 'grim old place.' The character of Hermione was partly based on Rowling herself as a child.",
                quotes=[
                    "It does not do to dwell on dreams and forget to live.",
                    "It takes a great deal of bravery to stand up to our enemies, but just as much to stand up to our friends.",
                    "You're a wizard, Harry."
                ],
                trivia=[
                    "12 publishers rejected the manuscript before Bloomsbury accepted it",
                    "The first edition was only 500 copies",
                    "It's been translated into over 80 languages"
                ],
                rating=4.9,
                pages=352,
                isbn="9780439708180"
            ),
            Book(
                id="8",
                title="The Lord of the Rings: The Fellowship of the Ring",
                author="J.R.R. Tolkien",
                genre="High Fantasy",
                year_published=1954,
                description="The first part of an epic quest to destroy a powerful ring and save Middle-earth.",
                funny_story="Tolkien originally started writing what became The Lord of the Rings as a sequel to The Hobbit for children, but it kept getting darker and more complex. His publisher kept asking 'Where are the hobbits?' and 'When do we get to the dragon?' Tolkien had to keep explaining that this was a different kind of story. The publisher was so confused by the manuscript that they almost didn't publish it, thinking it was too weird and long for adults but too dark for children.",
                additional_lore="Tolkien created entire languages for Middle-earth before he wrote the stories. He was a linguistics professor at Oxford and created Elvish languages (Quenya and Sindarin) as a hobby, then needed to create a world where people would speak them. The One Ring's inscription is written in the Black Speech of Mordor, and Tolkien based the sound on what he thought would be the most unpleasant language possible. He drew maps of Middle-earth that were more detailed than many real countries.",
                quotes=[
                    "All we have to decide is what to do with the time that is given us.",
                    "Even the smallest person can change the course of the future.",
                    "I will take the Ring, though I do not know the way."
                ],
                trivia=[
                    "Tolkien invented entire languages before writing the story",
                    "He drew detailed maps and created thousands of years of history",
                    "The books were originally supposed to be published as one volume"
                ],
                rating=4.8,
                pages=479,
                isbn="9780547928210"
            )
        ]
        
        for book in books_data:
            self.books[book.id] = book
    
    def search_books(self, query: str) -> List[Book]:
        """Search for books by title, author, genre, or keywords in description."""
        query = query.lower()
        results = []
        
        for book in self.books.values():
            if (query in book.title.lower() or 
                query in book.author.lower() or 
                query in book.genre.lower() or 
                query in book.description.lower() or
                any(query in quote.lower() for quote in book.quotes)):
                results.append(book)
        
        return results
    
    def get_book_by_id(self, book_id: str) -> Optional[Book]:
        """Get a specific book by its ID."""
        return self.books.get(book_id)
    
    def get_books_by_author(self, author: str) -> List[Book]:
        """Get all books by a specific author."""
        author = author.lower()
        return [book for book in self.books.values() if author in book.author.lower()]
    
    def get_books_by_genre(self, genre: str) -> List[Book]:
        """Get all books in a specific genre."""
        genre = genre.lower()
        return [book for book in self.books.values() if genre in book.genre.lower()]
    
    def get_all_books(self) -> List[Book]:
        """Get all books in the database."""
        return list(self.books.values())
    
    def get_book_statistics(self) -> Dict[str, Any]:
        """Get statistics about the book collection."""
        books = list(self.books.values())
        if not books:
            return {}
        
        return {
            "total_books": len(books),
            "average_rating": sum(book.rating for book in books) / len(books),
            "total_pages": sum(book.pages for book in books),
            "genres": list(set(book.genre for book in books)),
            "publication_years": {
                "earliest": min(book.year_published for book in books),
                "latest": max(book.year_published for book in books)
            }
        }


# Global instance for use by the agent
book_database = BookDatabase()

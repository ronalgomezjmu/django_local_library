from ninja import NinjaAPI, Schema
from ninja.security import APIKeyHeader
from typing import List, Optional
from django.shortcuts import get_object_or_404
from catalog.models import Author, Genre, Language, Book, BookInstance
import uuid

api = NinjaAPI()

# Authentication
class ApiKey(APIKeyHeader):
    param_name = "X-API-Key"
    
    def authenticate(self, request, key):
        if key == "your_secret_key":  # Replace with a more secure key management
            return key
        return None

auth = ApiKey()

# Schemas for request/response bodies
class AuthorIn(Schema):
    first_name: str
    last_name: str
    date_of_birth: Optional[str] = None
    date_of_death: Optional[str] = None

class AuthorOut(Schema):
    id: int
    first_name: str
    last_name: str
    date_of_birth: Optional[str] = None
    date_of_death: Optional[str] = None

class GenreIn(Schema):
    name: str

class GenreOut(Schema):
    id: int
    name: str

class LanguageIn(Schema):
    name: str

class LanguageOut(Schema):
    id: int
    name: str

class BookIn(Schema):
    title: str
    author_id: int
    summary: str
    isbn: str
    genre_ids: List[int]
    language_id: int

class BookOut(Schema):
    id: int
    title: str
    author_id: int
    summary: str
    isbn: str
    genre_ids: List[int]
    language_id: int

class BookInstanceIn(Schema):
    book_id: int
    imprint: str
    due_back: Optional[str] = None
    status: str

class BookInstanceOut(Schema):
    id: str
    book_id: int
    imprint: str
    due_back: Optional[str] = None
    status: str

# Author CRUD endpoints
@api.get("/authors", response=List[AuthorOut], tags=["authors"])
def list_authors(request):
    return Author.objects.all()

@api.get("/authors/{author_id}", response=AuthorOut, tags=["authors"])
def get_author(request, author_id: int):
    return get_object_or_404(Author, id=author_id)

@api.post("/authors", response=AuthorOut, tags=["authors"], auth=auth)
def create_author(request, payload: AuthorIn):
    author = Author.objects.create(**payload.dict())
    return author

@api.put("/authors/{author_id}", response=AuthorOut, tags=["authors"], auth=auth)
def update_author(request, author_id: int, payload: AuthorIn):
    author = get_object_or_404(Author, id=author_id)
    for attr, value in payload.dict().items():
        setattr(author, attr, value)
    author.save()
    return author

@api.delete("/authors/{author_id}", response={"success": bool}, tags=["authors"], auth=auth)
def delete_author(request, author_id: int):
    author = get_object_or_404(Author, id=author_id)
    author.delete()
    return {"success": True}

# Genre CRUD endpoints
@api.get("/genres", response=List[GenreOut], tags=["genres"])
def list_genres(request):
    return Genre.objects.all()

@api.get("/genres/{genre_id}", response=GenreOut, tags=["genres"])
def get_genre(request, genre_id: int):
    return get_object_or_404(Genre, id=genre_id)

@api.post("/genres", response=GenreOut, tags=["genres"], auth=auth)
def create_genre(request, payload: GenreIn):
    genre = Genre.objects.create(**payload.dict())
    return genre

@api.put("/genres/{genre_id}", response=GenreOut, tags=["genres"], auth=auth)
def update_genre(request, genre_id: int, payload: GenreIn):
    genre = get_object_or_404(Genre, id=genre_id)
    for attr, value in payload.dict().items():
        setattr(genre, attr, value)
    genre.save()
    return genre

@api.delete("/genres/{genre_id}", response={"success": bool}, tags=["genres"], auth=auth)
def delete_genre(request, genre_id: int):
    genre = get_object_or_404(Genre, id=genre_id)
    genre.delete()
    return {"success": True}

# Language CRUD endpoints
@api.get("/languages", response=List[LanguageOut], tags=["languages"])
def list_languages(request):
    return Language.objects.all()

@api.get("/languages/{language_id}", response=LanguageOut, tags=["languages"])
def get_language(request, language_id: int):
    return get_object_or_404(Language, id=language_id)

@api.post("/languages", response=LanguageOut, tags=["languages"], auth=auth)
def create_language(request, payload: LanguageIn):
    language = Language.objects.create(**payload.dict())
    return language

@api.put("/languages/{language_id}", response=LanguageOut, tags=["languages"], auth=auth)
def update_language(request, language_id: int, payload: LanguageIn):
    language = get_object_or_404(Language, id=language_id)
    for attr, value in payload.dict().items():
        setattr(language, attr, value)
    language.save()
    return language

@api.delete("/languages/{language_id}", response={"success": bool}, tags=["languages"], auth=auth)
def delete_language(request, language_id: int):
    language = get_object_or_404(Language, id=language_id)
    language.delete()
    return {"success": True}

# Book CRUD endpoints
@api.get("/books", response=List[BookOut], tags=["books"])
def list_books(request):
    books = Book.objects.all()
    result = []
    for book in books:
        result.append({
            "id": book.id,
            "title": book.title,
            "author_id": book.author_id,
            "summary": book.summary,
            "isbn": book.isbn,
            "genre_ids": list(book.genre.values_list('id', flat=True)),
            "language_id": book.language_id
        })
    return result

@api.get("/books/{book_id}", response=BookOut, tags=["books"])
def get_book(request, book_id: int):
    book = get_object_or_404(Book, id=book_id)
    return {
        "id": book.id,
        "title": book.title,
        "author_id": book.author_id,
        "summary": book.summary,
        "isbn": book.isbn,
        "genre_ids": list(book.genre.values_list('id', flat=True)),
        "language_id": book.language_id
    }

@api.post("/books", response=BookOut, tags=["books"], auth=auth)
def create_book(request, payload: BookIn):
    genre_ids = payload.dict().pop("genre_ids")
    book = Book.objects.create(**payload.dict())
    book.genre.set(genre_ids)
    return {
        "id": book.id,
        "title": book.title,
        "author_id": book.author_id,
        "summary": book.summary,
        "isbn": book.isbn,
        "genre_ids": genre_ids,
        "language_id": book.language_id
    }

@api.put("/books/{book_id}", response=BookOut, tags=["books"], auth=auth)
def update_book(request, book_id: int, payload: BookIn):
    book = get_object_or_404(Book, id=book_id)
    data = payload.dict()
    genre_ids = data.pop("genre_ids")
    
    for attr, value in data.items():
        setattr(book, attr, value)
    
    book.save()
    book.genre.set(genre_ids)
    
    return {
        "id": book.id,
        "title": book.title,
        "author_id": book.author_id,
        "summary": book.summary,
        "isbn": book.isbn,
        "genre_ids": genre_ids,
        "language_id": book.language_id
    }

@api.delete("/books/{book_id}", response={"success": bool}, tags=["books"], auth=auth)
def delete_book(request, book_id: int):
    book = get_object_or_404(Book, id=book_id)
    book.delete()
    return {"success": True}

# BookInstance CRUD endpoints
@api.get("/bookinstances", response=List[BookInstanceOut], tags=["bookinstances"])
def list_bookinstances(request):
    bookinstances = BookInstance.objects.all()
    result = []
    for instance in bookinstances:
        result.append({
            "id": str(instance.id),
            "book_id": instance.book_id,
            "imprint": instance.imprint,
            "due_back": instance.due_back.isoformat() if instance.due_back else None,
            "status": instance.status
        })
    return result

@api.get("/bookinstances/{instance_id}", response=BookInstanceOut, tags=["bookinstances"])
def get_bookinstance(request, instance_id: str):
    instance = get_object_or_404(BookInstance, id=instance_id)
    return {
        "id": str(instance.id),
        "book_id": instance.book_id,
        "imprint": instance.imprint,
        "due_back": instance.due_back.isoformat() if instance.due_back else None,
        "status": instance.status
    }

@api.post("/bookinstances", response=BookInstanceOut, tags=["bookinstances"], auth=auth)
def create_bookinstance(request, payload: BookInstanceIn):
    data = payload.dict()
    # Generate a UUID for the new BookInstance
    instance_id = uuid.uuid4()
    
    # Create the BookInstance with the generated ID
    instance = BookInstance.objects.create(
        id=instance_id,
        book_id=data["book_id"],
        imprint=data["imprint"],
        due_back=data["due_back"],
        status=data["status"]
    )
    
    return {
        "id": str(instance.id),
        "book_id": instance.book_id,
        "imprint": instance.imprint,
        "due_back": instance.due_back.isoformat() if instance.due_back else None,
        "status": instance.status
    }

@api.put("/bookinstances/{instance_id}", response=BookInstanceOut, tags=["bookinstances"], auth=auth)
def update_bookinstance(request, instance_id: str, payload: BookInstanceIn):
    instance = get_object_or_404(BookInstance, id=instance_id)
    data = payload.dict()
    
    for attr, value in data.items():
        setattr(instance, attr, value)
    
    instance.save()
    
    return {
        "id": str(instance.id),
        "book_id": instance.book_id,
        "imprint": instance.imprint,
        "due_back": instance.due_back.isoformat() if instance.due_back else None,
        "status": instance.status
    }

@api.delete("/bookinstances/{instance_id}", response={"success": bool}, tags=["bookinstances"], auth=auth)
def delete_bookinstance(request, instance_id: str):
    instance = get_object_or_404(BookInstance, id=instance_id)
    instance.delete()
    return {"success": True}

# Hello world endpoint (keeping from your original code)
@api.get("/hello")
def hello(request):
    return "Hello world"
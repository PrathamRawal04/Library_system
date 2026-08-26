from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from library_engine import Library, Book, Member


app = FastAPI(title="Library Management API")
library = Library()

# pydantic models for input validation

class BookCreate(BaseModel):
    isbn: str
    title: str
    author: str
    total_copies: int = 1


class MemberCreate(BaseModel):
    member_id: str
    name: str


class TransactionRequest(BaseModel):
    member_id: str
    isbn: str

class WaiveFineRequest(BaseModel):
    member_id: str
    amount: float

class BorrowRequest(BaseModel):
    member_id: str
    isbn: str

class ReturnRequest(BaseModel):
    member_id: str
    isbn: str

# API endpoints

@app.get("/books")
def search_book(query: str = ""):
    return library.search_books(query)

@app.post("/books")
def add_book(book: BookCreate):
    if not book.isbn or not book.title or not book.author:
        raise HTTPException(status_code=422, detail="ISBN, Title, and Author are required.")
    if book.total_copies < 1:
        raise HTTPException(status_code=422, detail="Total copies must be at least 1.")
    try:
        if book.isbn in library.books:
            library.books[book.isbn].total_copies += book.total_copies
            library.books[book.isbn].available_copies += book.total_copies
        else:
            new_book = Book(book.isbn, book.title, book.author, book.total_copies)
            library.books[book.isbn] = new_book
        library.save_data()
        return {"message": "Book saved successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save book: {str(e)}")


@app.post("/members")
def Register_member(req: MemberCreate):
    success, message = library.register_member(req.member_id, req.name)
    if not success:
        raise HTTPException(status_code=400, detail=message)
    return {"message": message}


@app.post("/borrow")
def borrow_book(req: BorrowRequest):
    if not req.member_id or not req.isbn:
        raise HTTPException(status_code=422, detail="Member ID and ISBN are required.")
    success, message = library.borrow_books(req.member_id, req.isbn)
    if not success:
        raise HTTPException(status_code=400, detail=message)
    return {"message": message}


@app.post("/waive-fine")
def waive_fine(req: WaiveFineRequest):
    if req.member_id not in library.members_data:
        raise HTTPException(status_code=400, detail="Member not found.")
    if req.amount < 0:
        raise HTTPException(status_code=422, detail="Amount cannot be negative.")
    member = library.members_data[req.member_id]
    waived = min(member.fines, req.amount)
    member.fines -= waived
    library.save_data()
    return {"message": f"Waived ${waived:.2f}. Remaining fine: ${member.fines:.2f}."}


@app.get("/members")
def get_members():
    return [m.to_dict() for m in library.members_data.values()]

@app.post("/return")
def return_book(req: ReturnRequest):
    if not req.member_id or not req.isbn:
        raise HTTPException(status_code=422, detail="Member ID and ISBN are required.")
    success, message = library.return_book(req.member_id, req.isbn)
    if not success:
        raise HTTPException(status_code=400, detail=message)
    return {"message": message}

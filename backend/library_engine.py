import json
import os
from datetime import datetime, timedelta
from collections import deque

DAILY_FINE_RATE = 0.50
BORROW_PERIOD_DAYS = 14

class Book:
    def __init__(self, isbn: str, title: str, author: str, total_copies: int = 1):
        self.isbn = isbn
        self.title = title
        self.author = author
        self.total_copies = total_copies
        self.available_copies = total_copies
        self.waitlist = deque()

    def to_dict(self) -> dict:
        return {"isbn": self.isbn, "title": self.title, "author": self.author, "available_copies": self.available_copies, "waitlist": list(self.waitlist)}

    @classmethod
    def from_dict(cls, data: dict):
        book = cls(
            isbn=data["isbn"],
            title=data["title"],
            author=data["author"],
            total_copies=data["total_copies"]
        )
        book.available_copies = data["available_copies"]
        book.waitlist = deque(data.get("waitlist", []))
        return book


class Member:
    def __init__(self, member_id: str, name: str):
        self.member_id = member_id
        self.name = name
        self.borrow_books = {}
        self.fines = 0.0

    def to_dict(self) -> dict:
        return {
            "member_id": self.member_id,
            "name": self.name,
            "borrow_books": self.borrow_books,
            "fines": self.fines
        }

    @classmethod
    def from_dict(cls, data: dict):
        member = cls(data["member_id"], data["name"])
        member.borrow_books = data.get("borrow_books", {})
        member.fines = float(data.get("fines", 0.0))
        return member


class Library:
    def __init__(self, storage_file: str = None):
        if storage_file is None:
            storage_file = os.getenv("STORAGE_FILE", "library_data.json")
        self.storage_file = storage_file
        self.books = {}
        self.members_data = {}
        self.load_data()

    def borrow_books(self, member_id: str, isbn: str) -> tuple[bool, str]:
        if member_id not in self.members_data or isbn not in self.books:
            return False, "Invalid member ID or ISBN."

        member = self.members_data[member_id]
        book = self.books[isbn]

        if member.fines > 0:
            return False, f"Cannot borrow: Unpaid fines of ${member.fines:.2f}."

        if isbn in member.borrow_books:
            return False, f"Member already has a copy of '{book.title}'."

        # Check waitlist: if member is on it but not first, block them
        if member_id in book.waitlist and book.waitlist[0] != member_id:
            return False, f"'{book.title}' is reserved. Only person #1 on the waitlist can borrow."

        if book.available_copies > 0:
            # Remove member from waitlist if they're first
            if book.waitlist and book.waitlist[0] == member_id:
                book.waitlist.popleft()

            book.available_copies -= 1
            due_date = (datetime.now() + timedelta(days=BORROW_PERIOD_DAYS)).strftime("%Y-%m-%d")
            member.borrow_books[isbn] = due_date
            self.save_data()
            return True, f"Successfully borrowed '{book.title}'. Due date: {due_date}"

        else:
            self.add_to_waitlist(member_id, isbn)
            self.save_data()
            return False, f"No copies available. Added {member.name} to the waitlist."

    def return_book(self, member_id: str, isbn: str) -> tuple[bool, str]:
        if member_id not in self.members_data or isbn not in self.books:
            return False, "Invalid Member ID or ISBN."

        member = self.members_data[member_id]
        book = self.books[isbn]

        if isbn not in member.borrow_books:
            return False, f"Member did not borrow '{book.title}'."

        due_date_str = member.borrow_books.pop(isbn)
        due_date = datetime.strptime(due_date_str, "%Y-%m-%d")
        today = datetime.now()

        msg = f"Returned '{book.title}'."
        if today > due_date:
            days_overdue = (today - due_date).days
            fine = days_overdue * DAILY_FINE_RATE
            member.fines += fine
            msg += f" Overdue by {days_overdue} days. ${fine:.2f} fine added."

        book.available_copies += 1
        self.save_data()
        return True, msg

    def add_to_waitlist(self, member_id: str, isbn: str):
        book = self.books[isbn]
        if member_id not in book.waitlist:
            book.waitlist.append(member_id)

    def search_books(self, query: str) -> list:
        if not query:
            return [b.to_dict() for b in self.books.values()]
        q = query.lower()
        return [b.to_dict() for b in self.books.values()
                if q in b.title.lower() or q in b.author.lower() or q in b.isbn.lower()]

    def save_data(self):
        try:
            os.makedirs(os.path.dirname(self.storage_file), exist_ok=True)
        except Exception:
            pass
        data = {
            "books": [b.to_dict() for b in self.books.values()],
            "members": [m.to_dict() for m in self.members_data.values()]
        }
        with open(self.storage_file, "w") as f:
            json.dump(data, f, indent=4)

    def load_data(self):
        if not os.path.exists(self.storage_file):
            return
        try:
            with open(self.storage_file, "r") as f:
                data = json.load(f)
            self.books = {b["isbn"]: Book.from_dict(b) for b in data.get("books", [])}
            self.members_data = {m["member_id"]: Member.from_dict(m) for m in data.get("members", [])}
        except json.JSONDecodeError:
            print(f"Warning: Corrupted JSON in {self.storage_file}. Starting fresh.")
        except Exception as e:
            print(f"Warning: Failed to load data: {e}")

    def register_member(self, member_id: str, name: str):
        member_id = member_id.strip()

        if member_id in self.members_data:
            return False, "Member already exists."
        self.members_data[member_id] = Member(member_id, name)
        self.save_data()
        return True, "Member registered successfully."

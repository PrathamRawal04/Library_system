# Library Management System

A simple full-stack library management application. It provides a web dashboard built with Streamlit and a REST API powered by FastAPI to handle book inventory, member registrations, checkout transactions, and fine management.

## Features

- Search the catalog by book title, author, or ISBN
- Track inventory, available copies, and member waitlists
- Manage member registration and view borrowing histories
- Handle checkouts, returns, and automatic fine calculations ($0.50/day after 14 days)
- Waive member fines through the API

## Tech Stack

- **Backend:** Python, FastAPI, Uvicorn, Pydantic
- **Frontend:** Streamlit
- **Storage:** JSON (`library_data.json`)
- **Deployment:** Docker support for frontend

## Project Structure

- `library_engine.py` - Core domain models and business logic
- `main.py` - FastAPI application and API routes
- `app.py` - Streamlit UI interface
- `Dockerfile` - Container setup for the Streamlit app
- `requirements.txt` - Project dependencies

## Local Setup

### Prerequisites
- Python 3.10+
- Git

### Installation

1. Clone the repository:
   ```bash
   git clone [https://github.com/YOUR_USERNAME/YOUR_REPO.git](https://github.com/YOUR_USERNAME/YOUR_REPO.git)
   cd YOUR_REPO
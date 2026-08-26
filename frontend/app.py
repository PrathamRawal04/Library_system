import streamlit as st
import requests
import os

API_URL = os.getenv("API_URL", "http://localhost:8000")

st.set_page_config(page_title="library System", layout="wide")
st.title("Library Management System")

# side Navigation
page = st.sidebar.selectbox("Navigate", ["Catalog & Search", "Borrow & Return", "Members & Fines", "Admin - Add Books/Members"])

# --- page1: catalog & search ---
if page == "Catalog & Search":
    st.header("Book Catalog")
    search_query = st.text_input("search by Title, Author, or ISBN")

    try:
        response = requests.get(f"{API_URL}/books", params={"query": search_query})
        if response.status_code == 200:
            books = response.json()
            if books:
                st.table(books)
            else:
                st.info("No books found.")
    except requests.exceptions.RequestException:
        st.error("Could not connect to the backend server.")

# --- page2: Borrow & return ---
elif page == "Borrow & Return":
    st.header("Transaction")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Borrow a Book")
        b_member_id = st.text_input("Member ID", key="b_mid")
        b_isbn = st.text_input("Book ISBN", key="b_isbn")
        if st.button("Borrow"):
            res = requests.post(f"{API_URL}/borrow", json={"member_id": b_member_id, "isbn": b_isbn})
            if res.status_code in (200, 201):
                try:
                    st.success(res.json()["message"])
                except (KeyError, ValueError):
                    st.success("Borrowed successfully!")
            else:
                try:
                    error_msg = res.json().get("detail", "Error processing request.")
                except ValueError:
                    error_msg = res.text if res.text else f"server returned status code {res.status_code}"
                st.error(f"Failed: {error_msg}")

    with col2:
        st.subheader("Return a Book")
        r_member_id = st.text_input("Member ID", key="r_mid")
        r_isbn = st.text_input("Book ISBN", key="r_isbn")
        if st.button("Return"):
            res = requests.post(f"{API_URL}/return", json={"member_id": r_member_id, "isbn": r_isbn})
            if res.status_code == 200:
                try:
                    st.success(res.json()["message"])
                except (KeyError, ValueError):
                    st.success("Book returned successfully!")
            else:
                try:
                    error_msg = res.json().get("detail", "Error processing request.")
                except ValueError:
                    error_msg = f"Server error ({res.status_code})"
                st.error(f"Failed: {error_msg}")

# --- page 3: member & fines ---
elif page == "Members & Fines":
    st.header("Member Directory")
    res = requests.get(f"{API_URL}/members")
    if res.status_code == 200:
        try:
            members = res.json()
        except ValueError:
            st.error("Failed to parse member data.")
            members = []

        if members:
            table_data = []
            for m in members:
                borrowed = ", ".join(m.get("borrow_books", {}).keys()) or "None"
                table_data.append({
                    "Member ID": m.get("member_id"),
                    "Name": m.get("name"),
                    "Borrowed ISBNs": borrowed,
                    "Fines ($)": f"{m.get('fines', 0.0):.2f}"
                })
            st.table(table_data)
        else:
            st.info("No members registered yet.")
    else:
        st.error("Could not fetch members.")

# --- page 4: Admin ---
elif page == "Admin - Add Books/Members":
    st.header("Librarian Admin Panel")

    col1, col2 = st.columns(2)

    with col1: 
        st.subheader("Add / Restock Book")
        isbn = st.text_input("ISBN")
        title = st.text_input("Title")
        author = st.text_input("Author")
        copies = st.number_input("Total Copies", min_value=1, value=1)
        if st.button("Add Book"):
            if not isbn or not title or not author:
                st.warning("Please fill in ISBN, Title, and Author.")
            else:
                payload = {"isbn": isbn, "title": title, "author": author, "total_copies": int(copies)}
                res = requests.post(f"{API_URL}/books", json=payload)
                if res.status_code in (200, 201):
                    st.success("Book added successfully!")
                else:
                    try:
                        error_msg = res.json().get("detail", "Error adding book.")
                    except ValueError:
                        error_msg = f"Server error ({res.status_code})"
                    st.error(f"Failed: {error_msg}")

    with col2:
        st.subheader("Register Member")
        m_id = st.text_input("New Member ID").strip()
        name = st.text_input("Member name").strip()

        if st.button("Register Member"):
            if not m_id or not name:
                st.warning("Please fill in both Member ID and Name.")
            else: 
                payload = {"member_id": m_id, "name": name}
                res = requests.post(f"{API_URL}/members", json=payload)
                if res.status_code in (200, 201):
                    st.success("Member registered successfully.")
                else:
                    try:
                        error_msg = res.json().get("detail", "Error registering member.")
                    except ValueError:
                        error_msg = f"Server error ({res.status_code})"
                    st.error(f"Failed: {error_msg}")

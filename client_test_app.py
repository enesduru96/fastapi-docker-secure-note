import requests
import sys
import time
import json
import os
import re
import traceback

BASE_URL = "http://localhost:8000"
SESSION_FILE = "session.json"

class SessionState:
    access_token = None
    refresh_token = None
    user_email = None

state = SessionState()

def print_header(title):
    print("\n" + "=" * 40)
    print(f" {title}")
    print("=" * 40)

def get_auth_headers():
    if not state.access_token:
        return {}
    return {"Authorization": f"Bearer {state.access_token}"}


def is_valid_email(email):
    pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
    return re.match(pattern, email) is not None

# --------------------------
# SESSION MANAGEMENT
# --------------------------

def save_session():
    data = {
        "access_token": state.access_token,
        "refresh_token": state.refresh_token,
        "user_email": state.user_email
    }
    try:
        with open(SESSION_FILE, "w") as f:
            json.dump(data, f)
            
        print("Debug: Session saved to disk.")
    except Exception as e:
        print(f"Could not save session: {e}")

def load_session():
    if not os.path.exists(SESSION_FILE):
        return

    try:
        with open(SESSION_FILE, "r") as f:
            data = json.load(f)
            
        state.access_token = data.get("access_token")
        state.refresh_token = data.get("refresh_token")
        state.user_email = data.get("user_email")
        print(f"🔄 Session restored for {state.user_email}")
    except Exception as e:
        print(f"Could not load session: {e}")

def logout():
    state.access_token = None
    state.refresh_token = None
    state.user_email = None
    
    if os.path.exists(SESSION_FILE):
        os.remove(SESSION_FILE)
    print("Logged out successfully.")

# --------------------------
# ACTIONS
# --------------------------

def register():
    print_header("REGISTER NEW USER")
    
    while True:
        username = input("Username: ").strip()
        if len(username) > 2:
            break
        print("❌ Username must be at least 3 characters.")

    while True:
        email = input("Email: ").strip()
        if is_valid_email(email):
            break
        print("Invalid email format.")

    password = input("Password: ")
    
    payload = {
        "username": username, # <-- YENİ
        "email": email,
        "password": password,
        "is_active": True,
        "is_admin": False
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/register", json=payload)
        
        if response.status_code == 201:
            print(f"Success! User {email} created.")
        else:
            print(f"Error: {response.json().get('detail')}")
    except Exception as e:
        print(f"Connection Error: {e}")

def login():
    print_header("LOGIN")
    
    while True:
        email = input("Email: ").strip()
        if is_valid_email(email):
            break
        print("Invalid email format. Please try again.")

    password = input("Password: ")
    
    payload = {
        "username": email,
        "password": password
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/token", data=payload)
        
        if response.status_code == 200:
            data = response.json()
            state.access_token = data["access_token"]
            state.refresh_token = data["refresh_token"]
            state.user_email = email
            
            save_session()
            print(f"Login successful! Welcome, {email}.")
        else:
            print(f"Login failed: {response.json().get('detail')}")
    except Exception as e:
        print(f"Connection Error: {e}")


def view_public_feed():
    print_header("PUBLIC NOTES FEED")
    if not state.access_token:
        print("You must login to view the public feed!")
        return

    try:
        response = requests.get(f"{BASE_URL}/notes/public", headers=get_auth_headers())
        
        if response.status_code == 200:
            notes = response.json()
            if not notes:
                print("No public notes available yet.")
                return
                
            print(f"found {len(notes)} public notes:\n")
            
            for note in notes:
                author = note['owner_username']
                print(f"{note['title']} (@{author})")
                print(f"   \"{note['content']}\"")
                print("-" * 30)
                
        elif response.status_code == 401:
             print("Unauthorized. Token might be expired.")
        else:
            print(f"Error: {response.status_code}")

    except Exception as e:
        print(f"Error: {e}")
        print(traceback.format_exc())
    
    input("\nPress Enter to return to Main Menu")
    
def search_notes():
    print_header("SEARCH NOTES")
    if not state.access_token:
        print("You must login first!")
        return

    query = input("Enter search query: ").strip()
    if not query:
        print("Search query cannot be empty.")
        return

    try:
        response = requests.get(
            f"{BASE_URL}/notes/search", 
            params={"q": query}, 
            headers=get_auth_headers()
        )
        
        if response.status_code == 200:
            notes = response.json()
            if not notes:
                print(f"No notes found matching '{query}'.")
            else:
                print(f"Found {len(notes)} matching notes:\n")
                for note in notes:
                    status = "Public" if note["is_public"] else "Private"
                    author = note.get('owner_username', 'Unknown')
                    
                    print(f"{note['title']} (@{author}) [{status}]")
                    print(f"   Content: {note['content']}")
                    print("-" * 30)
        
        elif response.status_code == 401:
             print("Unauthorized. Token might be expired.")
        else:
            print(f"Error: {response.status_code} - {response.text}")

    except Exception as e:
        print(f"Error: {e}")
        
    input("\nPress Enter to return to Main Menu")

    
def view_my_notes():
    print_header("MY NOTES")
    if not state.access_token:
        print("You must login first!")
        return

    try:
        response = requests.get(f"{BASE_URL}/notes/", headers=get_auth_headers())
        
        if response.status_code == 200:
            notes = response.json()
            if not notes:
                print("No notes found.")
            for note in notes:
                status = "Public" if note["is_public"] else "Private"
                print(f"ID: {note['id']} | {note['title']} ({status})")
                print(f"   Content: {note['content']}")
                print("-" * 20)
        elif response.status_code == 401:
             print("Unauthorized. Token might be expired. Try option 5 (Refresh).")
        else:
            print(f"Error: {response.status_code}")

    except Exception as e:
        print(f"Error: {e}")
        
    input("Press Enter to return to Main Menu")

def create_note():
    print_header("CREATE NEW NOTE")
    if not state.access_token:
        print("You must login first!")
        return

    title = input("Title: ")
    content = input("Content: ")
    is_public_in = input("Is Public? (y/n): ").lower()
    is_public = True if is_public_in == 'y' else False

    payload = {
        "title": title,
        "content": content,
        "is_public": is_public
    }

    try:
        response = requests.post(f"{BASE_URL}/notes/", json=payload, headers=get_auth_headers())
        
        if response.status_code == 201:
            print("Note created successfully!")
        else:
            print(f"Error: {response.json().get('detail')}")
            
    except Exception as e:
        print(f"Error: {e}")

def refresh_token():
    print_header("REFRESHING TOKEN")
    if not state.refresh_token:
        print("No refresh token available. Login first.")
        return

    payload = {"refresh_token": state.refresh_token}
    
    try:
        response = requests.post(f"{BASE_URL}/auth/refresh", json=payload)
        
        if response.status_code == 200:
            data = response.json()
            state.access_token = data["access_token"]
            state.refresh_token = data["refresh_token"]
            
            save_session()
            print("Token refreshed successfully! Session extended.")
        else:
            print(f"Failed to refresh: {response.json().get('detail')}")
            logout()
            
    except Exception as e:
        print(f"Error: {e}")

# --------------------------
# MAIN MENU LOOP
# --------------------------
def main():
    load_session() 
    
    while True:
        print("\n" + "*" * 30)
        print(" SECURE NOTE APP CLI ")
        if state.user_email:
            print(f" 👤 User: {state.user_email}")
        else:
            print(" 👤 Guest (Not logged in)")
        print("*" * 30)
        print("1. Register")
        print("2. Login")
        print("3. View My Notes")
        print("4. Search Notes 🔍")
        print("5. Create Note")
        print("6. View Public Feed 🌍")
        print("7. Refresh Token")
        print("8. Logout")
        print("9. Exit")
        
        choice = input("\nChoose an option (1-9): ")
        
        if choice == "1": register()
        elif choice == "2": login()
        elif choice == "3": view_my_notes()
        elif choice == "4": search_notes()
        elif choice == "5": create_note()
        elif choice == "6": view_public_feed()
        elif choice == "7": refresh_token()
        elif choice == "8": logout()
        elif choice == "9": 
            print("Goodbye! 👋")
            sys.exit()
        else:
            print("Invalid choice, try again.")
        
        time.sleep(1)

if __name__ == "__main__":
    try:
        requests.get(BASE_URL)
        main()
    except requests.exceptions.ConnectionError:
        print(f"Error: Could not connect to API at {BASE_URL}")
        print("Make sure Docker is running: 'docker-compose up'")
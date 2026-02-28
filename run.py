"""
run.py - Entry Point (Start the App from Here)

This is the file you run to start the entire application.
It creates the Flask app and launches the development server.

Usage:
    python run.py

Then open http://127.0.0.1:5000 in your browser.
"""

# Import the app factory function that sets up everything
from app.app import create_app

# Create the Flask application (this also connects to the database
# and creates all tables if they don't exist yet)
app = create_app()

# This block only runs when you execute "python run.py" directly
# (not when the file is imported by something else)
if __name__ == "__main__":
    print("=" * 50)
    print("  Resume Parser — http://127.0.0.1:5000")
    print("=" * 50)

    # Start the Flask development server
    # debug=True  → auto-reloads when you change code & shows error details
    # host="0.0.0.0" → accessible from other devices on your network
    # port=5000   → the server runs on http://localhost:5000
    app.run(debug=True, host="0.0.0.0", port=5000)

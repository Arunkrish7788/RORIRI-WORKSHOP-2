#!/usr/bin/env python3
"""
Simple runner script for the AWS Workshop Registration System
"""

import os
import sys

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import and run the Flask app
from app import app, init_db

if __name__ == '__main__':
    # Initialize database
    init_db()
    
    # Run the application
    print("Starting AWS Workshop Registration System...")
    print("Admin Dashboard: http://localhost:5000/admin")
    print("Registration Page: http://localhost:5000/register")
    print("Press Ctrl+C to stop the server")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
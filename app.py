"""
Main entry point for the Musical Loop Generation Application.
Coordinates the core components and initializes the application.
"""

# Import core application class
from src.core.application import Application

def main():
    """Initialize and run the musical loop generation application."""
    # Create application instance
    app = Application()
    
    # Run the application
    app.run()

if __name__ == "__main__":
    main()
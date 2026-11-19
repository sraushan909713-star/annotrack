# WHAT: Starting point of the app.
# WHY:  "flask run" (and Docker later) starts the app from this file.

from app import create_app

app = create_app()

if __name__ == "__main__":
    app.run()
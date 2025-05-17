from app import create_app
import os

app = create_app()

if __name__ == '__main__':
    try:
        print(f"Current working directory: {os.getcwd()}")
        print("Starting Flask server...")
        # Menonaktifkan auto-reloader untuk menghindari error socket di Windows
        app.run(debug=True, use_reloader=False)
    except Exception as e:
        print(f"Error starting server: {str(e)}")
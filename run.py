from app import create_app

# Create Flask application
app = create_app()

if __name__ == "__main__":
    # Run the application
    app.run(debug=True, host='0.0.0.0', port=5000)
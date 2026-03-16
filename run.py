from app import myapp, db

if __name__ == "__main__":
    with myapp.app_context():
        db.create_all()
    myapp.run(debug=True)
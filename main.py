import os
from flask import Flask

from website import app, db
from website.accounts.models import User

import unittest
import getpass
from datetime import datetime
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, ".env"))

if os.environ.get("FLASK_ENV") != "testing":
    with app.app_context():
        try:
            db.create_all()
            if not User.query.filter_by(email="mokshita@vit.ac.in").first():
                print("Demo accounts not found. Auto-seeding initial database...")
                import seed_demo_data
        except Exception as e:
            print(f"Database auto-seed note: {e}")


@app.cli.command("test")
def test():
    tests = unittest.TestLoader().discover("tests")
    with open("log_test.txt", "w") as f:
        runner = unittest.TextTestRunner(stream=f, verbosity=2)
        result = runner.run(tests)
    if result.wasSuccessful():
        return 0
    else:
        return 1


@app.cli.command("create_admin")
def create_admin():
    email = input("Enter email address: ")
    password = getpass.getpass("Enter password: ")
    confirm_password = getpass.getpass("Enter password again: ")
    if password != confirm_password:
        print("Passwords don't match")
    else:
        try:
            user = User(
                email=email,
                password=password,
                is_admin=True,
                is_confirmed=True,
                confirmed_on=datetime.now(),
            )
            db.session.add(user)
            db.session.commit()
            print(f"Admin with email {email} created successfully!")
        except Exception as e:
            print("Couldn't create admin user.")
            print(f"Error: {str(e)}")


if __name__ == "__main__":
    if os.getenv("FLASK_DOCKER") == "True":
        print("DOCKER MODE")
        app.run(host="0.0.0.0", port=5000)
    else:
        print("LOCAL MODE")
        app.run()

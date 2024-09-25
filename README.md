# baboon-web
A webserver written in flask.

Inspired by Miguel Grindbergs Blog: https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-i-hello-world

# Required
- Python >= 3.12.6

# Setup - Windows
Create a venv
```
python -m venv venv
```

Activate venv
```
.\venv\Scripts\activate
```

Install flask and some other stuff...
```
pip install flask

# Remembers environment variables across sessions
pip install python-dotenv

# HTTP client written in Python that makes it easy to send API requests
pip install httpie

# Flask extension used for Forms
pip install flask-wtf

# Flask extension that allow us to handle db entries as objects
pip install flask-sqlalchemy

# Flask extension for db migration
pip install flask-migrate

# init database
flask db init

```

Run the app
```
flask --debug run
```

# Setup - Linux
Basically the same as for Windows

# Testing
Run unit tests (TODO)
```
pytest
```

Test API endpoints manually
```
http GET http://localhost:5000/api/raids
```

# Package

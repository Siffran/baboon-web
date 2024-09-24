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
```

Run the app
```
flask run
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

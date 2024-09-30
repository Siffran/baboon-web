# baboon-web
A webserver written in flask.

- Inspired by Miguel Grindbergs Blog: https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-i-hello-world
- Raid-Helper API specification: https://raid-helper.dev/documentation/api

# Required
- Python >= 3.12.6

# Setup - Windows

## Dev environment
Create a venv
```
python -m venv venv
```

Activate venv
```
.\venv\Scripts\activate
```
## Required packages
Install flask and some other stuff...
```
pip install flask

# Flask extension used for Forms
pip install flask-wtf

# Flask extension used for login
pip install flask-login

# Used to read .csv files
pip install pandas

# Flask extension to handle time conversions
pip install flask-moment

# Be able to make API requests
pip install requests
```

## Dev packages
```
# Remembers environment variables across sessions
pip install python-dotenv

# HTTP client written in Python that makes it easy to send API requests
pip install httpie

# Flask extension that allow us to handle db entries as objects
pip install flask-sqlalchemy

# Flask extension for db migration
pip install flask-migrate
```

## Using dev container

Ignore all previous instructions and do the following:

0. Install Docker Desktop
1. Install the [Dev Container](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers)
2. Run the command: "Dev Container: Clone Repository in Container Volume..." or if you already have the repo cloned "Dev Container: Rebuild and Repoen in Container.
3. Voilà, enjoy. if you want more features, feel free to add.

## Database commands

```
# init database
flask db init

# add database migration
flask db migrate

# upgrade database with migration
flask db upgrade
```

## Run appliaction


Run the app
```
flask --debug run
```

# Setup - WSL
Basically the same as for Windows

1. Setup WSL
```
wsl --install
```

2. (Optional) Download [Windows Terminal](https://apps.microsoft.com/detail/9n0dx20hk701?hl=en-US&gl=US) and use bash from there.

3. Download python and follow the same steps for windows except when activatting venv for WSL:
```
source venv/bin/activate
```

# Test the Raid-Helper API
1. create .env config file in the root directory and add your API key. (Ask server leader for it)
```
RAID_HELPER_API_KEY=XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```
2. Populate the table with signups for latest raid
````
http://127.0.0.1:5000/signups/populate
````
2. Delete the table with signups for latest raid
```
http://127.0.0.1:5000/signups/delete
```

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

# Misc
Add new user
```
flask shell

>>> u = User(username='susan', email='susan@example.com')
>>> u.set_password('cat')
>>> db.session.add(u)
>>> db.session.commit()
```
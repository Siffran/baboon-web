import sqlalchemy as sa
from flask import request, url_for, abort, jsonify
from app import db
import pandas as pd
import os
from app.models import Raid, Player, RaidPlayer
from app.api import bp
# from app.api.auth import token_auth
from app.api.errors import bad_request
from datetime import datetime
import pytz # For timezones

@bp.route('/raids', methods=['POST'])
#@token_auth.login_required
def put_raid():

    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if file and file.filename.endswith('.csv'):
        # Process your CSV file here

        data = pd.read_csv(file)

        # Raid
        discord_id = os.path.splitext(file.filename)[0] # Omit extension
        title = data.iloc[0]['Name']
        description = data.iloc[0]['Description']
        link = data.iloc[0]['Link']
        timestamp = calc_raid_time(data.iloc[0]['Date'], data.iloc[0]['Time'])

        # Check if the Raid exists
        raid = db.session.query(Raid).filter_by(discord_id=discord_id).first()

        if raid:
            # Update the existing Raid
            raid.type = "chill"
            raid.title = title
            raid.description = description
            raid.timestamp = timestamp
            raid.link = link
            print("Raid updated.")
        else:
            # Create a new Raid
            new_raid = Raid(
                discord_id=discord_id,
                type="chill",
                title=title,
                description=description,
                timestamp=timestamp,
                link=link
            )
            db.session.add(new_raid)
            print("New Raid created.")

        # Get all players in the raid, if some players in the raid do not exist in the database, add them
        # Fetch existing players
        # existing_players = db.session.query(Player).filter(Player.discord_id.in_(discord_ids)).all()

        # Create a set of existing discord_ids for quick lookup
        # existing_discord_ids = {player.discord_id for player in existing_players}
        
        # Create a list for new players
        # new_players = []

        """ # Iterate through the provided discord_ids
        for discord_id in discord_ids:
            if discord_id not in existing_discord_ids:
                # If the discord_id is not found, create a new Player instance
                new_players.append(Player(discord_id=discord_id))
        
        # Add new players to the session
        if new_players:
            db.session.add_all(new_players)
        
        # Commit the transaction
        db.session.commit() """

        """# Subset 2: "players"
        players_subset = data.iloc[2:, [0, 3]].reset_index(drop=True)  # Get Names and IDs
        players_subset.columns = ['Name', 'ID']
        print("\nPlayers Subset:")
        print(players_subset)

        # Subset 3: "raidplayers"
        raidplayers_subset = data.iloc[2:, [0, 1, 3, 4]].reset_index(drop=True)  # Get Role, Spec, ID, and Timestamp
        raidplayers_subset.columns = ['Role', 'Spec', 'ID', 'Timestamp']
        print("\nRaid Players Subset:")
        print(raidplayers_subset) """

        # Try to find all player in Player table
        # If no player -> create player
        # Else -> continue

        # Fetch all RaidPlayers
        # update responses / roles / joined_at etc...

        # DONE!

        # Commit the transaction
        db.session.commit()

        return jsonify({'message': 'File uploaded successfully'}), 200
    else:
        return jsonify({'error': 'File type not supported'}), 400

""" @bp.route('/users/<int:id>', methods=['GET'])
@token_auth.login_required
def get_user(id):
    return db.get_or_404(User, id).to_dict()


@bp.route('/users', methods=['GET'])
@token_auth.login_required
def get_users():
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 10, type=int), 100)
    return User.to_collection_dict(sa.select(User), page, per_page,
                                   'api.get_users')


@bp.route('/users/<int:id>/followers', methods=['GET'])
@token_auth.login_required
def get_followers(id):
    user = db.get_or_404(User, id)
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 10, type=int), 100)
    return User.to_collection_dict(user.followers.select(), page, per_page,
                                   'api.get_followers', id=id)


@bp.route('/users/<int:id>/following', methods=['GET'])
@token_auth.login_required
def get_following(id):
    user = db.get_or_404(User, id)
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 10, type=int), 100)
    return User.to_collection_dict(user.following.select(), page, per_page,
                                   'api.get_following', id=id)


@bp.route('/users', methods=['POST'])
def create_user():
    data = request.get_json()
    if 'username' not in data or 'email' not in data or 'password' not in data:
        return bad_request('must include username, email and password fields')
    if db.session.scalar(sa.select(User).where(
            User.username == data['username'])):
        return bad_request('please use a different username')
    if db.session.scalar(sa.select(User).where(
            User.email == data['email'])):
        return bad_request('please use a different email address')
    user = User()
    user.from_dict(data, new_user=True)
    db.session.add(user)
    db.session.commit()
    return user.to_dict(), 201, {'Location': url_for('api.get_user',
                                                     id=user.id)}


@bp.route('/users/<int:id>', methods=['PUT'])
@token_auth.login_required
def update_user(id):
    if token_auth.current_user().id != id:
        abort(403)
    user = db.get_or_404(User, id)
    data = request.get_json()
    if 'username' in data and data['username'] != user.username and \
        db.session.scalar(sa.select(User).where(
            User.username == data['username'])):
        return bad_request('please use a different username')
    if 'email' in data and data['email'] != user.email and \
        db.session.scalar(sa.select(User).where(
            User.email == data['email'])):
        return bad_request('please use a different email address')
    user.from_dict(data, new_user=False)
    db.session.commit()
    return user.to_dict() """

def calc_raid_time(date, time):
    local_timestamp = datetime.strptime(f"{date} {time}", "%d-%m-%Y %H:%M")
    timestamp = pytz.timezone("Europe/Berlin").localize(local_timestamp).astimezone(pytz.utc)

    return timestamp
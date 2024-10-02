from app.forms import LoginForm
import os
from flask_login import current_user, login_user, logout_user, login_required
from urllib.parse import urlsplit
from datetime import datetime, timezone, timedelta
from flask import render_template, flash, redirect, url_for, request, current_app
import sqlalchemy as sa
from app import db
from app.models import User, Player, Raid, RaidPlayer
from app.main import bp
from sqlalchemy import func
import requests

@bp.route('/')
@bp.route('/index')
def index():

    # Fetch upcoming raids based on the current date and time
    raids_upcoming = db.session.scalars(
        sa.select(Raid).where(Raid.timestamp > datetime.now(timezone.utc))
    ).all()

    # Sort players by bp (descending) and joined_at (ascending) for each raid
    for raid in raids_upcoming:
        raid.players.sort(key=lambda raid_player: (-raid_player.player.bp, raid_player.joined_at))

    return render_template("index.html", title='Home Page', raids_upcoming=raids_upcoming, )

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = db.session.scalar(
            sa.select(User).where(User.username == form.username.data))
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('main.login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or urlsplit(next_page).netloc != '':
            next_page = url_for('main.index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)

@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.index'))

@bp.route('/raids')
def raids():
    raids = db.session.scalars(sa.select(Raid)).all()
    return render_template("raids.html", raids=raids)

@bp.route('/players')
def players():
    
    players = db.session.scalars(sa.select(Player).order_by(func.lower(Player.name))).all()
    return render_template("players.html", players=players)

@bp.route('/players/<int:player_id>', methods=['POST'])
def update_player(player_id):
    bp = request.form['bp']
    rank = request.form['rank']
    
    # Here, implement logic to update the player's BP and rank in the database.
    player = Player.query.get(player_id)  # Assuming you're using SQLAlchemy
    if player:
        player.bp = bp
        player.rank = rank
        db.session.commit()
    
    return redirect(url_for('main.players'))  # Redirect to the players page after update

@bp.route('/admin', methods=['GET'])
@login_required
def admin():
    return redirect(url_for('main.index'))

@bp.route('/fetch_raids', methods=['GET'])
def fetch_raids():

    fetch_upcoming_raid_events()
    
    # Fetch upcoming raids from DB
    raids = db.session.scalars(sa.select(Raid).filter(Raid.timestamp >= datetime.now(timezone.utc))).all()

    for raid in raids:

        # Update the bench for raids that are not locked
        update_bench(raid.discord_id)

        # Check if raid is already locked
        if raid.is_locked:
            continue  # Skip this raid since it's locked

        # Check if the raid is within the next 24 hours
        # Remove tz and micorseconds because reasons...
        now = datetime.now(timezone.utc).replace(microsecond=0, tzinfo=None)

        if raid.timestamp <= now + timedelta(hours=24):
            # Lock the raid
            raid.is_locked = True

            # Update player bench points
            for raid_player in raid.players:
                if raid_player.role == 'Baboon_Bench':
                    raid_player.player.bp += 1

            # Commit changes to the database
            db.session.commit()

    return redirect(url_for('main.raids'))

# Extract data from Raid Helper API: https://raid-helper.dev/documentation/api

def fetch_upcoming_raid_events():

    server_id = "955055697144446976"
    api_key = os.getenv('RAID_HELPER_API_KEY')

    url = f"https://raid-helper.dev/api/v3/servers/{server_id}/events"
    headers = {
        'Authorization': f'{api_key}',
        'StartTimeFilter': f'{int(datetime.now(timezone.utc).timestamp())}',
        'IncludeSignUps': 'true'
    }

    try:
        response = requests.get(url, headers=headers)

        response.raise_for_status()

        data = response.json()  # Parse JSON response into a dictionary

        # Populate the database
        for event in data['postedEvents']:

            existing_raid = db.session.query(Raid).filter_by(discord_id=event['id']).first()

            # If the raid is locked, don't update it.
            if existing_raid is not None and existing_raid.is_locked:
                continue

            # Remove all RaidPlayer entries for given Raid
            raid_players = db.session.query(RaidPlayer).filter(RaidPlayer.raid_id == event['id']).all()

            # Delete all matching RaidPlayer objects
            for raid_player in raid_players:
                db.session.delete(raid_player)

            if existing_raid:
                # If a raid with the same discord_id already exists, update its fields
                existing_raid.type = 'mythic' if 'mythic' in event['title'].lower() else 'chill'
                existing_raid.title = event['title']
                existing_raid.description = event['description']
                existing_raid.timestamp = datetime.fromtimestamp(event['startTime'], tz=timezone.utc)
            else:
                # If no such raid exists, create a new one
                raid = Raid(
                    discord_id=event['id'], 
                    type='chill', # Hardcoded for now
                    title=event['title'], 
                    description=event['description'],
                    timestamp=datetime.fromtimestamp(event['startTime'], tz=timezone.utc)
                )
                db.session.add(raid)

            for player in event['signUps']:

                # Add player to db...
                existing_player = db.session.query(Player).filter_by(discord_id=player['userId']).first()

                if existing_player:
                    # If a player with the same discord_id already exists, update its fields
                    existing_player.name = player['name']
                else:
                    # If no such player exists, create a new one
                    new_player = Player(
                        discord_id=player['userId'], 
                        name=player['name']
                    )
                    db.session.add(new_player)

                # Add RaidPlayers to db...
                raid_player = RaidPlayer(
                    raid_id=event['id'],
                    player_id=player['userId'],
                    role=player['className'],
                    joined_at=datetime.fromtimestamp(player['entryTime'], tz=timezone.utc)
                )
                db.session.add(raid_player)

        db.session.commit()

        return None
    except requests.RequestException as e:
        print(f"Error fetching events: {e}")
        return None

def update_bench(raid_id):

    #Fetch raid
    raid = db.session.scalar(sa.select(Raid).filter(Raid.discord_id == raid_id))

    # Split players by roles
    tanks = [p for p in raid.players if p.role == 'Tank']
    healers = [p for p in raid.players if p.role == 'Healer']
    dps = [p for p in raid.players if p.role == 'Melee' or p.role == 'Ranged']

    # Sort each role by core-raider status, bp (descending), and joined_at (ascending)
    if raid.type.lower() == 'mythic':
        tanks.sort(key=lambda p: (-int(p.player.rank == 'core-raider'), -p.player.bp, p.joined_at))
        healers.sort(key=lambda p: (-int(p.player.rank == 'core-raider'), -p.player.bp, p.joined_at))
        dps.sort(key=lambda p: (-int(p.player.rank == 'core-raider'), -p.player.bp, p.joined_at))
    else:
        tanks.sort(key=lambda p: (-p.player.bp, p.joined_at))
        healers.sort(key=lambda p: (-p.player.bp, p.joined_at))
        dps.sort(key=lambda p: (-p.player.bp, p.joined_at))

    # Set max capacities based on event type
    if raid.type.lower() == 'mythic':
        tank_spots, healer_spots, dps_spots = 2, 4, 14
    elif raid.type.lower() == 'chill':
        tank_spots, healer_spots, dps_spots = 2, 6, 22
    else:
        raise ValueError('Unknown event type')

    # Assign players based on role capacities
    assigned_tanks = tanks[:tank_spots]
    assigned_healers = healers[:healer_spots]
    assigned_dps = dps[:dps_spots]

    # Players who are not selected in their primary role
    benched_tanks = tanks[tank_spots:]
    benched_healers = healers[healer_spots:]
    benched_dps = dps[dps_spots:]

    # Calculate available spots from under-filled roles (tanks, healers, dps)
    remaining_tank_spots = max(0, tank_spots - len(assigned_tanks))
    remaining_healer_spots = max(0, healer_spots - len(assigned_healers))
    remaining_dps_spots = max(0, dps_spots - len(assigned_dps))

    # Total available extra spots
    total_extra_spots = remaining_tank_spots + remaining_healer_spots + remaining_dps_spots

    # Create a pool of benched players, sorted by core-raider (if mythic), BP and joined_at
    benched_players = benched_tanks + benched_healers + benched_dps

    if raid.type.lower() == 'mythic':
        benched_players.sort(key=lambda p: (-int(p.player.rank == 'core-raider'), -p.player.bp, p.joined_at))
    else:
        benched_players.sort(key=lambda p: (-p.player.bp, p.joined_at))

    # Pull people from the bench to fill any remaining spots
    if total_extra_spots > 0:
        benched_players = benched_players[total_extra_spots:]  # Remaining players on the bench after extra assignment

    # Update benched players
    for player in benched_players:
        player.role = 'Baboon_Bench'

    db.session.commit()

    return None

# TODO
# update player data (all fields)
# update raid data (all fields)

#################################################
    

# Debug view for adding stuff to the database
@bp.route('/debug')
def debug():
    users = db.session.scalars(sa.select(User)).all()
    players = db.session.scalars(sa.select(Player)).all()
    raids = db.session.scalars(sa.select(Raid)).all()
    raid_players = db.session.scalars(sa.select(RaidPlayer)).all()

    return render_template("debug.html", 
                           users=users,
                           players=players,
                           raids=raids,
                           raid_players=raid_players)

# Route to add a new user
@bp.route('/debug/add_user', methods=['GET', 'POST'])
def add_user():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        # Add the user to the database
        new_user = User(username=username, email=email)
        db.session.add(new_user)
        db.session.commit()
        flash('User added successfully!')
        return redirect(url_for('main.debug'))

# Route to add a new player
@bp.route('/debug/add_player', methods=['GET', 'POST'])
def add_player():
    if request.method == 'POST':
        name = request.form['name']
        bp = request.form['bp']
        rank = request.form['rank']
        # Add the player to the database
        new_player = Player(name=name, bp=bp, rank=rank)
        db.session.add(new_player)
        db.session.commit()
        flash('Player added successfully!')
        return redirect(url_for('main.debug'))
    
# Route to add a new raid
@bp.route('/debug/add_raid', methods=['GET', 'POST'])
def add_raid():
    if request.method == 'POST':
        discord_id = request.form['discord_id']
        type = request.form['type']
        # Add the raid to the database
        new_raid = Raid(discord_id=discord_id, type=type)
        db.session.add(new_raid)
        db.session.commit()
        flash('Raid added successfully!')
        return redirect(url_for('main.debug'))

# Route to add a new raid_player
@bp.route('/debug/add_raid_player', methods=['POST'])
def add_raid_player():
    if request.method == 'POST':
        raid_id = request.form['raid_id']
        player_id = request.form['player_id']
        role = request.form['role']
        
        # Create a new RaidPlayer object
        new_raid_player = RaidPlayer(raid_id=raid_id, player_id=player_id, role=role)
        
        # Add to the session and commit
        db.session.add(new_raid_player)
        db.session.commit()
        
        flash('RaidPlayer added successfully!')
        return redirect(url_for('main.debug'))
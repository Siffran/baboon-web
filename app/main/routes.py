from app.forms import LoginForm
from flask_login import current_user, login_user, logout_user, login_required
from urllib.parse import urlsplit
from datetime import datetime, timezone
from flask import render_template, flash, redirect, url_for, request, current_app
import sqlalchemy as sa
from app import db
from app.models import User, Player, Raid, RaidPlayer
from app.main import bp

@bp.route('/')
@bp.route('/index')
def index():
    raids_upcoming = db.session.scalars(sa.select(Raid)).all() # TODO filter based on upcoming dates...
    # TODO get attending and benched players for each upcoming raid... DOCCOOL ALGORITM :)
    return render_template("index.html", title='Home Page', raids_upcoming=raids_upcoming)

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
    players = db.session.scalars(sa.select(Player)).all()
    return render_template("players.html", players=players)

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

# TODO - Add admin stuff here...
@bp.route('/admin', methods=['GET'])
@login_required
def admin():
    return redirect(url_for('main.index'))

# TODO
# update player data (all fields)
# update raid data (all fields)

#################################################
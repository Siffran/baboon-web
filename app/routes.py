from app import app, db
from app.models import User, Player, Raid, RaidPlayer
from app.forms import LoginForm

from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user, login_user, logout_user, login_required

import sqlalchemy as sa
import sqlalchemy.orm as so
from urllib.parse import urlsplit

@app.route('/')
@app.route('/index')
def index():
    return render_template("index.html", title='Home Page')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = db.session.scalar(
            sa.select(User).where(User.username == form.username.data))
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or urlsplit(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/debug')
def debug():

    users = db.session.scalars(sa.select(User)).all()
    for user in users:
        print(vars(user))

    players = db.session.scalars(sa.select(Player)).all()
    for player in players:
        print(vars(player))

    raids = db.session.scalars(sa.select(Raid)).all()
    for raid in raids:
        print(vars(raid))

    raid_players = db.session.scalars(sa.select(RaidPlayer)).all()
    for raid_player in raid_players:
        print(vars(raid_player))
    
    return render_template('debug.html')


    

# TODO - Add admin stuff here...
@app.route('/admin', methods=['GET'])
@login_required
def admin():
    return redirect(url_for('index'))

# TODO
# update player data (all fields)
# update raid data (all fields)

#################################################

@app.route('/raids/<int:id>', methods=['GET'])
def raid():
    
    active_players, benched_players = get_active_and_benched_players(id)

    return render_template('raid.html', title='Sign In', active_players=active_players, benched_players=benched_players)

def get_active_and_benched_players(raid_id, total_limit=20, tanks_limit=2, healers_limit=4, dps_limit=14):
    # Query all players in the raid
    all_players = RaidPlayer.query.filter_by(raid_id=raid_id).order_by(RaidPlayer.joined_at).all()
    
    # Get the total number of players in the raid
    total_players = len(all_players)
    
    # If the raid has fewer than the max number of players (20), all are active
    if total_players < total_limit:
        return all_players, []  # All are active, no one is benched
    
    # Otherwise, apply role limits
    tanks = [p for p in all_players if p.role == 'tank']
    healers = [p for p in all_players if p.role == 'healer']
    dps = [p for p in all_players if p.role == 'dps']
    
    # Apply role limits and determine active/benched
    active_tanks = tanks[:tanks_limit]
    benched_tanks = tanks[tanks_limit:]
    
    active_healers = healers[:healers_limit]
    benched_healers = healers[healers_limit:]
    
    active_dps = dps[:dps_limit]
    benched_dps = dps[dps_limit:]
    
    # Collect all active and benched players
    active_players = active_tanks + active_healers + active_dps
    benched_players = benched_tanks + benched_healers + benched_dps
    
    return active_players, benched_players
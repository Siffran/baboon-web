from app import app
from app.forms import LoginForm
from flask import render_template, flash, redirect, url_for

@app.route('/')
@app.route('/index')
def index():
    user = {'username': 'Siffran'}
    posts = [
        {
            'author': {'username': 'John'},
            'body': 'Beautiful day in Portland!'
        },
        {
            'author': {'username': 'Susan'},
            'body': 'The Avengers movie was so cool!'
        }
    ]
    return render_template('index.html', title='Home', user=user, posts=posts)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        flash('Login requested for user {}, remember_me={}'.format(
            form.username.data, form.remember_me.data))
        return redirect(url_for('index'))
    return render_template('login.html', title='Sign In', form=form)

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
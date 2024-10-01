import sqlalchemy as sa
import sqlalchemy.orm as so

from typing import Optional
from datetime import datetime, timezone

from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from app import login, db

class User(UserMixin, db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    username: so.Mapped[str] = so.mapped_column(sa.String(64), index=True,
                                                unique=True)
    email: so.Mapped[str] = so.mapped_column(sa.String(120), index=True,
                                             unique=True)
    password_hash: so.Mapped[Optional[str]] = so.mapped_column(sa.String(256))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return '<User {}>'.format(self.username)
    
@login.user_loader
def load_user(id):
    return db.session.get(User, int(id))

# A Player model
class Player(db.Model):
    __tablename__ = 'player'

    discord_id: so.Mapped[int] = so.mapped_column(primary_key=True, index=True,unique=True, nullable=False)
    name: so.Mapped[str] = so.mapped_column(sa.String(64), index=True, unique=True, nullable=False)
    bp: so.Mapped[int] = so.mapped_column(default=0, nullable=False)
    rank: so.Mapped[str] = so.mapped_column(sa.Enum('core-raider', 'raider', 'trial', name='rank_types'), default='raider', nullable=False)

    # Relationship to RaidPlayer (many-to-many through RaidPlayer)
    raids: so.Mapped[list['RaidPlayer']] = so.relationship('RaidPlayer', back_populates='player')

    def __repr__(self):
        return f'<Raider {self.name}>'
    
# Mapping between players and raids, with role and join timestamp
class RaidPlayer(db.Model):
    __tablename__ = 'raid_player'
    
    raid_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey('raid.discord_id'), primary_key=True)
    player_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey('player.discord_id'), primary_key=True)
    
    # Enum for role (tank, healer, dps)
    role: so.Mapped[str] = so.mapped_column(sa.Enum('Tank', 'Healer', 'Ranged', 'Melee', 'Late','Tentative', 'Absence', 'Bench', 'Baboon_Bench', name='role_types'), nullable=False)
    
    # Timestamp when the player joined the raid
    joined_at: so.Mapped[datetime] = so.mapped_column(sa.DateTime, default=datetime.now(timezone.utc), nullable=False)
    
    # Relationship with the Player model
    player: so.Mapped['Player'] = so.relationship('Player', back_populates='raids')

    # Relationship with the Raid model (missing part added)
    raid: so.Mapped['Raid'] = so.relationship('Raid', back_populates='players')
    
    def __repr__(self):
        return f'<Raider {self.player.name} as {self.role}>'


# A Raid model with a relationship to RaidPlayer
class Raid(db.Model):
    __tablename__ = 'raid'

    discord_id: so.Mapped[int] = so.mapped_column(primary_key=True, index=True, unique=True, nullable=False)
    type: so.Mapped[str] = so.mapped_column(sa.Enum('chill', 'mythic', name='raid_types'), nullable=False)
    title: so.Mapped[str] = so.mapped_column(sa.String, unique=False, nullable=False)
    description: so.Mapped[str] = so.mapped_column(sa.String(length=2048), unique=False, nullable=True)
    timestamp: so.Mapped[datetime] = so.mapped_column(sa.DateTime)
    
    # Relationship to RaidPlayer (many-to-many through RaidPlayer)
    players: so.Mapped[list['RaidPlayer']] = so.relationship('RaidPlayer', back_populates='raid')

    def __repr__(self):
        return f'<Raid {self.discord_id}>'

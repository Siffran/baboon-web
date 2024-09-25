from typing import Optional
import sqlalchemy as sa
import sqlalchemy.orm as so
from app import db
from datetime import datetime, timezone

class User(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    username: so.Mapped[str] = so.mapped_column(sa.String(64), index=True,
                                                unique=True)
    email: so.Mapped[str] = so.mapped_column(sa.String(120), index=True,
                                             unique=True)
    password_hash: so.Mapped[Optional[str]] = so.mapped_column(sa.String(256))

    def __repr__(self):
        return '<User {}>'.format(self.username)

# A Player model
class Player(db.Model):
    __tablename__ = 'player'

    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    name: so.Mapped[str] = so.mapped_column(sa.String(64), index=True, unique=True, nullable=False)
    bp: so.Mapped[int] = so.mapped_column(nullable=False)
    trial: so.Mapped[Optional[bool]] = so.mapped_column(sa.Boolean, default=False)
    core: so.Mapped[Optional[bool]] = so.mapped_column(sa.Boolean, default=False)

    # Relationship to RaidPlayer (many-to-many through RaidPlayer)
    raids: so.Mapped[list['RaidPlayer']] = so.relationship('RaidPlayer', back_populates='player')

    def __repr__(self):
        return f'<Raider {self.name}>'
    
# Mapping between players and raids, with role and join timestamp
class RaidPlayer(db.Model):
    __tablename__ = 'raid_player'
    
    raid_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey('raid.id'), primary_key=True)
    player_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey('player.id'), primary_key=True)
    
    # Enum for role (tank, healer, dps)
    role: so.Mapped[str] = so.mapped_column(sa.Enum('tank', 'healer', 'dps', name='role_types'), nullable=False)
    
    # Timestamp when the player joined the raid
    joined_at: so.Mapped[datetime] = so.mapped_column(sa.DateTime, default=datetime.now(timezone.utc), nullable=False)
    
    # Relationship with the Player model
    player: so.Mapped['Player'] = so.relationship('Player')
    
    def __repr__(self):
        return f'<Raider {self.player.name} as {self.role}>'


# A Raid model with a relationship to RaidPlayer
class Raid(db.Model):
    __tablename__ = 'raid'

    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    discord_id: so.Mapped[str] = so.mapped_column(sa.String, nullable=False)
    type: so.Mapped[str] = so.mapped_column(sa.Enum('chill', 'mythic', name='raid_types'), nullable=False)
    
    # Relationship to RaidPlayer (many-to-many through RaidPlayer)
    players: so.Mapped[list['RaidPlayer']] = so.relationship('RaidPlayer', back_populates='raid')

    def __repr__(self):
        return f'<Raid {self.discord_id}>'
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Domain(db.Model):
    __tablename__ = 'domains'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.BigInteger, nullable=False, index=True)  # Telegram user ID
    domain = db.Column(db.String(255), nullable=False)
    status = db.Column(db.Boolean, default=False)  # False = not blocked, True = blocked
    last_checked = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Unique constraint to prevent duplicate domains per user
    __table_args__ = (db.UniqueConstraint('user_id', 'domain', name='unique_user_domain'),)
    
    def __repr__(self):
        return f'<Domain {self.domain} - User {self.user_id}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'domain': self.domain,
            'status': self.status,
            'last_checked': self.last_checked.isoformat() if self.last_checked else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


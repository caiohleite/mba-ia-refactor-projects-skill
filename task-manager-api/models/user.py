from database import db
import hashlib
import hmac
import re

from werkzeug.security import check_password_hash, generate_password_hash

from utils.time import utc_now

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(50), default='user')
    active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=utc_now)

    def set_password(self, pwd):
        self.password = generate_password_hash(pwd)

    def check_password(self, pwd):
        if self.has_legacy_password():
            legacy_hash = hashlib.md5(pwd.encode()).hexdigest()
            return hmac.compare_digest(self.password, legacy_hash)
        return check_password_hash(self.password, pwd)

    def has_legacy_password(self):
        return bool(re.fullmatch(r"[a-f0-9]{32}", self.password or ""))

    def is_admin(self):
        if self.role == 'admin':
            return True
        else:
            return False

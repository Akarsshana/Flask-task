# app/models.py
from . import db
from datetime import datetime
import uuid
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash


def gen_id():
    return str(uuid.uuid4())[:8]


# -----------------------
# Product Model
# -----------------------
class Product(db.Model):
    product_id = db.Column(db.String(32), primary_key=True, default=gen_id)
    name = db.Column(db.String(120), nullable=False, unique=True)
    description = db.Column(db.String(300))

    def __repr__(self):
        return f'<Product {self.name}>'


# -----------------------
# Location Model
# -----------------------
class Location(db.Model):
    location_id = db.Column(db.String(32), primary_key=True, default=gen_id)
    name = db.Column(db.String(120), nullable=False, unique=True)
    description = db.Column(db.String(300))

    def __repr__(self):
        return f'<Location {self.name}>'


# -----------------------
# Product Movement Model
# -----------------------
class ProductMovement(db.Model):
    movement_id = db.Column(db.String(32), primary_key=True, default=gen_id)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    from_location = db.Column(db.String(32), db.ForeignKey('location.location_id'), nullable=True)
    to_location = db.Column(db.String(32), db.ForeignKey('location.location_id'), nullable=True)
    product_id = db.Column(db.String(32), db.ForeignKey('product.product_id'), nullable=False)
    qty = db.Column(db.Integer, nullable=False)

    # Optional: relationship shortcuts
    product = db.relationship('Product', foreign_keys=[product_id])
    from_loc = db.relationship('Location', foreign_keys=[from_location])
    to_loc = db.relationship('Location', foreign_keys=[to_location])

    def __repr__(self):
        return f'<Move {self.product_id} {self.qty} {self.from_location}->{self.to_location}>'


# -----------------------
# User Model (for login)
# -----------------------
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'

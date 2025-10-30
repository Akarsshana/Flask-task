from app import db
from datetime import datetime
import uuid
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash


def gen_id():
    """Generate short UUIDs for locations and movements"""
    return str(uuid.uuid4())[:8]


# -----------------------
# Product Model
# -----------------------
class Product(db.Model):
    __tablename__ = 'product'

    product_id = db.Column(db.String(10), primary_key=True)  # e.g., PI001
    name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.String(255))
    qty = db.Column(db.Integer, default=0)

    def __init__(self, name, description=None, qty=0):
        # Auto-generate product_id like PI001, PI002, etc.
        last_product = Product.query.order_by(Product.product_id.desc()).first()
        if last_product and last_product.product_id.startswith("PI"):
            last_num = int(last_product.product_id.replace("PI", ""))
            new_num = last_num + 1
        else:
            new_num = 1
        self.product_id = f"PI{new_num:03d}"

        self.name = name
        self.description = description
        self.qty = qty

    def __repr__(self):
        return f'<Product {self.product_id} - {self.name}>'


# -----------------------
# Location Model
# -----------------------
class Location(db.Model):
    __tablename__ = 'location'

    location_id = db.Column(db.String(32), primary_key=True, default=gen_id)
    name = db.Column(db.String(120), nullable=False, unique=True)
    description = db.Column(db.String(300))

    def __repr__(self):
        return f'<Location {self.name}>'


# -----------------------
# Product Movement Model
# -----------------------
class ProductMovement(db.Model):
    __tablename__ = 'product_movement'

    movement_id = db.Column(db.String(32), primary_key=True, default=gen_id)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    from_location = db.Column(db.String(32), db.ForeignKey('location.location_id'), nullable=True)
    to_location = db.Column(db.String(32), db.ForeignKey('location.location_id'), nullable=True)
    product_id = db.Column(db.String(10), db.ForeignKey('product.product_id'), nullable=False)
    qty = db.Column(db.Integer, nullable=False)

    product = db.relationship('Product', foreign_keys=[product_id])
    from_loc = db.relationship('Location', foreign_keys=[from_location])
    to_loc = db.relationship('Location', foreign_keys=[to_location])

    def __repr__(self):
        return f'<Move {self.product_id} {self.qty} {self.from_location}->{self.to_location}>'


# -----------------------
# User Model
# -----------------------
class User(UserMixin, db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'

# sample_data.py
from app import create_app, db
from app.models import Product, Location, ProductMovement
from datetime import datetime

app = create_app()

with app.app_context():
    # Reset database
    db.drop_all()
    db.create_all()

    # Create products
    p1 = Product(name='Product A', description='Alpha')
    p2 = Product(name='Product B', description='Beta')
    p3 = Product(name='Product C', description='Gamma')
    p4 = Product(name='Product D', description='Delta')
    db.session.add_all([p1, p2, p3, p4])
    db.session.commit()

    # Create locations
    w1 = Location(name='Main Warehouse', description='Central storage')
    w2 = Location(name='Retail Shop', description='Customer-facing store')
    db.session.add_all([w1, w2])
    db.session.commit()

    # Create simple movements
    m1 = ProductMovement(  # Inbound
        product_id=p1.product_id,
        from_location=None,
        to_location=w1.location_id,
        qty=10
    )
    m2 = ProductMovement(  # Outbound
        product_id=p1.product_id,
        from_location=w1.location_id,
        to_location=None,
        qty=3
    )
    m3 = ProductMovement(  # Inbound different product
        product_id=p2.product_id,
        from_location=None,
        to_location=w2.location_id,
        qty=5
    )

    db.session.add_all([m1, m2, m3])
    db.session.commit()

    print("✅ Simple sample data created successfully.")

from app import create_app, db
from app.models import Product, Location, ProductMovement

app = create_app()

with app.app_context():
    # Reset database
    db.drop_all()
    db.create_all()

    # -------------------
    # PRODUCTS
    # -------------------
    products = [
        ("MacBook Pro 16-inch", "Apple laptop with M3 chip"),
        ("Dell XPS 13", "Ultraportable Windows laptop"),
        ("iPhone 15 Pro", "Apple smartphone with titanium design"),
        ("Samsung Galaxy S24", "Android flagship phone"),
        ("Lenovo ThinkPad X1 Carbon", "Business ultrabook"),
        ("Logitech MX Master 3S", "Wireless ergonomic mouse"),
        ("Apple AirPods Pro 2", "Noise-cancelling earbuds"),
        ("HP Envy Desktop", "Powerful desktop PC for office use"),
        ("Asus ROG Zephyrus G14", "Gaming laptop"),
        ("iPad Air 5th Gen", "Tablet with M1 chip"),
    ]

    product_objs = []
    for name, desc in products:
        p = Product(name=name, description=desc)
        db.session.add(p)
        product_objs.append(p)
    db.session.commit()

    # -------------------
    # LOCATIONS
    # -------------------
    main = Location(name="Main Warehouse", description="Central storage facility")
    store = Location(name="Retail Store", description="Customer-facing retail space")
    repair = Location(name="Repair Center", description="Device repair workshop")

    db.session.add_all([main, store, repair])
    db.session.commit()

    # -------------------
    # MOVEMENTS
    # -------------------
    movements = [
        # Inbound stock into warehouse
        ProductMovement(product_id=product_objs[0].product_id, from_location=None, to_location=main.location_id, qty=20),
        ProductMovement(product_id=product_objs[1].product_id, from_location=None, to_location=main.location_id, qty=15),
        ProductMovement(product_id=product_objs[2].product_id, from_location=None, to_location=main.location_id, qty=30),
        ProductMovement(product_id=product_objs[3].product_id, from_location=None, to_location=main.location_id, qty=25),

        # Transfer from warehouse to store
        ProductMovement(product_id=product_objs[0].product_id, from_location=main.location_id, to_location=store.location_id, qty=5),
        ProductMovement(product_id=product_objs[2].product_id, from_location=main.location_id, to_location=store.location_id, qty=10),
        ProductMovement(product_id=product_objs[3].product_id, from_location=main.location_id, to_location=store.location_id, qty=8),

        # Sale (outbound from store)
        ProductMovement(product_id=product_objs[2].product_id, from_location=store.location_id, to_location=None, qty=3),
        ProductMovement(product_id=product_objs[3].product_id, from_location=store.location_id, to_location=None, qty=2),

        # Move faulty items to repair
        ProductMovement(product_id=product_objs[3].product_id, from_location=store.location_id, to_location=repair.location_id, qty=1),
    ]

    db.session.add_all(movements)
    db.session.commit()

    print("✅ Sample data with stock movements created successfully.")

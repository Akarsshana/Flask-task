# app/routes.py
from flask import Blueprint, render_template, redirect, url_for, request, flash
from .models import Product, Location, ProductMovement, User
from .forms import ProductForm, LocationForm, MovementForm, LoginForm, RegisterForm
from . import db
from flask_login import login_user, logout_user, login_required, current_user

main_bp = Blueprint('main', __name__)

# -------------------------------------------
# Home
# -------------------------------------------
@main_bp.route('/')
def index():
    return render_template('index.html')

# -------------------------------------------
# Products
# -------------------------------------------
@main_bp.route('/products')
@login_required
def product_list():
    products = Product.query.order_by(Product.name).all()
    return render_template('product_list.html', products=products)

@main_bp.route('/products/add', methods=['GET', 'POST'])
@login_required
def product_add():
    form = ProductForm()
    if form.validate_on_submit():
        p = Product(name=form.name.data, description=form.description.data)
        db.session.add(p)
        db.session.commit()
        flash('Product added', 'success')
        return redirect(url_for('main.product_list'))
    return render_template('product_form.html', form=form, action='Add')

@main_bp.route('/products/edit/<string:product_id>', methods=['GET', 'POST'])
@login_required
def product_edit(product_id):
    p = Product.query.get_or_404(product_id)
    form = ProductForm(obj=p)
    if form.validate_on_submit():
        p.name = form.name.data
        p.description = form.description.data
        db.session.commit()
        flash('Product updated', 'success')
        return redirect(url_for('main.product_list'))
    return render_template('product_form.html', form=form, action='Edit')

@main_bp.route('/products/delete/<string:product_id>', methods=['POST'])
@login_required
def product_delete(product_id):
    p = Product.query.get_or_404(product_id)
    move_exists = ProductMovement.query.filter_by(product_id=product_id).first()
    if move_exists:
        flash('Cannot delete product — it has existing movements.', 'danger')
        return redirect(url_for('main.product_list'))

    db.session.delete(p)
    db.session.commit()
    flash('Product deleted successfully.', 'success')
    return redirect(url_for('main.product_list'))

# -------------------------------------------
# Locations
# -------------------------------------------
@main_bp.route('/locations')
@login_required
def location_list():
    locations = Location.query.order_by(Location.name).all()
    return render_template('location_list.html', locations=locations)

@main_bp.route('/locations/add', methods=['GET', 'POST'])
@login_required
def location_add():
    form = LocationForm()
    if form.validate_on_submit():
        l = Location(name=form.name.data, description=form.description.data)
        db.session.add(l)
        db.session.commit()
        flash('Location added', 'success')
        return redirect(url_for('main.location_list'))
    return render_template('location_form.html', form=form, action='Add')

@main_bp.route('/locations/edit/<string:location_id>', methods=['GET', 'POST'])
@login_required
def location_edit(location_id):
    l = Location.query.get_or_404(location_id)
    form = LocationForm(obj=l)
    if form.validate_on_submit():
        l.name = form.name.data
        l.description = form.description.data
        db.session.commit()
        flash('Location updated', 'success')
        return redirect(url_for('main.location_list'))
    return render_template('location_form.html', form=form, action='Edit')

@main_bp.route('/locations/delete/<string:location_id>', methods=['POST'])
@login_required
def location_delete(location_id):
    loc = Location.query.get_or_404(location_id)
    move_exists = ProductMovement.query.filter(
        (ProductMovement.from_location == location_id) |
        (ProductMovement.to_location == location_id)
    ).first()
    if move_exists:
        flash('Cannot delete location — it has related product movements.', 'danger')
        return redirect(url_for('main.location_list'))

    db.session.delete(loc)
    db.session.commit()
    flash('Location deleted successfully.', 'success')
    return redirect(url_for('main.location_list'))

# -------------------------------------------
# Movements
# -------------------------------------------
@main_bp.route('/movements')
@login_required
def movement_list():
    moves = ProductMovement.query.order_by(ProductMovement.timestamp.desc()).all()
    return render_template('movement_list.html', moves=moves)

@main_bp.route('/movements/add', methods=['GET', 'POST'])
@login_required
def movement_add():
    form = MovementForm()
    products = Product.query.order_by(Product.name).all()
    locations = Location.query.order_by(Location.name).all()

    if not products:
        flash('Please add at least one product before recording movements.', 'warning')
        return redirect(url_for('main.product_add'))

    form.product_id.choices = [(p.product_id, p.name) for p in products]
    loc_choices = [('', '--- None ---')] + [(l.location_id, l.name) for l in locations]
    form.from_location.choices = loc_choices
    form.to_location.choices = loc_choices

    if form.validate_on_submit():
        from_loc = form.from_location.data or None
        to_loc = form.to_location.data or None
        if from_loc is None and to_loc is None:
            flash('Either from or to location must be provided', 'danger')
            return render_template('movement_form.html', form=form, action='Add')

        move = ProductMovement(
            from_location=from_loc,
            to_location=to_loc,
            product_id=form.product_id.data,
            qty=form.qty.data
        )
        db.session.add(move)
        db.session.commit()
        flash('Movement recorded', 'success')
        return redirect(url_for('main.movement_list'))

    return render_template('movement_form.html', form=form, action='Add')

@main_bp.route('/movements/delete/<string:movement_id>', methods=['POST'])
@login_required
def movement_delete(movement_id):
    m = ProductMovement.query.get_or_404(movement_id)
    db.session.delete(m)
    db.session.commit()
    flash('Movement deleted successfully.', 'success')
    return redirect(url_for('main.movement_list'))

# -------------------------------------------
# Balance
# -------------------------------------------
@main_bp.route('/balance')
@login_required
def balance():
    balances = {}
    moves = ProductMovement.query.all()
    for m in moves:
        if m.to_location:
            key = (m.product_id, m.to_location)
            balances[key] = balances.get(key, 0) + (m.qty or 0)
        if m.from_location:
            key = (m.product_id, m.from_location)
            balances[key] = balances.get(key, 0) - (m.qty or 0)

    products = {p.product_id: p.name for p in Product.query.all()}
    locations = {l.location_id: l.name for l in Location.query.all()}

    rows = []
    for (prod_id, loc_id), qty in balances.items():
        if qty != 0:
            rows.append({
                'product': products.get(prod_id, prod_id),
                'location': locations.get(loc_id, loc_id),
                'qty': int(qty)
            })

    rows.sort(key=lambda r: (r['product'], r['location']))
    return render_template('balance.html', rows=rows)

# -------------------------------------------
# Authentication (Login / Register / Logout)
# -------------------------------------------
@main_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            flash('Logged in successfully!', 'success')
            return redirect(url_for('main.index'))
        flash('Invalid username or password', 'danger')
    return render_template('login.html', form=form)

@main_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.login'))

@main_bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        existing = User.query.filter_by(username=form.username.data).first()
        if existing:
            flash('Username already taken', 'warning')
        else:
            user = User(username=form.username.data)
            user.set_password(form.password.data)
            db.session.add(user)
            db.session.commit()
            flash('User registered! Please log in.', 'success')
            return redirect(url_for('main.login'))
    return render_template('register.html', form=form)

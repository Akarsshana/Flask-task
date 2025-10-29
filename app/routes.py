from flask import Blueprint, render_template, redirect, url_for, request, flash
from .models import Product, Location, ProductMovement, User
from .forms import ProductForm, LocationForm, MovementForm, LoginForm, RegisterForm
from . import db
from flask_login import login_user, logout_user, login_required, current_user

main_bp = Blueprint('main', __name__)

# ========== HOME ==========
@main_bp.route('/')
def index():
    return render_template('index.html')

# ========== PRODUCTS ==========
@main_bp.route('/products')
@login_required
def product_list():
    products = Product.query.order_by(Product.name).all()
    return render_template('products/list.html', items=products, type='product')

@main_bp.route('/products/add', methods=['GET', 'POST'])
@login_required
def product_add():
    form = ProductForm()
    if form.validate_on_submit():
        db.session.add(Product(name=form.name.data, description=form.description.data))
        db.session.commit()
        flash('Product added', 'success')
        return redirect(url_for('main.product_list'))
    return render_template('products/form.html', form=form, action='Add')

@main_bp.route('/products/edit/<string:product_id>', methods=['GET', 'POST'])
@login_required
def product_edit(product_id):
    p = Product.query.get_or_404(product_id)
    form = ProductForm(obj=p)
    if form.validate_on_submit():
        p.name, p.description = form.name.data, form.description.data
        db.session.commit()
        flash('Product updated', 'success')
        return redirect(url_for('main.product_list'))
    return render_template('products/form.html', form=form, action='Edit')

@main_bp.route('/products/delete/<string:product_id>', methods=['POST'])
@login_required
def product_delete(product_id):
    p = Product.query.get_or_404(product_id)
    if ProductMovement.query.filter_by(product_id=product_id).first():
        flash('Cannot delete — product has movements', 'danger')
    else:
        db.session.delete(p)
        db.session.commit()
        flash('Product deleted', 'success')
    return redirect(url_for('main.product_list'))

# ========== LOCATIONS ==========
@main_bp.route('/locations')
@login_required
def location_list():
    locations = Location.query.order_by(Location.name).all()
    return render_template('locations/list.html', items=locations, type='location')

@main_bp.route('/locations/add', methods=['GET', 'POST'])
@login_required
def location_add():
    form = LocationForm()
    if form.validate_on_submit():
        db.session.add(Location(name=form.name.data, description=form.description.data))
        db.session.commit()
        flash('Location added', 'success')
        return redirect(url_for('main.location_list'))
    return render_template('locations/form.html', form=form, action='Add')

@main_bp.route('/locations/edit/<string:location_id>', methods=['GET', 'POST'])
@login_required
def location_edit(location_id):
    l = Location.query.get_or_404(location_id)
    form = LocationForm(obj=l)
    if form.validate_on_submit():
        l.name, l.description = form.name.data, form.description.data
        db.session.commit()
        flash('Location updated', 'success')
        return redirect(url_for('main.location_list'))
    return render_template('locations/form.html', form=form, action='Edit')

@main_bp.route('/locations/delete/<string:location_id>', methods=['POST'])
@login_required
def location_delete(location_id):
    loc = Location.query.get_or_404(location_id)
    if ProductMovement.query.filter((ProductMovement.from_location == location_id) | (ProductMovement.to_location == location_id)).first():
        flash('Cannot delete — location has movements', 'danger')
    else:
        db.session.delete(loc)
        db.session.commit()
        flash('Location deleted', 'success')
    return redirect(url_for('main.location_list'))

# ========== MOVEMENTS ==========
@main_bp.route('/movements')
@login_required
def movement_list():
    moves = ProductMovement.query.order_by(ProductMovement.timestamp.desc()).all()
    return render_template('movements/list.html', moves=moves)

@main_bp.route('/movements/add', methods=['GET', 'POST'])
@login_required
def movement_add():
    form = MovementForm()
    products = Product.query.order_by(Product.name).all()
    if not products:
        flash('Add a product first', 'warning')
        return redirect(url_for('main.product_add'))
    
    locations = Location.query.order_by(Location.name).all()
    form.product_id.choices = [(p.product_id, p.name) for p in products]
    form.from_location.choices = form.to_location.choices = [('', '---')] + [(l.location_id, l.name) for l in locations]

    if form.validate_on_submit():
        from_loc = form.from_location.data or None
        to_loc = form.to_location.data or None
        if not from_loc and not to_loc:
            flash('Provide from or to location', 'danger')
        else:
            db.session.add(ProductMovement(from_location=from_loc, to_location=to_loc, product_id=form.product_id.data, qty=form.qty.data))
            db.session.commit()
            flash('Movement recorded', 'success')
            return redirect(url_for('main.movement_list'))
    return render_template('movements/form.html', form=form, action='Add')

@main_bp.route('/movements/delete/<string:movement_id>', methods=['POST'])
@login_required
def movement_delete(movement_id):
    db.session.delete(ProductMovement.query.get_or_404(movement_id))
    db.session.commit()
    flash('Movement deleted', 'success')
    return redirect(url_for('main.movement_list'))

# ========== BALANCE ==========
@main_bp.route('/balance')
@login_required
def balance():
    balances = {}
    for m in ProductMovement.query.all():
        if m.to_location:
            balances[(m.product_id, m.to_location)] = balances.get((m.product_id, m.to_location), 0) + m.qty
        if m.from_location:
            balances[(m.product_id, m.from_location)] = balances.get((m.product_id, m.from_location), 0) - m.qty

    products = {p.product_id: p.name for p in Product.query.all()}
    locations = {l.location_id: l.name for l in Location.query.all()}
    rows = [{'product': products.get(pid), 'location': locations.get(lid), 'qty': int(qty)} 
            for (pid, lid), qty in balances.items() if qty != 0]
    rows.sort(key=lambda r: (r['product'], r['location']))
    return render_template('movements/balance.html', rows=rows)

# ========== AUTH ==========
@main_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            flash('Logged in!', 'success')
            return redirect(url_for('main.index'))
        flash('Invalid credentials', 'danger')
    return render_template('auth/login.html', form=form)

@main_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out', 'info')
    return redirect(url_for('main.login'))

@main_bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if User.query.filter_by(username=form.username.data).first():
            flash('Username taken', 'warning')
        else:
            user = User(username=form.username.data)
            user.set_password(form.password.data)
            db.session.add(user)
            db.session.commit()
            flash('Registered! Please log in', 'success')
            return redirect(url_for('main.login'))
    return render_template('auth/register.html', form=form)
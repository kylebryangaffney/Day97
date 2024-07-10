from datetime import date
from flask import Flask, abort, render_template, redirect, url_for, flash, request
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, login_required, current_user, logout_user, UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from models import db, User, Item
from forms import RegisterForm, LoginForm, ItemForm, AddMoneyForm
from flask_ckeditor import CKEditor


app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///market.db"

db.init_app(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
Bootstrap5(app)
ckeditor = CKEditor(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def admin_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.id != 1:
            return abort(403)
        return f(*args, **kwargs)
    return decorated_function

def get_current_date():
    return date.today().strftime("%Y")

@app.route('/')
@app.route('/home')
def home():
    all_items = Item.query.filter(Item.owner == None).order_by(Item.id).all()
    return render_template("index.html", items=all_items, current_user=current_user, current_date=get_current_date())

@app.route('/login', methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('market'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user)
            flash("Logged in successfully!", "success")
            return redirect(url_for('market'))
        else:
            flash("Login Unsuccessful. Please check email and password", "danger")
    return render_template("login.html", form=form, current_user=current_user, current_date=get_current_date())

@app.route('/register', methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('market'))
    
    form = RegisterForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data)
        user = User(email=form.email.data, name=form.name.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash("Registered successfully!", "success")
        return redirect(url_for('login'))
    return render_template("register.html", form=form, current_user=current_user, current_date=get_current_date())

@app.route('/market')
@login_required
def market():
    all_items = Item.query.filter(Item.owner == None).order_by(Item.id).all()
    return render_template("market.html", items=all_items, current_user=current_user, current_date=get_current_date())

@app.route('/add_money', methods=["GET", "POST"])
@login_required
def add_money():
    form = AddMoneyForm()
    if form.validate_on_submit():
        current_user.balance += form.amount.data
        db.session.commit()
        flash("Money added successfully!", "success")
        return redirect(url_for('market'))
    return render_template("add_money.html", form=form, current_user=current_user, current_date=get_current_date())

@app.route('/item/<int:item_id>', methods=["GET", "POST"])
@login_required
def item_detail(item_id):
    item = Item.query.get_or_404(item_id)
    form = ItemForm(obj=item)
    if form.validate_on_submit():
        item.name = form.name.data
        item.price = form.price.data
        item.barcode = form.barcode.data
        item.description = form.description.data
        db.session.commit()
        flash("Item updated successfully!", "success")
        return redirect(url_for('market'))
    return render_template("item_detail.html", item=item, form=form, current_user=current_user, current_date=get_current_date())

@app.route('/sell_item/<int:item_id>', methods=["POST"])
@login_required
def sell_item(item_id):
    item = Item.query.get_or_404(item_id)
    if item.owner != current_user:
        flash("You can only sell items you own.", "danger")
        return redirect(url_for('inventory'))

    current_user.balance += item.price
    item.owner = None
    db.session.commit()
    flash("Item sold successfully!", "success")
    return redirect(url_for('inventory'))


@app.route('/inventory')
@login_required
def inventory():
    user_items = current_user.items
    return render_template('inventory.html', items=user_items, current_user=current_user, current_date=get_current_date())

@app.route('/add_item', methods=["GET", "POST"])
@login_required
@admin_only
def add_item():
    form = ItemForm()
    if form.validate_on_submit():
        new_item = Item(
            name=form.name.data,
            price=form.price.data,
            barcode=form.barcode.data,
            description=form.description.data
        )
        db.session.add(new_item)
        db.session.commit()
        flash("Item added successfully!", "success")
        return redirect(url_for('market'))
    return render_template("add_item.html", form=form, current_user=current_user, current_date=get_current_date())

@app.route('/delete_item/<int:item_id>', methods=["POST"])
@login_required
def delete_item(item_id):
    item = Item.query.get_or_404(item_id)
    db.session.delete(item)
    db.session.commit()
    flash("Item deleted successfully!", "success")
    return redirect(url_for('market'))

@app.route('/add_to_account/<int:item_id>', methods=["POST"])
@login_required
def add_to_account(item_id):
    item = Item.query.get_or_404(item_id)
    if item.owner is not None:
        flash("Item already in another user's account.", "danger")
        return redirect(url_for('market'))
    
    if current_user.balance < item.price:
        flash("Insufficient balance to purchase this item.", "danger")
        return redirect(url_for('market'))
    
    current_user.balance -= item.price
    item.owner = current_user
    db.session.commit()
    flash("Item added to your account and balance updated!", "success")
    return redirect(url_for('market'))

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("You have been logged out!", "info")
    return redirect(url_for('login'))

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
